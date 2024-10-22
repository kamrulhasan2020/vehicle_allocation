from datetime import date

from fastapi import FastAPI, Query
from typing import List

from .models import (
    AllocationModel,
    AllocationUpdateModel,
    PaginatedResponse,
    CreateResponseModel,
)
from .crud import (
    create_allocation,
    update_allocation,
    delete_allocation,
    get_allocation_history,
)


app = FastAPI()


@app.post("/allocate/", status_code=201, response_model=CreateResponseModel)
async def allocate_vehicle(allocation: AllocationModel):
    allocation = await create_allocation(allocation)
    return allocation


@app.patch("/allocate/{allocation_id}/", response_model=AllocationUpdateModel)
async def modify_allocation(allocation_id: str, update_data: AllocationUpdateModel):
    await update_allocation(allocation_id, update_data)
    return update_data


@app.delete("/allocate/{allocation_id}/", status_code=204)
async def remove_allocation(allocation_id: str):
    await delete_allocation(allocation_id)


# Get allocation history with filters
@app.get("/history/", response_model=PaginatedResponse)
async def fetch_allocation_history(
    employee_id: str = Query(None),
    vehicle_id: str = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
    skip: int = Query(0, ge=0),  # starting point for pagination
    limit: int = Query(10, ge=1),  # number of items per page
):
    history = await get_allocation_history(
        employee_id, vehicle_id, start_date, end_date, skip, limit
    )
    return history
