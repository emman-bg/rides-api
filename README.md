# Rides API

A Django REST Framework API for managing ride-sharing operations, including users, rides, and ride events with real-time tracking and distance-based sorting.

## Tech Stack

- **Python 3.10**
- **Django 5.2.7**
- **Django REST Framework 3.16.1**
- **PostgreSQL 15**
- **Docker & Docker Compose**

### Key Dependencies

- `python-decouple` - Environment variable management
- `django-debug-toolbar` - SQL query inspection and debugging
- `django-filter` - Advanced filtering for API endpoints
- `psycopg2-binary` - PostgreSQL adapter

## Features

- **Token Authentication** - Secure API access with token-based auth
- **Role-Based Access Control** - Admin-only access to all endpoints
- **Advanced Filtering** - Filter rides by status and rider email
- **Distance-Based Sorting** - Sort rides by distance to pickup location using Haversine formula
- **Optimized Queries** - Uses `select_related` and `prefetch_related` for efficient database access
- **Cached Pagination** - LimitOffset pagination with 5-minute cached counts
- **Automated Testing** - 80 comprehensive tests with GitHub Actions CI/CD
- **Management Commands** - Quick data population for testing

## Prerequisites

- Docker
- Docker Compose

## Project Structure

```
rides-api/
├── .github/
│   └── workflows/
│       └── tests.yml             # GitHub Actions CI/CD pipeline
├── config/                       # Django project configuration
│   ├── settings.py               # Project settings
│   ├── urls.py                   # URL routing
│   └── wsgi.py                   # WSGI application
├── rides/                        # Main application
│   ├── management/
│   │   └── commands/
│   │       └── populate_data.py  # Data population command
│   ├── tests/                    # Test suite
│   │   ├── test_models.py        # Model tests (32 tests)
│   │   ├── test_serializers.py   # Serializer tests (19 tests)
│   │   └── test_views.py         # View tests (29 tests)
│   ├── models.py                 # User, Ride, RideEvent models
│   ├── serializers.py            # DRF serializers
│   ├── views.py                  # ViewSets with CRUD operations
│   ├── auth_views.py             # Custom login endpoint
│   ├── permissions.py            # Custom permission classes
│   ├── pagination.py             # Cached pagination
│   └── urls.py                   # App URL routing
├── .env                          # Environment variables (not in git)
├── .env.example                  # Environment variables template
├── docker-compose.yml            # Docker services configuration
├── Dockerfile                    # Docker image configuration
├── Makefile                      # Convenient commands
├── manage.py                     # Django management script
└── requirements.txt              # Python dependencies
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
- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Debug Toolbar**: Available on any page when DEBUG=True

### 4. Create an Admin User

```bash
docker compose exec rides-api python manage.py createsuperuser
```

Follow the prompts to create an admin user with `role='admin'`.

### 5. Populate Test Data (Optional)

```bash
make populate
```

This creates:
- 10 riders (passenger_1 through passenger_10)
- 10 drivers (driver_1 through driver_10)
- 50 rides with random data
- 50 ride events linked to rides

## Makefile Commands

The project includes a Makefile for convenient operations:

```bash
make help       # Show all available commands
make up         # Start Docker containers
make down       # Stop Docker containers
make migrate    # Run database migrations
make test       # Run all tests (80 tests)
make populate   # Populate database with 50 rides and 50 events
make clean      # Remove all rides and events from database
make shell      # Open Django shell
make logs       # View Docker logs
```

## Database Models

### User
Custom user model with role-based access:
- `id_user` (Primary Key)
- `username`, `email`, `first_name`, `last_name`
- `role` - Choices: `driver`, `passenger`, `admin`
- `phone_number`
- Inherits from Django's `AbstractUser`

### Ride
Represents a ride with pickup and dropoff locations:
- `id_ride` (Primary Key)
- `status` - Choices: `en-route`, `pickup`, `dropoff`
- `id_rider` (ForeignKey to User)
- `id_driver` (ForeignKey to User)
- `pickup_latitude`, `pickup_longitude`
- `dropoff_latitude`, `dropoff_longitude`
- `pickup_time`

### RideEvent
Tracks events during a ride with custom manager:
- `id_ride_event` (Primary Key)
- `id_ride` (ForeignKey to Ride)
- `description`
- `created_at` (auto-set)
- **Default Manager**: Returns only events from past 24 hours
- **Methods**:
  - `all_unfiltered()` - Get all events without time filter
  - `for_ride(ride)` - Get all events for a specific ride

## API Endpoints

### Authentication

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "your-password"
}
```

**Response:**
```json
{
    "token": "abc123...",
    "id_user": 1,
    "username": "admin",
    "role": "admin"
}
```

**Authentication Required:**
All API endpoints require token authentication. Include the token in the header:
```
Authorization: Token abc123...
```

**Permission:**
All endpoints require `role='admin'`.

---

### Users

#### List Users
```http
GET /api/users/
Authorization: Token abc123...
```

Returns lightweight list of users (id, username, first_name, last_name, role).

#### Get User Details
```http
GET /api/users/{id_user}/
Authorization: Token abc123...
```

#### Create User
```http
POST /api/users/
Authorization: Token abc123...
Content-Type: application/json

{
    "username": "driver1",
    "email": "driver1@example.com",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe",
    "role": "driver",
    "phone_number": "1234567890"
}
```

#### Update User
```http
PUT /api/users/{id_user}/
PATCH /api/users/{id_user}/
Authorization: Token abc123...
```

#### Delete User
```http
DELETE /api/users/{id_user}/
Authorization: Token abc123...
```

---

### Rides

#### List Rides
```http
GET /api/rides/
Authorization: Token abc123...
```

**Query Parameters:**
- `limit` - Number of results per page (default: 20, max: 100)
- `offset` - Starting position for pagination
- `status` - Filter by ride status (`en-route`, `pickup`, `dropoff`)
- `id_rider__email` - Filter by rider email
- `ordering` - Sort results:
  - `pickup_time` - Sort by pickup time (ascending)
  - `-pickup_time` - Sort by pickup time (descending)
  - `distance` - Sort by distance to pickup (requires `lat` and `lng`)
  - `-distance` - Sort by distance (descending)
- `lat`, `lng` - Your GPS coordinates for distance calculation

**Examples:**
```http
# Get rides sorted by pickup time (most recent first)
GET /api/rides/?ordering=-pickup_time

# Get rides sorted by distance to your location
GET /api/rides/?ordering=distance&lat=40.7128&lng=-74.0060

# Filter by status
GET /api/rides/?status=en-route

# Filter by rider email
GET /api/rides/?id_rider__email=passenger1@example.com

# Pagination
GET /api/rides/?limit=10&offset=20
```

**Response includes:**
- Pagination metadata (count, next, previous)
- List of rides with basic info and events

#### Get Ride Details
```http
GET /api/rides/{id_ride}/
Authorization: Token abc123...
```

Returns detailed ride information with rider/driver details and all events.

#### Create Ride
```http
POST /api/rides/
Authorization: Token abc123...
Content-Type: application/json

{
    "status": "en-route",
    "id_rider": 2,
    "id_driver": 3,
    "pickup_latitude": 40.7128,
    "pickup_longitude": -74.0060,
    "dropoff_latitude": 40.7580,
    "dropoff_longitude": -73.9855,
    "pickup_time": "2025-10-29T14:30:00Z"
}
```

#### Update Ride
```http
PUT /api/rides/{id_ride}/
PATCH /api/rides/{id_ride}/
Authorization: Token abc123...
```

#### Delete Ride
```http
DELETE /api/rides/{id_ride}/
Authorization: Token abc123...
```

---

### Ride Events

#### List Ride Events
```http
GET /api/ride-events/
Authorization: Token abc123...
```

Returns events from the **past 24 hours only** by default.

#### Get Ride Event Details
```http
GET /api/ride-events/{id_ride_event}/
Authorization: Token abc123...
```

#### Create Ride Event
```http
POST /api/ride-events/
Authorization: Token abc123...
Content-Type: application/json

{
    "id_ride": 1,
    "description": "Driver arrived at pickup location"
}
```

#### Update Ride Event
```http
PUT /api/ride-events/{id_ride_event}/
PATCH /api/ride-events/{id_ride_event}/
Authorization: Token abc123...
```

#### Delete Ride Event
```http
DELETE /api/ride-events/{id_ride_event}/
Authorization: Token abc123...
```

## Distance Calculation

The API uses the **Haversine formula** for distance calculation:
- Calculates great-circle distance between two points on Earth
- Database-level calculation for efficiency (no Python loops)
- Returns distance in kilometers
- Accurate for short distances (~0.1-0.5% error)
- Formula: `distance = R * acos(cos(lat1) * cos(lat2) * cos(lng2 - lng1) + sin(lat1) * sin(lat2))`
  - Where R = 6371 km (Earth's radius)

**Why Haversine?**
- No external libraries required (uses standard PostgreSQL functions)
- Much faster than GeodeticCalculator for large datasets
- Sufficient accuracy for ride-sharing use cases

## Testing

The project includes 80 comprehensive tests:

### Run All Tests
```bash
make test
# Or:
docker compose exec rides-api python manage.py test rides
```

### Test Structure
- **Model Tests** (32 tests) - Test User, Ride, RideEvent models and custom managers
- **Serializer Tests** (19 tests) - Test all serializers and validation
- **View Tests** (29 tests) - Test CRUD operations, filtering, ordering, pagination, and authentication

### GitHub Actions CI/CD

The project uses GitHub Actions for automated testing on every push and pull request:

1. Sets up Python 3.10 and PostgreSQL 15
2. Installs dependencies
3. Runs migrations
4. Executes all 80 tests
5. Reports results in the GitHub Actions tab

**Workflow File:** `.github/workflows/tests.yml`

**View Test Results:**
- Go to your GitHub repository
- Click on the "Actions" tab
- View test results for each commit/PR

## Performance Optimizations

1. **Query Optimization**
   - `select_related()` for ForeignKey relationships (rider, driver)
   - `prefetch_related()` for reverse ForeignKey (events)
   - Database-level distance calculation with annotations

2. **Cached Pagination**
   - Caches COUNT(*) queries for 5 minutes
   - Reduces database load on large datasets
   - Cache key based on SQL query hash

3. **Efficient Filtering**
   - Uses `django-filter` for database-level filtering
   - No Python-level filtering overhead

4. **Custom Managers**
   - RideEvent default filter to past 24 hours
   - Prevents accidental full table scans

## Development Workflow

### Running the Project

```bash
# Start services
make up

# Stop services
make down

# View logs
make logs

# Rebuild after dependency changes
docker compose up --build
```

### Database Migrations

```bash
# Create migrations
docker compose exec rides-api python manage.py makemigrations

# Apply migrations
make migrate

# Migrations run automatically on container startup
```

### Django Shell

```bash
make shell
```

### Populate Test Data

```bash
# Add 50 rides and 50 events
make populate

# Clear all rides and events
make clean

# Re-populate fresh data
make clean && make populate
```

## Environment Variables

Key environment variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DB_ENGINE` | Database engine | `django.db.backends.postgresql` |
| `DB_NAME` | Database name | `db` |
| `DB_USER` | Database user | `superuser` |
| `DB_PASSWORD` | Database password | `superpass` |
| `DB_HOST` | Database host | `db` (Docker service name) |
| `DB_PORT` | Database port | `5432` |

## Django Debug Toolbar

The project includes Django Debug Toolbar for development. Access it by:

1. Visit any page in your browser (e.g., http://localhost:8000/api/)
2. Look for the debug toolbar on the right side
3. Click the **SQL** panel to inspect database queries

The toolbar is only available when `DEBUG=True`.

## Services

### Rides API Service
- **Port**: 8000
- **Command**: `python manage.py runserver 0.0.0.0:8000`
- **Features**: Auto-reload on code changes

### Database Service
- **Database**: PostgreSQL 15
- **Port**: 5432 (exposed for local access)
- **Volume**: `postgres_data` (persistent storage)

## Security Notes

- **Production Deployment**: This is a development setup. For production:
  - Set `DEBUG=False`
  - Use a strong `SECRET_KEY`
  - Configure proper `ALLOWED_HOSTS`
  - Use environment variables for secrets (never commit `.env`)
  - Consider using gunicorn/uwsgi instead of runserver
  - Set up HTTPS with a reverse proxy (nginx/Apache)

- **Authentication**: All API endpoints require token authentication and admin role

## License

This project is for educational and collaboration purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass (`make test`)
5. Submit a pull request

The CI pipeline will automatically run tests on your PR.
