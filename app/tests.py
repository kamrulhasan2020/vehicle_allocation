from datetime import datetime, timezone, timedelta

import pytest
import pytest_asyncio
from bson import ObjectId
from httpx import AsyncClient, ASGITransport

from app.main import app
from .database import database as db, redis as redis_client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Clean up MongoDB and Redis databases before and after each test.
    """
    # Clean the MongoDB and Redis databases before the test
    await db.drop_collection("allocations")
    await redis_client.flushdb()

    yield  # Run the test
    # Clean up after the test
    await db.drop_collection("allocations")
    await redis_client.flushdb()


@pytest.mark.asyncio(scope="session")
async def test_create_allocation():
    """
    Test the creation of a vehicle allocation.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {
            "employee_id": "123",
            "vehicle_id": "ABCd",
            "allocation_date": "2024-10-26",
        }
        response = await client.post("/allocate/", json=payload)
        assert response.status_code == 201
        assert response.json() is not None


@pytest.mark.asyncio(scope="session")
async def test_get_allocation_history():
    """
    Test fetching the allocation history with filters.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        params = {
            "employee_id": "123",
            "vehicle_id": "ABC",
            "start_date": "2024-10-01",
            "end_date": "2024-10-23",
            "skip": 0,
            "limit": 10,
        }
        response = await client.get("/history/", params=params)
        assert response.status_code == 200
        assert "data" in response.json()


@pytest.mark.asyncio(scope="session")
async def test_delete_allocation():
    """
    Test the deletion of a vehicle allocation.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Arrange: Directly insert an allocation into MongoDB for testing
        allocation_data = {
            "employee_id": "emp123",
            "vehicle_id": "veh456",
            "allocation_date": datetime.combine(
                datetime.now(timezone.utc).date(), datetime.min.time()
            ),
        }
        # Insert the allocation into MongoDB
        allocations_collection = db.get_collection("allocations")
        insert_result = await allocations_collection.insert_one(allocation_data)
        allocation_id = str(insert_result.inserted_id)

        # Act: Delete the allocation using the DELETE endpoint
        delete_response = await client.delete(f"/allocation/{allocation_id}/")
        # Assert the deletion response
        # Allocation with Present date cant be deleted
        assert delete_response.status_code == 400

        allocation_data = {
            "employee_id": "emp123",
            "vehicle_id": "veh456",
            "allocation_date": datetime.combine(
                datetime.now(timezone.utc).date() + timedelta(days=2),
                datetime.min.time(),
            ),
        }
        # Insert the allocation into MongoDB
        allocations_collection = db.get_collection("allocations")
        insert_result = await allocations_collection.insert_one(allocation_data)
        allocation_id = str(insert_result.inserted_id)

        # Act: Delete the allocation using the DELETE endpoint
        delete_response = await client.delete(f"/allocation/{allocation_id}/")
        # Assert the deletion response
        # As allocation in future date allocation can be deleted
        assert delete_response.status_code == 204

        # Verify that the allocation is no longer in the database (MongoDB)
        allocation_in_db = await allocations_collection.find_one(
            {"_id": ObjectId(allocation_id)}
        )
        assert allocation_in_db is None

        # Verify that the allocation is also removed from Redis
        allocation_in_redis = await redis_client.get(
            f"vehicle:{allocation_data['vehicle_id']}"
            f":date:{allocation_data['allocation_date']}"
        )
        assert allocation_in_redis is None


@pytest.mark.asyncio(scope="session")
async def test_update_allocation():
    """
    Test the update of a vehicle allocation.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Arrange: Directly insert an allocation into MongoDB for testing
        allocation_data = {
            "employee_id": "emp123",
            "vehicle_id": "veh456",
            "allocation_date": datetime.combine(
                datetime.now(timezone.utc).date(), datetime.min.time()
            ),
        }

        # Insert the allocation into MongoDB
        allocations_collection = db.get_collection("allocations")
        insert_result = await allocations_collection.insert_one(allocation_data)
        allocation_id = str(insert_result.inserted_id)

        # Act: Attempt to update the allocation with a present date
        updated_data = {
            "employee_id": "emp789",
        }

        update_response = await client.patch(
            f"/allocation/{allocation_id}/", json=updated_data
        )

        # Assert the update response (should fail due to allocation date being present)
        assert update_response.status_code == 400

        # Now, update with a future date
        allocation_data = {
            "employee_id": "emp123",
            "vehicle_id": "veh456",
            "allocation_date": datetime.combine(
                datetime.now(timezone.utc).date() + timedelta(days=2),
                datetime.min.time(),
            ),
        }
        # Insert the allocation into MongoDB
        allocations_collection = db.get_collection("allocations")
        insert_result = await allocations_collection.insert_one(allocation_data)
        allocation_id = str(insert_result.inserted_id)

        # Act: Update the allocation using the PATCH endpoint
        update_response = await client.patch(
            f"/allocation/{allocation_id}/", json=updated_data
        )

        # Assert the update response
        assert update_response.status_code == 200

        # Verify that the allocation is updated in the database (MongoDB)
        updated_allocation = await allocations_collection.find_one(
            {"_id": ObjectId(allocation_id)}
        )
        assert updated_allocation["employee_id"] == updated_data["employee_id"]

        allocation_in_redis = await redis_client.get(
            f"vehicle:{allocation_data['vehicle_id']}"
            f":date:{allocation_data['allocation_date']}"
        )
        assert allocation_in_redis is None
