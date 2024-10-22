import aioredis
import motor.motor_asyncio

# MongoDB connection URL
MONGO_URL = "mongodb://mongo:27017"
# Redis connection URL
REDIS_URL = "redis://redis:6379"

# Create an asynchronous MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# Access the 'vehicle_allocation' database from MongoDB
database = client.vehicle_allocation

# Access the 'allocations' collection within the database
allocations_collection = database.get_collection("allocations")

# Create an asynchronous Redis client with UTF-8 encoding and response decoding
redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
