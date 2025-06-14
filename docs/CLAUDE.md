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

## Learned Standards (from Tasks 1-5)

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

### Database Transaction Management (from Task 5)
```python
# Critical fix for execute_query function
if fetch_one:
    result = cur.fetchone()
    conn.commit()  # MUST commit INSERT/UPDATE...RETURNING queries
    return result
```

### Model Constructor Pattern (from Task 5)
```python
# Correct pattern for get_by_id methods
@classmethod
def get_by_id(cls, id: int) -> Optional['ModelName']:
    result = execute_query("SELECT id, field1, field2... FROM table WHERE id = %s", (id,), fetch_one=True)
    if result:
        # Use explicit keyword arguments, not positional unpacking
        return cls(field1=result[1], field2=result[2], ..., id=result[0])
    return None
```

### REST Endpoint Implementation Pattern (from Task 5)
```python
@app.route('/api/resource', methods=['POST'])
def create_resource():
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("VALIDATION_ERROR", "Request body must be JSON")), 400
        
        # Parse and validate input data (dates, times, required fields)
        resource = Model(**validated_data)
        resource.save()
        
        return jsonify(create_success_response(resource.to_dict())), 201
    except ValidationError as e:
        return jsonify(create_error_response("VALIDATION_ERROR", str(e))), 400
    except Exception as e:
        logger.error(f"Failed to create resource: {e}")
        return jsonify(create_error_response("DATABASE_ERROR", "Failed to create resource")), 500
```

### Foreign Key Validation Pattern
- Always verify parent resources exist before creating children
- Return 404 with descriptive message if parent not found
- Use consistent error messages: "Parent with id {id} not found"

### Date/Time Input Validation
- Dates: YYYY-MM-DD format using `datetime.strptime(date_str, '%Y-%m-%d').date()`
- Times: HH:MM format using `datetime.strptime(time_str, '%H:%M').time()`  
- Return 400 with format requirement in error message if parsing fails

### Frontend Integration Standards (from Task 8)

#### Flask Template Integration
```python
# Frontend route pattern
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Separate API info endpoint
@app.route('/api', methods=['GET'])
def api_info():
    return jsonify(api_documentation)
```

#### Static File Organization
```
static/
├── css/style.css      # Custom CSS with CSS custom properties
└── js/app.js          # JavaScript utilities and API wrapper

templates/
├── base.html          # Bootstrap base template with navigation
└── index.html         # Page-specific content extending base
```

#### JavaScript Architecture Pattern
```javascript
// Global API wrapper object
const TravelPlanner = {
    async get(endpoint) { /* HTTP GET */ },
    async post(endpoint, data) { /* HTTP POST */ },
    async put(endpoint, data) { /* HTTP PUT */ },
    async delete(endpoint) { /* HTTP DELETE */ },
    
    // UI utilities
    showLoading(element), hideLoading(element),
    showSuccess(message), showError(message),
    validateForm(form), formatDate(date)
};
```

#### Bootstrap Integration Standards
- Use Bootstrap 5.3 CDN for consistency and performance
- Custom CSS variables for theme customization
- Responsive design with mobile-first approach
- Form validation integrated with Bootstrap styling classes

#### Port Configuration
- Default port 5001 to avoid macOS AirPlay conflicts
- Environment variable `FLASK_RUN_PORT` for customization
- Use `0.0.0.0` host for Docker compatibility

### Enhanced Frontend Standards (from Task 9)

#### Modal Architecture Pattern
```html
<!-- Consistent modal structure -->
<div class="modal fade" id="modalName" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Title</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="formId">
                <div class="modal-body"><!-- Form fields --></div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Submit</button>
                </div>
            </form>
        </div>
    </div>
</div>
```

#### State Management Pattern
```javascript
// Global state variables for modal operations
let currentEditingTripId = null;
let currentDeletingTripId = null;

// Setup functions for each modal
function setupCreateForm() { /* Event listeners */ }
function setupEditForm() { /* Pre-populate and submit */ }
function setupDeleteConfirmation() { /* Confirmation handling */ }
```

#### Responsive Design System
```css
/* Mobile-first breakpoints */
@media (max-width: 576px) { 
    /* Icon-only buttons, compact layouts */ 
}
@media (max-width: 768px) { 
    /* Stacked layouts, full-width actions */ 
}
```

#### Enhanced Form Validation Pattern
```javascript
function validateTripData(data, form) {
    // Clear previous validation
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
    
    let isValid = true;
    
    // Field-specific validation with Bootstrap styling
    if (!data.name) {
        isValid = false;
        showFieldError(form.querySelector('[name="name"]'), 'Field is required');
    }
    
    return isValid;
}
```

#### Bootstrap Icons Integration
- Use Bootstrap Icons 1.11.0 CDN for consistent iconography
- Standard icons: `bi-eye` (view), `bi-pencil` (edit), `bi-trash` (delete)
- Icon + text pattern for desktop, icon-only for mobile
- Button groups for professional action grouping