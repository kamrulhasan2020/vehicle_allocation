import motor.motor_asyncio

MONGO_URI = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

database = client.vehicle_allocation

allocations_collection = database.get_collection("allocations")
vehicles_collection = database.get_collection("vehicles")
