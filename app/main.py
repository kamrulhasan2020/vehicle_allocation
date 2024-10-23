from datetime import date
from fastapi import FastAPI, Query

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

# Create an instance of the FastAPI application
app = FastAPI()


@app.post("/allocate/", status_code=201, response_model=CreateResponseModel)
async def allocate_vehicle(allocation: AllocationModel):
    """
    Allocate a vehicle to an employee.

    Parameters:
    - allocation (AllocationModel): The allocation details provided in the request body.

    Returns:
    - CreateResponseModel: The response model containing the ID of the newly created allocation.
    """
    allocation = await create_allocation(allocation)
    return allocation


@app.patch("/allocation/{allocation_id}/", response_model=AllocationUpdateModel)
async def modify_allocation(allocation_id: str, update_data: AllocationUpdateModel):
    """
    Modify an existing vehicle allocation.

    Parameters:
    - allocation_id (str): The ID of the allocation to modify.
    - update_data (AllocationUpdateModel): The updated allocation details.

    Returns:
    - AllocationUpdateModel: The updated allocation details.
    """
    await update_allocation(allocation_id, update_data)
    return update_data


@app.delete("/allocation/{allocation_id}/", status_code=204)
async def remove_allocation(allocation_id: str):
    """
    Remove a vehicle allocation.

    Parameters:
    - allocation_id (str): The ID of the allocation to remove.

    Returns:
    - None: A successful deletion returns no content.
    """
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
    """
    Fetch the allocation history with optional filters.

    Parameters:
    - employee_id (str, optional): Filter by employee ID.
    - vehicle_id (str, optional): Filter by vehicle ID.
    - start_date (date, optional): Filter for allocations on or after this date.
    - end_date (date, optional): Filter for allocations on or before this date.
    - skip (int, optional): Number of records to skip for pagination (default is 0).
    - limit (int, optional): Maximum number of records to return (default is 10).

    Returns:
    - PaginatedResponse: Contains the allocation history and pagination info.
    """
    history = await get_allocation_history(
        employee_id, vehicle_id, start_date, end_date, skip, limit
    )
    return history
