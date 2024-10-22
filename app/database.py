import aioredis
import motor.motor_asyncio

MONGO_URI = "mongodb://mongo:27017"
REDIS_URL = "redis://redis:6379"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

database = client.vehicle_allocation

allocations_collection = database.get_collection("allocations")
vehicles_collection = database.get_collection("vehicles")
redis = aioredis.from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )

