import re
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Phone number validator
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
)

# ZIP/Postal code validator
def validate_zip_code(value):
    # Basic pattern that works for most countries
    if not re.match(r'^[A-Z0-9]{3,10}(-[A-Z0-9]{4})?$', value, re.I):
        raise ValidationError(
            _('Invalid postal code format.')
        )

# Name validator
def validate_name(value):
    if re.search(r'[0-9!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(
            _('Name cannot contain numbers or special characters.')
        )

# Country validator
def validate_country(value):
    # Add your list of valid countries or use django-countries
    valid_countries = ['US', 'FR', 'GB']  # Example list
    if value not in valid_countries:
        raise ValidationError(
            _('Invalid country code.')
        )

# Updated models with validations
# src/users/models.py
from django.core.validators import EmailValidator, MinLengthValidator
from .validators import (
    phone_regex, validate_zip_code, validate_name, validate_country
)

class Address(models.Model):
    country = models.CharField(
        _('country'), 
        max_length=100,
        validators=[validate_country]
    )
    state = models.CharField(
        _('state/province'), 
        max_length=100,
        validators=[MinLengthValidator(2)]
    )
    city = models.CharField(
        _('city'), 
        max_length=100,
        validators=[MinLengthValidator(2)]
    )
    address_line1 = models.CharField(
        _('address line 1'), 
        max_length=100,
        validators=[MinLengthValidator(5)]
    )
    address_line2 = models.CharField(
        _('address line 2'), 
        max_length=100, 
        blank=True
    )
    zip_code = models.CharField(
        _('ZIP/Postal code'), 
        max_length=20,
        validators=[validate_zip_code]
    )

    def clean(self):
        # Custom model validation
        if self.address_line2 and self.address_line2 == self.address_line1:
            raise ValidationError({
                'address_line2': _('Address line 2 cannot be the same as Address line 1')
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other'))
    ]

    email = models.EmailField(
        _('email address'), 
        unique=True,
        validators=[EmailValidator()]
    )
    first_name = models.CharField(
        _('first name'), 
        max_length=50,
        validators=[validate_name, MinLengthValidator(2)]
    )
    last_name = models.CharField(
        _('last name'), 
        max_length=50,
        validators=[validate_name, MinLengthValidator(2)]
    )
    phone_number = models.CharField(
        _('phone number'), 
        max_length=20,
        validators=[phone_regex],
        blank=True, 
        null=True
    )
    sex = models.CharField(
        _('sex'), 
        max_length=1, 
        choices=GENDER_CHOICES,
        null=True
    )
    address = models.OneToOneField(
        Address, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    # ... rest of the model remains the same ...

    def clean(self):
        super().clean()
        # Custom validation for the user model
        if self.phone_number and not self.phone_number.startswith('+'):
            raise ValidationError({
                'phone_number': _('Phone number must start with "+"')
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

# src/users/serializers.py
from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import CustomUser, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

    def validate_zip_code(self, value):
        # Additional serializer-level validation
        if value.isalpha():
            raise serializers.ValidationError(
                _('ZIP code cannot contain only letters.')
            )
        return value

class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone_number', 'sex', 'address', 'preferred_language'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        # Cross-field validation
        if data.get('first_name') == data.get('last_name'):
            raise serializers.ValidationError(
                _('First name and last name cannot be the same.')
            )
        return data

    def validate_phone_number(self, value):
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                _('Phone number must start with "+"')
            )
        return value