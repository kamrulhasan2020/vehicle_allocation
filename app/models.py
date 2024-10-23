from pydantic import BaseModel, ConfigDict, Field, BeforeValidator
from datetime import date
from typing import Optional, Annotated, List

# Define a custom type for PyObjectId, which is a string validated before use.
PyObjectId = Annotated[str, BeforeValidator(str)]


class AllocationModel(BaseModel):
    """
    Model representing a vehicle allocation for an employee.

    Attributes:
    - employee_id (str): The ID of the employee to whom the vehicle is allocated.
    - vehicle_id (str): The ID of the vehicle being allocated.
    - allocation_date (date): The date of the allocation.
    """

    employee_id: str
    vehicle_id: str
    allocation_date: date


class AllocationResponseModel(AllocationModel):
    """
    Response model for vehicle allocation that includes an ID.

    Inherits from AllocationModel and adds an optional ID field.

    Attributes:
    - id (Optional[PyObjectId]): The unique identifier for the allocation.
    """

    model_config = ConfigDict(from_attributes=True)
    id: Optional[PyObjectId] = Field(alias="_id", default=None)


class PaginatedResponse(BaseModel):
    """
    Model for paginated responses containing a list of allocations.

    Attributes:
    - data (List[AllocationResponseModel]): List of allocation responses.
    - total (int): Total number of allocations.
    - skip (int): Number of records skipped for pagination.
    - limit (int): Number of records per page.
    - has_more (bool): Indicates if there are more records available.
    """

    data: List[AllocationResponseModel]
    total: int
    skip: int
    limit: int
    has_more: bool


class AllocationUpdateModel(BaseModel):
    """
    Model for updating vehicle allocation details.

    Attributes:
    - employee_id (Optional[str]): New employee ID, if updating.
    - allocation_date (Optional[date]): New allocation date, if updating.
    """

    employee_id: Optional[str] = None
    allocation_date: Optional[date] = None


class CreateResponseModel(BaseModel):
    """
    Response model for creating a new allocation.

    Attributes:
    - id (str): The unique identifier of the newly created allocation.
    """

    id: str
