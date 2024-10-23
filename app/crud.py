import json
from datetime import date, datetime, timezone
from fastapi import HTTPException
from bson import ObjectId

from .database import allocations_collection, redis
from .models import (
    AllocationModel,
    AllocationUpdateModel,
    PaginatedResponse,
    CreateResponseModel,
)
from .utils import CustomJSONEncoder


# Helper to retrieve allocation by vehicle and date
async def get_allocation_by_vehicle_date(vehicle_id: str, allocation_date: date):
    """
    Retrieve allocation by vehicle ID and allocation date, checking the cache first.

    Parameters:
    - vehicle_id (str): The ID of the vehicle.
    - allocation_date (date): The date of the allocation.

    Returns:
    - dict: The allocation details or None if not found.
    """
    # Create cache key
    cache_key = f"vehicle:{vehicle_id}:date:{allocation_date}"

    # Check in Redis cache first
    cached_allocation = await redis.get(cache_key)
    if cached_allocation:
        return json.loads(cached_allocation)

    allocation = await allocations_collection.find_one(
        {"vehicle_id": vehicle_id, "allocation_date": allocation_date}
    )
    # Cache the result in Redis
    if allocation:
        await redis.set(
            cache_key, json.dumps(allocation, cls=CustomJSONEncoder), ex=3600
        )  # Set cache expiry for 1 hour
        return allocation


# Create allocation
async def create_allocation(allocation: AllocationModel) -> CreateResponseModel:
    """
    Create a new vehicle allocation if it doesn't already exist for the given date.

    Parameters:
    - allocation (AllocationModel): The allocation details to create.

    Returns:
    - CreateResponseModel: The response model containing the ID of the new allocation.

    Raises:
    - HTTPException: If the vehicle is already allocated for the date.
    """
    existing_allocation = await get_allocation_by_vehicle_date(
        allocation.vehicle_id,
        datetime.combine(allocation.allocation_date, datetime.min.time()),
    )
    if existing_allocation:
        raise HTTPException(
            status_code=400, detail="Vehicle already allocated for this date"
        )

    new_allocation = allocation.model_dump()
    new_allocation["allocation_date"] = datetime.combine(
        new_allocation["allocation_date"], datetime.min.time()
    )
    result = await allocations_collection.insert_one(new_allocation)
    # Invalidate Redis cache for this vehicle and date
    cache_key = f"vehicle:{allocation.vehicle_id}:date:{allocation.allocation_date}"
    await redis.delete(cache_key)
    return CreateResponseModel(id=str(result.inserted_id))


# Update allocation (only before the allocation date)
async def update_allocation(
    allocation_id: str, update_data: AllocationUpdateModel
) -> None:
    """
    Update an existing vehicle allocation.

    Parameters:
    - allocation_id (str): The ID of the allocation to update.
    - update_data (AllocationUpdateModel): The updated allocation details.

    Raises:
    - HTTPException: If the allocation does not exist or if trying to update a past allocation.
    """
    allocation = await allocations_collection.find_one({"_id": ObjectId(allocation_id)})
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")

    if allocation["allocation_date"] <= datetime.combine(
        datetime.now(timezone.utc).date(), datetime.min.time()
    ):
        raise HTTPException(
            status_code=400, detail="Cannot update past or current date allocations"
        )

    update_data = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_data.get("allocation_date", None):
        update_data["allocation_date"] = datetime.combine(
            update_data["allocation_date"], datetime.min.time()
        )

    if update_data:
        await allocations_collection.update_one(
            {"_id": ObjectId(allocation_id)}, {"$set": update_data}
        )
    # Invalidate Redis cache for the old and new dates
    old_cache_key = (
        f"vehicle:{allocation['vehicle_id']}:date:{allocation['allocation_date']}"
    )
    await redis.delete(old_cache_key)
    if "allocation_date" in update_data:
        new_cache_key = (
            f"vehicle:{allocation['vehicle_id']}:date:{update_data['allocation_date']}"
        )
        await redis.delete(new_cache_key)


# Delete allocation (only before the allocation date)
async def delete_allocation(allocation_id: str) -> None:
    """
    Delete an existing vehicle allocation.

    Parameters:
    - allocation_id (str): The ID of the allocation to delete.

    Raises:
    - HTTPException: If the allocation does not exist or if trying to delete a past allocation.
    """
    allocation = await allocations_collection.find_one({"_id": ObjectId(allocation_id)})
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")

    if allocation["allocation_date"] <= datetime.combine(
        datetime.now(timezone.utc).date(), datetime.min.time()
    ):
        raise HTTPException(
            status_code=400, detail="Cannot delete past or current date allocations"
        )

    await allocations_collection.delete_one({"_id": ObjectId(allocation_id)})
    # Invalidate Redis cache for the allocation date
    cache_key = (
        f"vehicle:{allocation['vehicle_id']}:date:{allocation['allocation_date']}"
    )
    await redis.delete(cache_key)


async def get_allocation_history(
    employee_id: str = None,
    vehicle_id: str = None,
    start_date: date = None,
    end_date: date = None,
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieve allocation history based on provided filters.

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
    query = {}
    if employee_id:
        query["employee_id"] = employee_id
    if vehicle_id:
        query["vehicle_id"] = vehicle_id
    if start_date and end_date:
        query["allocation_date"] = {
            "$gte": datetime.combine(start_date, datetime.min.time()),
            "$lte": datetime.combine(end_date, datetime.min.time()),
        }
    elif start_date:
        query["allocation_date"] = {"$gte": start_date}
    elif end_date:
        query["allocation_date"] = {"$lte": end_date}

    # Use aggregation to count and fetch results
    pipeline = [
        {"$match": query},  # Filter based on query
        {
            "$facet": {  # Use facet to separate counting and fetching
                "count": [{"$count": "total"}],  # Count total matching documents
                "data": [{"$skip": skip}, {"$limit": limit}],  # Paginate results
            }
        },
    ]

    result = await allocations_collection.aggregate(pipeline).to_list(length=None)

    # Extract total count and data
    total_count = result[0]["count"][0]["total"] if result and result[0]["count"] else 0
    history = result[0]["data"]
    # Determine if there's a next page
    has_more = (skip + limit) < total_count

    return PaginatedResponse(
        data=history, total=total_count, skip=skip, limit=limit, has_more=has_more
    )
