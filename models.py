"""
Database models for Travel Planner application.
Contains Trip, Day, and Activity model definitions with CRUD operations.
"""

from datetime import date, time, datetime
from typing import Optional, List, Dict, Any
import logging
from database import execute_query

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when model validation fails."""
    pass


class Trip:
    """
    Trip model representing a travel itinerary.
    
    Attributes:
        id: Unique trip identifier
        name: Trip name
        description: Trip description
        start_date: Trip start date
        end_date: Trip end date
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at
        self.updated_at = updated_at
    
    def validate(self) -> None:
        """
        Validate trip data.
        
        Raises:
            ValidationError: If validation fails
        """
        if not self.name or not self.name.strip():
            raise ValidationError("Trip name is required")
        
        if len(self.name.strip()) > 255:
            raise ValidationError("Trip name must be 255 characters or less")
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start date must be before or equal to end date")
    
    def save(self) -> 'Trip':
        """
        Save trip to database (create or update).
        
        Returns:
            Updated Trip instance with id and timestamps
            
        Raises:
            ValidationError: If validation fails
            psycopg2.Error: If database operation fails
        """
        self.validate()
        
        if self.id is None:
            # Create new trip
            query = """
                INSERT INTO trips (name, description, start_date, end_date)
                VALUES (%s, %s, %s, %s)
                RETURNING id, created_at, updated_at
            """
            result = execute_query(
                query, 
                (self.name, self.description, self.start_date, self.end_date),
                fetch_one=True
            )
            self.id, self.created_at, self.updated_at = result
            logger.info(f"Created trip with id {self.id}")
        else:
            # Update existing trip
            query = """
                UPDATE trips 
                SET name = %s, description = %s, start_date = %s, end_date = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING updated_at
            """
            result = execute_query(
                query,
                (self.name, self.description, self.start_date, self.end_date, self.id),
                fetch_one=True
            )
            if result:
                self.updated_at = result[0]
                logger.info(f"Updated trip with id {self.id}")
            else:
                raise ValidationError(f"Trip with id {self.id} not found")
        
        return self
    
    def delete(self) -> bool:
        """
        Delete trip from database.
        
        Returns:
            True if trip was deleted, False if not found
            
        Raises:
            psycopg2.Error: If database operation fails
        """
        if self.id is None:
            return False
        
        rows_affected = execute_query(
            "DELETE FROM trips WHERE id = %s",
            (self.id,)
        )
        
        if rows_affected > 0:
            logger.info(f"Deleted trip with id {self.id}")
            return True
        else:
            logger.warning(f"Trip with id {self.id} not found for deletion")
            return False
    
    @classmethod
    def get_by_id(cls, trip_id: int) -> Optional['Trip']:
        """
        Get trip by ID.
        
        Args:
            trip_id: Trip ID
            
        Returns:
            Trip instance or None if not found
        """
        result = execute_query(
            "SELECT id, name, description, start_date, end_date, created_at, updated_at FROM trips WHERE id = %s",
            (trip_id,),
            fetch_one=True
        )
        
        if result:
            # result: (id, name, description, start_date, end_date, created_at, updated_at)
            # constructor: (name, description, start_date, end_date, id, created_at, updated_at)
            return cls(
                name=result[1],
                description=result[2], 
                start_date=result[3],
                end_date=result[4],
                id=result[0],
                created_at=result[5],
                updated_at=result[6]
            )
        return None
    
    @classmethod
    def get_all(cls) -> List['Trip']:
        """
        Get all trips.
        
        Returns:
            List of Trip instances
        """
        results = execute_query(
            "SELECT id, name, description, start_date, end_date, created_at, updated_at FROM trips ORDER BY created_at DESC",
            fetch_all=True
        )
        
        return [cls(
            name=result[1],
            description=result[2], 
            start_date=result[3],
            end_date=result[4],
            id=result[0],
            created_at=result[5],
            updated_at=result[6]
        ) for result in results]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trip to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Day:
    """
    Day model representing a day within a trip.
    
    Attributes:
        id: Unique day identifier
        trip_id: Foreign key to trip
        date: Day date
        day_number: Day number within trip
        created_at: Creation timestamp
    """
    
    def __init__(
        self,
        trip_id: int,
        date: date,
        day_number: int,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.trip_id = trip_id
        self.date = date
        self.day_number = day_number
        self.created_at = created_at
    
    def validate(self) -> None:
        """
        Validate day data.
        
        Raises:
            ValidationError: If validation fails
        """
        if not self.trip_id:
            raise ValidationError("Trip ID is required")
        
        if not self.date:
            raise ValidationError("Date is required")
        
        if not self.day_number or self.day_number < 1:
            raise ValidationError("Day number must be positive")
    
    def save(self) -> 'Day':
        """
        Save day to database (create or update).
        
        Returns:
            Updated Day instance with id and timestamps
            
        Raises:
            ValidationError: If validation fails
            psycopg2.Error: If database operation fails
        """
        self.validate()
        
        if self.id is None:
            # Create new day
            query = """
                INSERT INTO days (trip_id, date, day_number)
                VALUES (%s, %s, %s)
                RETURNING id, created_at
            """
            result = execute_query(
                query,
                (self.trip_id, self.date, self.day_number),
                fetch_one=True
            )
            self.id, self.created_at = result
            logger.info(f"Created day with id {self.id}")
        else:
            # Update existing day
            query = """
                UPDATE days 
                SET trip_id = %s, date = %s, day_number = %s
                WHERE id = %s
            """
            rows_affected = execute_query(
                query,
                (self.trip_id, self.date, self.day_number, self.id)
            )
            if rows_affected == 0:
                raise ValidationError(f"Day with id {self.id} not found")
            logger.info(f"Updated day with id {self.id}")
        
        return self
    
    def delete(self) -> bool:
        """
        Delete day from database.
        
        Returns:
            True if day was deleted, False if not found
        """
        if self.id is None:
            return False
        
        rows_affected = execute_query(
            "DELETE FROM days WHERE id = %s",
            (self.id,)
        )
        
        if rows_affected > 0:
            logger.info(f"Deleted day with id {self.id}")
            return True
        else:
            logger.warning(f"Day with id {self.id} not found for deletion")
            return False
    
    @classmethod
    def get_by_id(cls, day_id: int) -> Optional['Day']:
        """Get day by ID."""
        result = execute_query(
            "SELECT id, trip_id, date, day_number, created_at FROM days WHERE id = %s",
            (day_id,),
            fetch_one=True
        )
        
        if result:
            # result: (id, trip_id, date, day_number, created_at)
            # constructor: (trip_id, date, day_number, id, created_at)
            return cls(
                trip_id=result[1],
                date=result[2],
                day_number=result[3],
                id=result[0],
                created_at=result[4]
            )
        return None
    
    @classmethod
    def get_by_trip_id(cls, trip_id: int) -> List['Day']:
        """Get all days for a trip, ordered by day number."""
        results = execute_query(
            "SELECT id, trip_id, date, day_number, created_at FROM days WHERE trip_id = %s ORDER BY day_number",
            (trip_id,),
            fetch_all=True
        )
        
        return [cls(
            trip_id=result[1],
            date=result[2],
            day_number=result[3],
            id=result[0],
            created_at=result[4]
        ) for result in results]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert day to dictionary representation."""
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'date': self.date.isoformat() if self.date else None,
            'day_number': self.day_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Activity:
    """
    Activity model representing an activity within a day.
    
    Attributes:
        id: Unique activity identifier
        day_id: Foreign key to day
        name: Activity name
        description: Activity description
        start_time: Activity start time
        end_time: Activity end time
        order_index: Order within day for chronological sorting
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    def __init__(
        self,
        day_id: int,
        name: str,
        description: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        order_index: int = 0,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.day_id = day_id
        self.name = name
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.order_index = order_index
        self.created_at = created_at
        self.updated_at = updated_at
    
    def validate(self) -> None:
        """
        Validate activity data.
        
        Raises:
            ValidationError: If validation fails
        """
        if not self.day_id:
            raise ValidationError("Day ID is required")
        
        if not self.name or not self.name.strip():
            raise ValidationError("Activity name is required")
        
        if len(self.name.strip()) > 255:
            raise ValidationError("Activity name must be 255 characters or less")
        
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Start time must be before end time")
    
    def save(self) -> 'Activity':
        """
        Save activity to database (create or update).
        
        Returns:
            Updated Activity instance with id and timestamps
        """
        self.validate()
        
        if self.id is None:
            # Create new activity
            query = """
                INSERT INTO activities (day_id, name, description, start_time, end_time, order_index)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at, updated_at
            """
            result = execute_query(
                query,
                (self.day_id, self.name, self.description, self.start_time, self.end_time, self.order_index),
                fetch_one=True
            )
            self.id, self.created_at, self.updated_at = result
            logger.info(f"Created activity with id {self.id}")
        else:
            # Update existing activity
            query = """
                UPDATE activities 
                SET day_id = %s, name = %s, description = %s, start_time = %s, 
                    end_time = %s, order_index = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING updated_at
            """
            result = execute_query(
                query,
                (self.day_id, self.name, self.description, self.start_time, 
                 self.end_time, self.order_index, self.id),
                fetch_one=True
            )
            if result:
                self.updated_at = result[0]
                logger.info(f"Updated activity with id {self.id}")
            else:
                raise ValidationError(f"Activity with id {self.id} not found")
        
        return self
    
    def delete(self) -> bool:
        """Delete activity from database."""
        if self.id is None:
            return False
        
        rows_affected = execute_query(
            "DELETE FROM activities WHERE id = %s",
            (self.id,)
        )
        
        if rows_affected > 0:
            logger.info(f"Deleted activity with id {self.id}")
            return True
        else:
            logger.warning(f"Activity with id {self.id} not found for deletion")
            return False
    
    @classmethod
    def get_by_id(cls, activity_id: int) -> Optional['Activity']:
        """Get activity by ID."""
        result = execute_query(
            """SELECT id, day_id, name, description, start_time, end_time, 
               order_index, created_at, updated_at FROM activities WHERE id = %s""",
            (activity_id,),
            fetch_one=True
        )
        
        if result:
            # result: (id, day_id, name, description, start_time, end_time, order_index, created_at, updated_at)
            # constructor: (day_id, name, description, start_time, end_time, order_index, id, created_at, updated_at)
            return cls(
                day_id=result[1],
                name=result[2],
                description=result[3],
                start_time=result[4],
                end_time=result[5],
                order_index=result[6],
                id=result[0],
                created_at=result[7],
                updated_at=result[8]
            )
        return None
    
    @classmethod
    def get_by_day_id(cls, day_id: int) -> List['Activity']:
        """Get all activities for a day, ordered chronologically."""
        results = execute_query(
            """SELECT id, day_id, name, description, start_time, end_time, 
               order_index, created_at, updated_at FROM activities 
               WHERE day_id = %s ORDER BY start_time ASC NULLS LAST, order_index ASC""",
            (day_id,),
            fetch_all=True
        )
        
        return [cls(
            day_id=result[1],
            name=result[2],
            description=result[3],
            start_time=result[4],
            end_time=result[5],
            order_index=result[6],
            id=result[0],
            created_at=result[7],
            updated_at=result[8]
        ) for result in results]
    
    def update_order(self, new_order_index: int) -> 'Activity':
        """
        Update activity order index for reordering.
        
        Args:
            new_order_index: New order index
            
        Returns:
            Updated Activity instance
        """
        if self.id is None:
            raise ValidationError("Cannot update order of unsaved activity")
        
        self.order_index = new_order_index
        
        query = """
            UPDATE activities 
            SET order_index = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING updated_at
        """
        result = execute_query(query, (new_order_index, self.id), fetch_one=True)
        
        if result:
            self.updated_at = result[0]
            logger.info(f"Updated order for activity {self.id} to {new_order_index}")
        else:
            raise ValidationError(f"Activity with id {self.id} not found")
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to dictionary representation."""
        return {
            'id': self.id,
            'day_id': self.day_id,
            'name': self.name,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }