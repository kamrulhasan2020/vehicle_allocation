from contextlib import asynccontextmanager

from fastapi import FastAPI
from typing import List

from .database import init_redis, close_redis
from .models import (
    AllocationModel,
    AllocationResponseModel,
    AllocationUpdateModel,
    FilterModel,
)
from .crud import (
    create_allocation,
    update_allocation,
    delete_allocation,
    get_allocation_history,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup: Initialize Redis
    await init_redis()
    yield  # The application runs after this point.

    # On shutdown: Close Redis connection
    await close_redis()


app = FastAPI(lifespan=lifespan)



@app.post("/allocate/")
async def allocate_vehicle(allocation: AllocationModel) -> str:
    allocation = await create_allocation(allocation)
    return allocation


@app.put("/allocate/{allocation_id}/", response_model=bool)
async def modify_allocation(allocation_id: str, update_data: AllocationUpdateModel):
    result = await update_allocation(allocation_id, update_data)
    return result


@app.delete("/allocate/{allocation_id}/", response_model=bool)
async def remove_allocation(allocation_id: str):
    result = await delete_allocation(allocation_id)
    return result


@app.post("/history/", response_model=List[AllocationResponseModel])
async def fetch_allocation_history(filters: FilterModel):
    history = await get_allocation_history(filters)
    return history
