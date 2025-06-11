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

# Code Quality
black .                   # Format code
flake8 .                 # Check style
pytest                   # Run tests

# Database
# Setup PostgreSQL locally or use Docker
# Run migrations/setup scripts
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
- **Structured Logging**: Use consistent log format
- **Error Logging**: Log errors with sufficient context
- **Debug Mode**: Clear distinction between development and production
- **Performance Monitoring**: Log slow queries and requests