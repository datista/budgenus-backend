from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import Address
from tenants.models import Tenant, Domain

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add extra responses here
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    tenant_name = serializers.CharField(required=False)  # Optional tenant name

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'tenant_name')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        print("[DEBUG] RegisterSerializer.create() started")
        try:
            # Remove tenant_name and password2 from validated data
            tenant_name = validated_data.pop('tenant_name', None)
            validated_data.pop('password2', None)
            
            print(f"[DEBUG] Creating user with data: {validated_data}")
            # Create the user instance but don't save yet
            user = User(**validated_data)
            user.set_password(validated_data['password'])
            
            print(f"[DEBUG] Creating tenant with name: {tenant_name}")
            return user.create_with_tenant(tenant_name=tenant_name)
        except Exception as e:
            print(f"[DEBUG] Error in RegisterSerializer.create(): {str(e)}")
            raise Exception(f"Failed to create user: {str(e)}")

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['country', 'state', 'city', 'address_line1', 
                 'address_line2', 'zip_code']

class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'id',           # API references
            'email',        # Primary identifier
            'first_name',   # Basic profile
            'last_name',    # Basic profile
            'phone_number', # Contact
            'gender',       # Basic profile
            'address',      # Contact
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'phone_number': {'required': False},
            'address': {'required': False},
            'gender': {
                'required': False,
                'choices': User.GENDER_CHOICES
            },

        }

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        user = User.objects.create_user(**validated_data)
        
        if address_data:
            address = Address.objects.create(**address_data)
            user.address = address
            user.save()
            
        return user

class UserDetailSerializer(UserSerializer):
    """Serializer for detailed user information"""
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['date_joined', 'last_login']
