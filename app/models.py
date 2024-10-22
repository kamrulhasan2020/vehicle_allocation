from pydantic import BaseModel, ConfigDict, Field, BeforeValidator
from datetime import date
from typing import Optional, Annotated, List

PyObjectId = Annotated[str, BeforeValidator(str)]


class AllocationModel(BaseModel):
    employee_id: str
    vehicle_id: str
    allocation_date: date


class AllocationResponseModel(AllocationModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[PyObjectId] = Field(alias="_id", default=None)


class PaginatedResponse(BaseModel):
    data: List[AllocationResponseModel]
    total: int
    skip: int
    limit: int
    has_more: bool


class AllocationUpdateModel(BaseModel):
    employee_id: Optional[str] = None
    allocation_date: Optional[date] = None


class CreateResponseModel(BaseModel):
    id: str
