from fastapi import FastAPI

app = FastAPI(title="Vehicle Allocation System", description="API for managing vehicle allocations for employees", version="1.0")

@app.get("/")
async def hello():
    return {"response": "Hi"}
