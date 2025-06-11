# Travel Planner

A web-based travel itinerary management system built with Flask API backend and separate frontend. Focus on itinerary building with activities, scheduling, and multi-day trip organization.

## Technology Stack

- **Backend**: Python 3.12+, Flask, PostgreSQL
- **Frontend**: Bootstrap + custom CSS
- **Architecture**: Flask REST API + separate frontend
- **Database**: PostgreSQL with structured relationships

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL database
- pip package manager

### Setup

1. **Clone and navigate to project**
   ```bash
   cd claude-travel-planner
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

5. **Database setup**
   ```bash
   # Create PostgreSQL database
   createdb travel_planner_dev
   
   # Initialize database schema
   python -c "from database import init_db; init_db()"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`

## Development Workflow

### Code Quality

```bash
# Format code
black .

# Check code style
flake8 .

# Run tests
pytest
```

### Database Management

```bash
# Development database
createdb travel_planner_dev

# Test database
createdb travel_planner_test

# Reset database
python -c "from database import reset_db; reset_db()"
```

## API Endpoints

### Trips
- `GET /api/trips` - List all trips
- `POST /api/trips` - Create new trip
- `GET /api/trips/{id}` - Get specific trip
- `PUT /api/trips/{id}` - Update trip
- `DELETE /api/trips/{id}` - Delete trip

### Days
- `GET /api/trips/{trip_id}/days` - Get days for trip
- `POST /api/trips/{trip_id}/days` - Add day to trip
- `PUT /api/days/{id}` - Update day
- `DELETE /api/days/{id}` - Delete day

### Activities
- `GET /api/days/{day_id}/activities` - Get activities for day
- `POST /api/days/{day_id}/activities` - Add activity to day
- `GET /api/activities/{id}` - Get specific activity
- `PUT /api/activities/{id}` - Update activity
- `DELETE /api/activities/{id}` - Delete activity
- `PUT /api/activities/{id}/reorder` - Reorder activity within day

## Project Structure

```
/
├── app.py              # Main Flask application and routes
├── models.py           # Database models and schemas
├── database.py         # Database connection and initialization
├── utils.py            # Helper functions and utilities
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Flask settings
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database settings
DATABASE_URL=postgresql://localhost/travel_planner_dev
DEV_DATABASE_URL=postgresql://localhost/travel_planner_dev
TEST_DATABASE_URL=postgresql://localhost/travel_planner_test

# CORS settings (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest test_activities.py
```

## Contributing

1. Follow the code standards defined in `docs/CLAUDE.md`
2. Use conventional commit messages
3. Run code quality checks before committing
4. All changes require pull request review

## License

This project is for educational purposes.