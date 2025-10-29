.PHONY: help migrate test populate shell up down logs clean

help:
	@echo "Available commands:"
	@echo "  make migrate    - Run database migrations"
	@echo "  make test       - Run all tests"
	@echo "  make populate   - Populate database with 50 rides and 50 events"
	@echo "  make shell      - Open Django shell"
	@echo "  make up         - Start Docker containers"
	@echo "  make down       - Stop Docker containers"
	@echo "  make logs       - View Docker logs"
	@echo "  make clean      - Remove all rides and events from database"

migrate:
	docker compose exec rides-api python manage.py migrate

test:
	docker compose exec rides-api python manage.py test rides

populate:
	docker compose exec rides-api python manage.py populate_data

shell:
	docker compose exec rides-api python manage.py shell

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f rides-api

clean:
	docker compose exec rides-api python manage.py shell -c "from rides.models import Ride, RideEvent; RideEvent.objects.all_unfiltered().delete(); Ride.objects.all().delete(); print('Deleted all rides and events')"
