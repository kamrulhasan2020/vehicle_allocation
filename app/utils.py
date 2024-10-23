import json
from datetime import datetime
from bson import ObjectId
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URL: str
    REDIS_URL: str

    class Config:
        env_file = ".env"


settings = Settings()


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that extends the default JSONEncoder to handle
    additional types, specifically ObjectId and datetime.

    This encoder converts:
    - ObjectId to its string representation.
    - datetime to its ISO 8601 string format.
    """

    def default(self, obj):
        """
        Override the default method to provide custom serialization for
        unsupported types.

        Parameters:
        - obj: The object to serialize.

        Returns:
        - str: The string representation of ObjectId or ISO format of datetime.
        - super: Calls the default method for all other types.
        """
        if isinstance(obj, ObjectId):
            # Convert ObjectId to string for JSON serialization
            return str(obj)
        if isinstance(obj, datetime):
            # Convert datetime to ISO 8601 string format for JSON serialization
            return obj.isoformat()
        # Call the default method for all other objects
        return super().default(obj)
