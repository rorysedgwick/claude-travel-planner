# Claude Development Guidelines

## Project Overview
Travel itinerary management system with Flask API backend and separate frontend. Focus on itinerary building with activities, scheduling, and multi-day trip organization.

## Technology Stack
- **Backend**: Python 3.12+, Flask, PostgreSQL
- **Package Management**: pip + requirements.txt
- **Frontend**: Bootstrap + custom CSS
- **Architecture**: Flask API + separate frontend
- **Database**: PostgreSQL with structured relationships

## Code Standards

### Python Style
- **Formatter**: Black (auto-formatting)
- **Linter**: Flake8 (style enforcement)
- **Line Length**: 88 characters (Black default)
- **Import Organization**: Standard library, third-party, local imports

### Naming Conventions
- **Functions/Variables**: snake_case (`get_trip_activities`, `activity_list`)
- **Classes**: PascalCase (`TripModel`, `ActivityService`)
- **Constants**: UPPER_CASE (`DATABASE_URL`, `MAX_ACTIVITIES_PER_DAY`)
- **Files**: snake_case (`trip_routes.py`, `activity_models.py`)

### Code Organization
```
/
├── app.py              # Main Flask app and routes
├── models.py           # Database models
├── database.py         # DB connection and init
├── utils.py           # Helper functions
├── config.py          # Configuration
└── requirements.txt   # Dependencies
```

## Development Principles

### Pragmatic Balance
- **Simple First**: Use straightforward solutions for basic requirements
- **Clean Complexity**: Apply clean patterns only for complex business logic
- **Delivery Focus**: Balance code quality with timeline constraints
- **Maintainable**: Write code that's easy to understand and modify

### Code Quality Guidelines
- **Single Responsibility**: Each function should have one clear purpose
- **DRY Principle**: Don't repeat yourself, extract common functionality
- **Readable Code**: Prioritize clarity over cleverness
- **Proper Error Handling**: Use structured error responses consistently

## API Standards

### RESTful Design
- **Resource-based URLs**: `/api/trips`, `/api/activities`
- **HTTP Methods**: GET (read), POST (create), PUT (update), DELETE (remove)
- **Status Codes**: 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Server Error)

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Error Handling
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Activity name is required",
    "details": { ... }
  }
}
```

## Database Standards

### Schema Design
- **Foreign Keys**: Use proper relationships with CASCADE deletes
- **Timestamps**: Include created_at and updated_at on all tables
- **Indexing**: Index frequently queried fields
- **Naming**: snake_case for tables and columns

### Model Patterns
- **Data Models**: Simple classes representing database entities
- **Repository Pattern**: Abstract data access when complexity warrants
- **Validation**: Input validation before database operations

## Testing Requirements

### Test Coverage
- **Unit Tests**: Test individual functions and methods using pytest
- **Integration Tests**: Test full API request/response cycles
- **Database Tests**: Test data persistence and retrieval
- **Error Scenarios**: Test error handling and edge cases

### Test Organization
```python
# test_activities.py
def test_create_activity():
    # Test activity creation
    pass

def test_get_activities_for_day():
    # Test activity retrieval
    pass

def test_reorder_activities():
    # Test activity reordering
    pass
```

## Version Control Standards

### Conventional Commits
- **Format**: `type(scope): description`
- **Types**: 
  - `feat`: New features
  - `fix`: Bug fixes
  - `docs`: Documentation changes
  - `style`: Code style changes
  - `refactor`: Code refactoring
  - `test`: Test additions/changes

### Examples
```
feat(api): add activity reordering endpoint
fix(database): resolve cascade delete issue
docs(readme): update setup instructions
test(activities): add integration tests for CRUD operations
```

### Branch Strategy
- **Feature Branches**: Create branches for new features
- **Descriptive Names**: `feat/activity-reordering`, `fix/time-validation`
- **Pull Requests**: Use PRs for code review before merging
- **Clean History**: Squash commits when appropriate

## Documentation Requirements

### Code Documentation
- **Docstrings**: Document all functions and classes
- **Type Hints**: Use Python type hints where beneficial
- **Inline Comments**: Explain complex business logic
- **API Documentation**: Maintain OpenAPI/Swagger docs

### Project Documentation
- **README**: Setup instructions, development workflow
- **API Docs**: Endpoint documentation with examples
- **Architecture Docs**: System overview and design decisions
- **Deployment Guide**: Production deployment instructions

## Development Workflow

### Local Development
```bash
# Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Database (Docker - Recommended)
docker-compose up -d postgres    # Start Postgres container
# Database URL: postgresql://travel_planner:dev_password@localhost:5432/travel_planner_dev

# Database (Alternative - Local PostgreSQL)
# Install PostgreSQL locally and create database
# Set DATABASE_URL environment variable

# Code Quality
black .                   # Format code
flake8 .                 # Check style
pytest                   # Run tests

# Development Server
python app.py            # Start Flask development server
```

### Docker Commands
```bash
# Start database container
docker-compose up -d postgres

# Stop database container
docker-compose down

# View container logs
docker-compose logs postgres

# Reset database (removes all data)
docker-compose down -v && docker-compose up -d postgres

# Connect to database directly
docker exec -it travel_planner_postgres psql -U travel_planner -d travel_planner_dev
```

### Code Quality Checks
- **Pre-commit**: Run Black and Flake8 before commits
- **Testing**: Run test suite before pushing
- **Review**: All code changes go through pull requests

## Security Guidelines
- **Environment Variables**: Store sensitive data in environment variables
- **SQL Injection**: Use parameterized queries or ORM
- **Input Validation**: Validate all user inputs
- **Error Messages**: Don't expose sensitive information in error messages

## Performance Considerations
- **Database Queries**: Optimize N+1 query problems
- **Indexing**: Index frequently queried columns
- **Connection Pooling**: Use database connection pooling
- **Caching**: Cache frequently accessed data when appropriate

## Debugging and Logging
- **Structured Logging**: Use consistent log format with logging module
- **Error Logging**: Log errors with sufficient context, include rollback on database errors
- **Debug Mode**: Clear distinction between development and production
- **Performance Monitoring**: Log slow queries and requests

## Learned Standards (from Tasks 1-4)

### Database Connection Pattern
```python
# Connection pooling with proper cleanup
conn = get_connection()
try:
    # Execute operations
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    return_connection(conn)
```

### Model CRUD Pattern
```python
# Standard model operations
def save(self) -> 'ModelName':
    self.validate()  # Always validate before database operations
    if self.id is None:
        # INSERT with RETURNING for timestamps
        result = execute_query(query, params, fetch_one=True)
        self.id, self.created_at, self.updated_at = result
    else:
        # UPDATE with timestamp refresh
        result = execute_query(query, params, fetch_one=True)
        if result:
            self.updated_at = result[0]
        else:
            raise ValidationError(f"Record not found")
    return self
```

### Configuration Management
- Use environment-specific config classes inheriting from base Config
- Validate required environment variables in production config
- Default values for development environment

### Validation Strategy
- Custom exception classes for structured error handling
- Input validation before database operations (required fields, length constraints, business logic)
- Meaningful error messages without exposing sensitive information
- Boolean return values for delete operations (True if deleted, False if not found)

### Chronological Data Ordering
- Primary sort by time fields (start_time, created_at)
- Secondary sort by order_index for manual reordering
- Use `NULLS LAST` for optional time fields

### Flask Application Architecture (from Task 4)
```python
# Flask app factory pattern
def create_app(env_name: Optional[str] = None) -> Flask:
    app = Flask(__name__)
    config = get_config(env_name)
    app.config.from_object(config)
    
    # Initialize CORS, database, error handlers, routes
    CORS(app, origins=config.CORS_ORIGINS)
    init_db(env_name)
    register_error_handlers(app)
    register_routes(app)
    return app
```

### API Response Standardization
```python
# Success responses
{"success": true, "data": {...}, "error": null}

# Error responses  
{"success": false, "data": null, "error": {"code": "ERROR_CODE", "message": "...", "details": ...}}
```

### Error Handler Registration Pattern
- ValidationError → 400 with VALIDATION_ERROR code
- HTTP errors (404, 405, 500) with structured JSON responses
- Generic exception handler with logging for debugging
- Consistent error codes: VALIDATION_ERROR, NOT_FOUND, METHOD_NOT_ALLOWED, SERVER_ERROR

### Environment Configuration Resolution
- Development environment: Uses `DEV_DATABASE_URL` environment variable
- Production/base config: Uses `DATABASE_URL` environment variable  
- .env file should contain both for flexibility
- IPv4 addresses (127.0.0.1) preferred over localhost for Docker compatibility