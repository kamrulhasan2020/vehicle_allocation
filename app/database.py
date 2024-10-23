import aioredis
import motor.motor_asyncio

from app.utils import settings

# MongoDB and Redis URLs are dynamically loaded from environment variables
MONGO_URL = settings.MONGO_URL
REDIS_URL = settings.REDIS_URL

# Create an asynchronous MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# Access the 'vehicle_allocation' database from MongoDB
database = client.get_default_database()

# Access the 'allocations' collection within the database
allocations_collection = database.get_collection("allocations")

# Create an asynchronous Redis client with UTF-8 encoding and response decoding
redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
