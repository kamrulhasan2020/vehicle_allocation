from pydantic import BaseModel
from datetime import date
from typing import Optional

class AllocationModel(BaseModel):
    employee_id: int
    vehicle_id: int
    driver_id: int
    allocation_date: date

class AllocationUpdateModel(BaseModel):
    allocation_date: Optional[date] = None

class FilterModel(BaseModel):
    employee_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
