# Django commands
docker-compose -f docker/docker-compose.yml run web python src/manage.py makemigrations
docker-compose -f docker/docker-compose.yml run web python src/manage.py migrate
docker-compose -f docker/docker-compose.yml run web python src/manage.py createsuperuser

# Translations
docker-compose -f docker/docker-compose.yml run web python src/manage.py makemessages -l fr
docker-compose -f docker/docker-compose.yml run web python src/manage.py compilemessages

# Shell
docker-compose -f docker/docker-compose.yml run web python src/manage.py shell