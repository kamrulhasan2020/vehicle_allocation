from datetime import date

from fastapi import FastAPI, Query
from typing import List

from .models import (
    AllocationModel,
    AllocationResponseModel,
    AllocationUpdateModel,
)
from .crud import (
    create_allocation,
    update_allocation,
    delete_allocation,
    get_allocation_history,
)


app = FastAPI()


@app.post("/allocate/")
async def allocate_vehicle(allocation: AllocationModel) -> str:
    allocation = await create_allocation(allocation)
    return allocation


@app.patch("/allocate/{allocation_id}/", response_model=bool)
async def modify_allocation(allocation_id: str, update_data: AllocationUpdateModel):
    result = await update_allocation(allocation_id, update_data)
    return result


@app.delete("/allocate/{allocation_id}/", response_model=bool)
async def remove_allocation(allocation_id: str):
    result = await delete_allocation(allocation_id)
    return result


# Get allocation history with filters
@app.get("/history/", response_model=List[AllocationResponseModel])
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
