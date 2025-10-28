# Rides API

A Django REST Framework API project for collaboration and peer review.

## Tech Stack

- **Python 3.10**
- **Django 5.2.7**
- **Django REST Framework 3.16.1**
- **PostgreSQL 15**
- **Docker & Docker Compose**

### Key Dependencies

- `python-decouple` - Environment variable management
- `django-debug-toolbar` - SQL query inspection and debugging
- `psycopg2-binary` - PostgreSQL adapter

## Prerequisites

- Docker
- Docker Compose

## Project Structure

```
rides-api/
├── config/                 # Django project configuration
│   ├── settings.py        # Project settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI application
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment variables template
├── docker-compose.yml     # Docker services configuration
├── Dockerfile             # Docker image configuration
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rides-api
```

### 2. Environment Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Update the `.env` file with your configuration (or use the defaults for development).

### 3. Build and Run with Docker

```bash
# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up -d --build
```

The application will be available at:
- **API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Debug Toolbar**: Available on any page when DEBUG=True

### 4. Create a Superuser (Optional)

```bash
docker compose exec rides-api python manage.py createsuperuser
```

## Development Workflow

### Running the Project

```bash
# Start services
docker compose up

# Stop services
docker compose down

# View logs
docker compose logs -f rides-api

# Rebuild after dependency changes
docker compose up --build
```

### Database Migrations

```bash
# Create migrations
docker compose exec rides-api python manage.py makemigrations

# Apply migrations
docker compose exec rides-api python manage.py migrate

# Migrations run automatically on container startup
```

### Django Shell

```bash
docker compose exec rides-api python manage.py shell
```

### Running Tests

```bash
docker compose exec rides-api python manage.py test
```

## Services

### Rides API Service
- **Port**: 8000
- **Command**: `python manage.py runserver 0.0.0.0:8000`
- **Features**: Auto-reload on code changes

### Database Service
- **Database**: PostgreSQL 15
- **Port**: 5432 (exposed for local access)
- **Volume**: `postgres_data` (persistent storage)

## Environment Variables

Key environment variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DB_NAME` | Database name | `db` |
| `DB_USER` | Database user | `superuser` |
| `DB_PASSWORD` | Database password | `superpass` |
| `DB_HOST` | Database host | `db` |
| `DB_PORT` | Database port | `5432` |

## Django Debug Toolbar

The project includes Django Debug Toolbar for development. Access it by:

1. Visit any page in your browser (e.g., http://localhost:8000/admin/)
2. Look for the debug toolbar on the right side
3. Click the **SQL** panel to inspect database queries

The toolbar is only available when `DEBUG=True`.

## API Endpoints

Coming soon - API documentation will be added as endpoints are developed.

## Notes

- This is a **development setup** using Django's built-in server
- Auto-reload is enabled for code changes
- Database data persists in Docker volumes
- `.env` file is not committed to version control
