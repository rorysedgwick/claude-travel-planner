# Travel Planner - Architectural Specification

## System Architecture 🏢

### Overall Architecture Pattern 📜
**Flask API + Separate Frontend**
- Backend: Flask REST API serving JSON responses
- Frontend: Separate client application consuming the API
- Clear separation of concerns between data layer and presentation layer

### Technology Stack 🔧

#### Backend
- **Language**: Python 3.8+
- **Framework**: Flask (lightweight, flexible web framework)
- **Database**: PostgreSQL (robust SQL database with JSON support)
- **Package Management**: pip + requirements.txt
- **API Design**: RESTful CRUD operations

#### Frontend
- **Styling**: Bootstrap + custom CSS
- **Architecture**: Single-page application consuming Flask API
- **UI Pattern**: List-based management with inline editing

## Project Structure 📁

### Flask Backend Structure (Simple Flat Layout) 📝
```
/
├── app.py              # Main Flask application and routes
├── models.py           # Database models and schemas
├── database.py         # Database connection and initialization
├── utils.py            # Helper functions and utilities
├── requirements.txt    # Python dependencies
└── config.py           # Configuration settings
```

### Database Schema 🗄

#### Tables
```sql
-- Trips table
trips (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Days table (represents individual days within a trip)
days (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    day_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Activities table
activities (
    id SERIAL PRIMARY KEY,
    day_id INTEGER REFERENCES days(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIME,
    end_time TIME,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## API Design 🔌

### RESTful Endpoints 🎯

#### Trip Management
```
GET    /api/trips              # List all trips
POST   /api/trips              # Create new trip
GET    /api/trips/{id}          # Get specific trip
PUT    /api/trips/{id}          # Update trip
DELETE /api/trips/{id}          # Delete trip
```

#### Day Management
```
GET    /api/trips/{trip_id}/days       # Get days for trip
POST   /api/trips/{trip_id}/days       # Add day to trip
PUT    /api/days/{id}                  # Update day
DELETE /api/days/{id}                  # Delete day
```

#### Activity Management (Core Focus)
```
GET    /api/days/{day_id}/activities   # Get activities for day
POST   /api/days/{day_id}/activities   # Add activity to day
GET    /api/activities/{id}            # Get specific activity
PUT    /api/activities/{id}            # Update activity
DELETE /api/activities/{id}            # Delete activity
PUT    /api/activities/{id}/reorder    # Reorder activity within day
```

### Response Format 📝
```json
{
  "success": true,
  "data": { ... },
  "error": null
}

// Error responses
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

## Data Models 🗺

### Python Models (SQLAlchemy/Raw SQL) 🐍
```python
# Trip Model
class Trip:
    id: int
    name: str
    description: str
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime

# Day Model  
class Day:
    id: int
    trip_id: int
    date: date
    day_number: int
    created_at: datetime

# Activity Model
class Activity:
    id: int
    day_id: int
    name: str
    description: str
    start_time: time
    end_time: time
    order_index: int
    created_at: datetime
    updated_at: datetime
```

## Error Handling Strategy ⚠️

### Structured Error Responses 📝
- Consistent JSON error format across all endpoints
- HTTP status codes: 400 (Bad Request), 404 (Not Found), 500 (Server Error)
- Error codes for client-side handling
- Detailed error messages for debugging
- Validation error details for form handling

### Error Categories 📂
- `VALIDATION_ERROR`: Input validation failures
- `NOT_FOUND`: Resource not found
- `DATABASE_ERROR`: Database operation failures
- `SERVER_ERROR`: Unexpected server errors

## Design Patterns 🎨

### Backend Patterns ⚙️
- **Repository Pattern**: Data access abstraction layer
- **Service Layer**: Business logic separation from routes
- **DTO Pattern**: Data transfer objects for API responses
- **Factory Pattern**: Database connection and model creation

### Database Patterns 🗄
- **Foreign Key Constraints**: Maintain referential integrity
- **Cascade Deletes**: Automatic cleanup of related records
- **Indexing**: Performance optimization for common queries
- **Timestamps**: Audit trail for all records

## Development Principles 🌱

### Pragmatic Balance Approach ⚖️
- Simple solutions for straightforward requirements
- Clean patterns for complex business logic
- Focus on delivery timeline without sacrificing maintainability
- Code quality balanced with development speed

### Performance Considerations 🚀
- Database indexing on frequently queried fields
- Efficient SQL queries with proper JOINs
- JSON response optimization
- Connection pooling for database access

## Deployment Architecture 🚀

### Simple Deployment Model 📦
- Single Flask application server
- PostgreSQL database server
- Static file serving for frontend assets
- Environment-based configuration (development/production)

### Configuration Management ⚙️
- Environment variables for sensitive data
- Separate config files for different environments
- Database connection string management
- CORS configuration for frontend integration