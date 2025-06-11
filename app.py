"""
Flask application for Travel Planner API.
Provides REST endpoints for trip, day, and activity management.
"""

import os
import logging
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from typing import Dict, Any, Optional
import atexit

from config import get_config
from database import init_db, close_connection_pool, test_connection, get_db_stats
from models import ValidationError, Trip, Day, Activity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(env_name: Optional[str] = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        env_name: Environment name (development, production, testing)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(env_name)
    app.config.from_object(config)
    
    # Initialize CORS
    CORS(app, origins=config.CORS_ORIGINS)
    
    # Initialize database
    try:
        init_db(env_name)
        logger.info(f"Database initialized for {env_name or 'default'} environment")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Register cleanup handler
    atexit.register(close_connection_pool)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app)
    
    logger.info(f"Flask app created for {env_name or 'default'} environment")
    return app


def register_error_handlers(app: Flask) -> None:
    """Register application-wide error handlers."""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError) -> tuple:
        """Handle model validation errors."""
        logger.warning(f"Validation error: {error}")
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(error),
                "details": None
            }
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(error) -> tuple:
        """Handle 404 errors."""
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "NOT_FOUND",
                "message": "Resource not found",
                "details": None
            }
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error) -> tuple:
        """Handle 405 errors."""
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "METHOD_NOT_ALLOWED",
                "message": "Method not allowed",
                "details": None
            }
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error) -> tuple:
        """Handle internal server errors."""
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "SERVER_ERROR",
                "message": "Internal server error",
                "details": None
            }
        }), 500
    
    @app.errorhandler(Exception)
    def handle_generic_error(error: Exception) -> tuple:
        """Handle unexpected errors."""
        logger.error(f"Unexpected error: {error}", exc_info=True)
        return jsonify({
            "success": False,
            "data": None,
            "error": {
                "code": "SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": None
            }
        }), 500


def register_routes(app: Flask) -> None:
    """Register application routes."""
    
    @app.route('/health', methods=['GET'])
    def health_check() -> Dict[str, Any]:
        """
        Health check endpoint.
        
        Returns:
            Application status and database connectivity
        """
        try:
            # Test database connection
            db_healthy = test_connection()
            
            # Get database stats
            stats = get_db_stats() if db_healthy else {}
            
            return jsonify({
                "success": True,
                "data": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "database": {
                        "connected": db_healthy,
                        "stats": stats
                    },
                    "environment": app.config.get('ENV', 'unknown'),
                    "debug": app.config.get('DEBUG', False)
                },
                "error": None
            })
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                "success": False,
                "data": None,
                "error": {
                    "code": "HEALTH_CHECK_FAILED",
                    "message": "Health check failed",
                    "details": str(e)
                }
            }), 500
    
    @app.route('/', methods=['GET'])
    def index():
        """Frontend application main page."""
        return render_template('index.html')
    
    @app.route('/api', methods=['GET'])
    def api_info() -> Dict[str, Any]:
        """API information endpoint."""
        return jsonify({
            "success": True,
            "data": {
                "name": "Travel Planner API",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "trips": "/api/trips",
                    "days": "/api/trips/{trip_id}/days, /api/days/{id}",
                    "activities": "/api/days/{day_id}/activities, /api/activities/{id}"
                }
            },
            "error": None
        })

    # ============ TRIP ENDPOINTS ============
    
    @app.route('/api/trips', methods=['GET'])
    def get_trips() -> Dict[str, Any]:
        """Get all trips."""
        try:
            trips = Trip.get_all()
            return jsonify(create_success_response([trip.to_dict() for trip in trips]))
        except Exception as e:
            logger.error(f"Failed to get trips: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to retrieve trips"
            )), 500
    
    @app.route('/api/trips', methods=['POST'])
    def create_trip() -> Dict[str, Any]:
        """Create a new trip."""
        try:
            data = request.get_json()
            if not data:
                return jsonify(create_error_response(
                    "VALIDATION_ERROR", "Request body must be JSON"
                )), 400
            
            # Parse dates if provided
            start_date = None
            end_date = None
            if data.get('start_date'):
                try:
                    from datetime import datetime
                    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify(create_error_response(
                        "VALIDATION_ERROR", "start_date must be in YYYY-MM-DD format"
                    )), 400
            
            if data.get('end_date'):
                try:
                    from datetime import datetime
                    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify(create_error_response(
                        "VALIDATION_ERROR", "end_date must be in YYYY-MM-DD format"
                    )), 400
            
            trip = Trip(
                name=data.get('name'),
                description=data.get('description'),
                start_date=start_date,
                end_date=end_date
            )
            trip.save()
            
            return jsonify(create_success_response(trip.to_dict())), 201
            
        except ValidationError as e:
            return jsonify(create_error_response(
                "VALIDATION_ERROR", str(e)
            )), 400
        except Exception as e:
            logger.error(f"Failed to create trip: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to create trip"
            )), 500
    
    @app.route('/api/trips/<int:trip_id>', methods=['GET'])
    def get_trip(trip_id: int) -> Dict[str, Any]:
        """Get a specific trip by ID."""
        try:
            trip = Trip.get_by_id(trip_id)
            if not trip:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Trip with id {trip_id} not found"
                )), 404
            
            return jsonify(create_success_response(trip.to_dict()))
            
        except Exception as e:
            logger.error(f"Failed to get trip {trip_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to retrieve trip"
            )), 500
    
    @app.route('/api/trips/<int:trip_id>', methods=['PUT'])
    def update_trip(trip_id: int) -> Dict[str, Any]:
        """Update a specific trip."""
        try:
            trip = Trip.get_by_id(trip_id)
            if not trip:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Trip with id {trip_id} not found"
                )), 404
            
            data = request.get_json()
            if not data:
                return jsonify(create_error_response(
                    "VALIDATION_ERROR", "Request body must be JSON"
                )), 400
            
            # Update fields if provided
            if 'name' in data:
                trip.name = data['name']
            if 'description' in data:
                trip.description = data['description']
            
            # Parse dates if provided
            if 'start_date' in data:
                if data['start_date']:
                    try:
                        from datetime import datetime
                        trip.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify(create_error_response(
                            "VALIDATION_ERROR", "start_date must be in YYYY-MM-DD format"
                        )), 400
                else:
                    trip.start_date = None
            
            if 'end_date' in data:
                if data['end_date']:
                    try:
                        from datetime import datetime
                        trip.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify(create_error_response(
                            "VALIDATION_ERROR", "end_date must be in YYYY-MM-DD format"
                        )), 400
                else:
                    trip.end_date = None
            
            trip.save()
            return jsonify(create_success_response(trip.to_dict()))
            
        except ValidationError as e:
            return jsonify(create_error_response(
                "VALIDATION_ERROR", str(e)
            )), 400
        except Exception as e:
            logger.error(f"Failed to update trip {trip_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to update trip"
            )), 500
    
    @app.route('/api/trips/<int:trip_id>', methods=['DELETE'])
    def delete_trip(trip_id: int) -> Dict[str, Any]:
        """Delete a specific trip."""
        try:
            trip = Trip.get_by_id(trip_id)
            if not trip:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Trip with id {trip_id} not found"
                )), 404
            
            if trip.delete():
                return jsonify(create_success_response({"message": "Trip deleted successfully"}))
            else:
                return jsonify(create_error_response(
                    "DATABASE_ERROR", "Failed to delete trip"
                )), 500
                
        except Exception as e:
            logger.error(f"Failed to delete trip {trip_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to delete trip"
            )), 500

    # ============ DAY ENDPOINTS ============
    
    @app.route('/api/trips/<int:trip_id>/days', methods=['GET'])
    def get_days_for_trip(trip_id: int) -> Dict[str, Any]:
        """Get all days for a specific trip."""
        try:
            # Verify trip exists
            trip = Trip.get_by_id(trip_id)
            if not trip:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Trip with id {trip_id} not found"
                )), 404
            
            days = Day.get_by_trip_id(trip_id)
            return jsonify(create_success_response([day.to_dict() for day in days]))
            
        except Exception as e:
            logger.error(f"Failed to get days for trip {trip_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to retrieve days"
            )), 500
    
    @app.route('/api/trips/<int:trip_id>/days', methods=['POST'])
    def create_day(trip_id: int) -> Dict[str, Any]:
        """Create a new day for a specific trip."""
        try:
            # Verify trip exists
            trip = Trip.get_by_id(trip_id)
            if not trip:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Trip with id {trip_id} not found"
                )), 404
            
            data = request.get_json()
            if not data:
                return jsonify(create_error_response(
                    "VALIDATION_ERROR", "Request body must be JSON"
                )), 400
            
            # Parse date
            day_date = None
            if data.get('date'):
                try:
                    from datetime import datetime
                    day_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify(create_error_response(
                        "VALIDATION_ERROR", "date must be in YYYY-MM-DD format"
                    )), 400
            
            day = Day(
                trip_id=trip_id,
                date=day_date,
                day_number=data.get('day_number')
            )
            day.save()
            
            return jsonify(create_success_response(day.to_dict())), 201
            
        except ValidationError as e:
            return jsonify(create_error_response(
                "VALIDATION_ERROR", str(e)
            )), 400
        except Exception as e:
            logger.error(f"Failed to create day for trip {trip_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to create day"
            )), 500
    
    @app.route('/api/days/<int:day_id>', methods=['GET'])
    def get_day(day_id: int) -> Dict[str, Any]:
        """Get a specific day by ID."""
        try:
            day = Day.get_by_id(day_id)
            if not day:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Day with id {day_id} not found"
                )), 404
            
            return jsonify(create_success_response(day.to_dict()))
            
        except Exception as e:
            logger.error(f"Failed to get day {day_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to retrieve day"
            )), 500
    
    @app.route('/api/days/<int:day_id>', methods=['PUT'])
    def update_day(day_id: int) -> Dict[str, Any]:
        """Update a specific day."""
        try:
            day = Day.get_by_id(day_id)
            if not day:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Day with id {day_id} not found"
                )), 404
            
            data = request.get_json()
            if not data:
                return jsonify(create_error_response(
                    "VALIDATION_ERROR", "Request body must be JSON"
                )), 400
            
            # Update fields if provided
            if 'trip_id' in data:
                day.trip_id = data['trip_id']
            if 'day_number' in data:
                day.day_number = data['day_number']
            
            # Parse date if provided
            if 'date' in data:
                if data['date']:
                    try:
                        from datetime import datetime
                        day.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify(create_error_response(
                            "VALIDATION_ERROR", "date must be in YYYY-MM-DD format"
                        )), 400
                else:
                    day.date = None
            
            day.save()
            return jsonify(create_success_response(day.to_dict()))
            
        except ValidationError as e:
            return jsonify(create_error_response(
                "VALIDATION_ERROR", str(e)
            )), 400
        except Exception as e:
            logger.error(f"Failed to update day {day_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to update day"
            )), 500
    
    @app.route('/api/days/<int:day_id>', methods=['DELETE'])
    def delete_day(day_id: int) -> Dict[str, Any]:
        """Delete a specific day."""
        try:
            day = Day.get_by_id(day_id)
            if not day:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Day with id {day_id} not found"
                )), 404
            
            if day.delete():
                return jsonify(create_success_response({"message": "Day deleted successfully"}))
            else:
                return jsonify(create_error_response(
                    "DATABASE_ERROR", "Failed to delete day"
                )), 500
                
        except Exception as e:
            logger.error(f"Failed to delete day {day_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to delete day"
            )), 500

    # ============ ACTIVITY ENDPOINTS ============
    
    @app.route('/api/days/<int:day_id>/activities', methods=['GET'])
    def get_activities_for_day(day_id: int) -> Dict[str, Any]:
        """Get all activities for a specific day."""
        try:
            # Verify day exists
            day = Day.get_by_id(day_id)
            if not day:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Day with id {day_id} not found"
                )), 404
            
            activities = Activity.get_by_day_id(day_id)
            return jsonify(create_success_response([activity.to_dict() for activity in activities]))
            
        except Exception as e:
            logger.error(f"Failed to get activities for day {day_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to retrieve activities"
            )), 500
    
    @app.route('/api/days/<int:day_id>/activities', methods=['POST'])
    def create_activity(day_id: int) -> Dict[str, Any]:
        """Create a new activity for a specific day."""
        try:
            # Verify day exists
            day = Day.get_by_id(day_id)
            if not day:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Day with id {day_id} not found"
                )), 404
            
            data = request.get_json()
            if not data:
                return jsonify(create_error_response(
                    "VALIDATION_ERROR", "Request body must be JSON"
                )), 400
            
            # Parse times if provided
            start_time = None
            end_time = None
            if data.get('start_time'):
                try:
                    from datetime import datetime
                    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
                except ValueError:
                    return jsonify(create_error_response(
                        "VALIDATION_ERROR", "start_time must be in HH:MM format"
                    )), 400
            
            if data.get('end_time'):
                try:
                    from datetime import datetime
                    end_time = datetime.strptime(data['end_time'], '%H:%M').time()
                except ValueError:
                    return jsonify(create_error_response(
                        "VALIDATION_ERROR", "end_time must be in HH:MM format"
                    )), 400
            
            activity = Activity(
                day_id=day_id,
                name=data.get('name'),
                description=data.get('description'),
                start_time=start_time,
                end_time=end_time,
                order_index=data.get('order_index', 0)
            )
            activity.save()
            
            return jsonify(create_success_response(activity.to_dict())), 201
            
        except ValidationError as e:
            return jsonify(create_error_response(
                "VALIDATION_ERROR", str(e)
            )), 400
        except Exception as e:
            logger.error(f"Failed to create activity for day {day_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to create activity"
            )), 500
    
    @app.route('/api/activities/<int:activity_id>', methods=['GET'])
    def get_activity(activity_id: int) -> Dict[str, Any]:
        """Get a specific activity by ID."""
        try:
            activity = Activity.get_by_id(activity_id)
            if not activity:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Activity with id {activity_id} not found"
                )), 404
            
            return jsonify(create_success_response(activity.to_dict()))
            
        except Exception as e:
            logger.error(f"Failed to get activity {activity_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to retrieve activity"
            )), 500
    
    @app.route('/api/activities/<int:activity_id>', methods=['PUT'])
    def update_activity(activity_id: int) -> Dict[str, Any]:
        """Update a specific activity."""
        try:
            activity = Activity.get_by_id(activity_id)
            if not activity:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Activity with id {activity_id} not found"
                )), 404
            
            data = request.get_json()
            if not data:
                return jsonify(create_error_response(
                    "VALIDATION_ERROR", "Request body must be JSON"
                )), 400
            
            # Update fields if provided
            if 'day_id' in data:
                activity.day_id = data['day_id']
            if 'name' in data:
                activity.name = data['name']
            if 'description' in data:
                activity.description = data['description']
            if 'order_index' in data:
                activity.order_index = data['order_index']
            
            # Parse times if provided
            if 'start_time' in data:
                if data['start_time']:
                    try:
                        from datetime import datetime
                        activity.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
                    except ValueError:
                        return jsonify(create_error_response(
                            "VALIDATION_ERROR", "start_time must be in HH:MM format"
                        )), 400
                else:
                    activity.start_time = None
            
            if 'end_time' in data:
                if data['end_time']:
                    try:
                        from datetime import datetime
                        activity.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
                    except ValueError:
                        return jsonify(create_error_response(
                            "VALIDATION_ERROR", "end_time must be in HH:MM format"
                        )), 400
                else:
                    activity.end_time = None
            
            activity.save()
            return jsonify(create_success_response(activity.to_dict()))
            
        except ValidationError as e:
            return jsonify(create_error_response(
                "VALIDATION_ERROR", str(e)
            )), 400
        except Exception as e:
            logger.error(f"Failed to update activity {activity_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to update activity"
            )), 500
    
    @app.route('/api/activities/<int:activity_id>', methods=['DELETE'])
    def delete_activity(activity_id: int) -> Dict[str, Any]:
        """Delete a specific activity."""
        try:
            activity = Activity.get_by_id(activity_id)
            if not activity:
                return jsonify(create_error_response(
                    "NOT_FOUND", f"Activity with id {activity_id} not found"
                )), 404
            
            if activity.delete():
                return jsonify(create_success_response({"message": "Activity deleted successfully"}))
            else:
                return jsonify(create_error_response(
                    "DATABASE_ERROR", "Failed to delete activity"
                )), 500
                
        except Exception as e:
            logger.error(f"Failed to delete activity {activity_id}: {e}")
            return jsonify(create_error_response(
                "DATABASE_ERROR", "Failed to delete activity"
            )), 500


def create_success_response(data: Any) -> Dict[str, Any]:
    """
    Create standardized success response.
    
    Args:
        data: Response data
        
    Returns:
        Standardized success response
    """
    return {
        "success": True,
        "data": data,
        "error": None
    }


def create_error_response(
    code: str, 
    message: str, 
    details: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        code: Error code
        message: Error message
        details: Optional error details
        
    Returns:
        Standardized error response
    """
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }


# Create application instance
app = create_app()


if __name__ == '__main__':
    """Run the Flask development server."""
    env = os.environ.get('FLASK_ENV', 'development')
    debug = env == 'development'
    
    logger.info(f"Starting Flask app in {env} mode")
    logger.info(f"Debug mode: {debug}")
    
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )