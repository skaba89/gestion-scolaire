from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.hr import (
    Employee, EmployeeCreate, EmployeeUpdate,
    Contract, ContractCreate, ContractUpdate,
    LeaveRequest, LeaveRequestCreate, LeaveRequestUpdate,
    Payslip, PayslipCreate, PayslipUpdate
)
from app.crud import hr as crud_hr

router = APIRouter()

# --- Employees ---

@router.get("/employees/")
def read_employees(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retrieve all employees for the tenant."""
    return crud_hr.get_employees(db, tenant_id=current_user.get("tenant_id"))

@router.get("/employees/statistics/")
def read_employee_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get HR statistics for dashboard."""
    return crud_hr.get_employee_statistics(db, tenant_id=current_user.get("tenant_id"))

@router.get("/employees/search/")
def search_employees(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Search employees by name, number, or email."""
    return crud_hr.search_employees(db, tenant_id=current_user.get("tenant_id"), query=q)

@router.get("/employees/department/{department}/")
def read_employees_by_department(
    department: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get employees filtered by department."""
    return crud_hr.get_employees_by_department(
        db, tenant_id=current_user.get("tenant_id"), department=department
    )

@router.post("/employees/", response_model=Employee)
def create_employee(
    *,
    db: Session = Depends(get_db),
    obj_in: EmployeeCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new employee."""
    return crud_hr.create_employee(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))

@router.get("/employees/{employee_id}/", response_model=Employee)
def read_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific employee."""
    employee = crud_hr.get_employee(db, employee_id=employee_id, tenant_id=current_user.get("tenant_id"))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.put("/employees/{employee_id}/", response_model=Employee)
def update_employee(
    *,
    db: Session = Depends(get_db),
    employee_id: UUID,
    obj_in: EmployeeUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an employee."""
    employee = crud_hr.update_employee(db, employee_id=employee_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.delete("/employees/{employee_id}/")
def delete_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete an employee."""
    success = crud_hr.delete_employee(db, employee_id=employee_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"status": "success"}

@router.get("/employees/{employee_id}/leave-balance/")
def read_leave_balance(
    employee_id: UUID,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get leave balance for an employee."""
    balance = crud_hr.get_leave_balance(db, employee_id=employee_id, tenant_id=current_user.get("tenant_id"), year=year)
    if not balance:
        raise HTTPException(status_code=404, detail="Employee not found")
    return balance

@router.get("/employees/export/csv/")
def export_employees(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Export employees to CSV."""
    csv_data = crud_hr.export_employees_csv(db, tenant_id=current_user.get("tenant_id"))
    from fastapi.responses import Response
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"}
    )

# --- Contracts ---

@router.get("/contracts/", response_model=List[Contract])
def read_contracts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return crud_hr.get_contracts(db, tenant_id=current_user.get("tenant_id"))

@router.post("/contracts/", response_model=Contract)
def create_contract(
    *,
    db: Session = Depends(get_db),
    obj_in: ContractCreate,
    current_user: dict = Depends(get_current_user),
):
    return crud_hr.create_contract(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))

@router.put("/contracts/{contract_id}/", response_model=Contract)
def update_contract(
    *,
    db: Session = Depends(get_db),
    contract_id: UUID,
    obj_in: ContractUpdate,
    current_user: dict = Depends(get_current_user),
):
    contract = crud_hr.update_contract(db, contract_id=contract_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.delete("/contracts/{contract_id}/")
def delete_contract(
    contract_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    success = crud_hr.delete_contract(db, contract_id=contract_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {"status": "success"}

# --- Leave Requests ---

@router.get("/leave-requests/", response_model=List[LeaveRequest])
def read_leave_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return crud_hr.get_leave_requests(db, tenant_id=current_user.get("tenant_id"))

@router.post("/leave-requests/", response_model=LeaveRequest)
def create_leave_request(
    *,
    db: Session = Depends(get_db),
    obj_in: LeaveRequestCreate,
    current_user: dict = Depends(get_current_user),
):
    return crud_hr.create_leave_request(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))

@router.put("/leave-requests/{leave_id}/", response_model=LeaveRequest)
def update_leave_status(
    *,
    db: Session = Depends(get_db),
    leave_id: UUID,
    obj_in: LeaveRequestUpdate,
    current_user: dict = Depends(get_current_user),
):
    leave = crud_hr.update_leave_status(db, leave_id=leave_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave

# --- Payslips ---

@router.get("/payslips/", response_model=List[Payslip])
def read_payslips(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return crud_hr.get_payslips(db, tenant_id=current_user.get("tenant_id"))

@router.post("/payslips/", response_model=Payslip)
def create_payslip(
    *,
    db: Session = Depends(get_db),
    obj_in: PayslipCreate,
    current_user: dict = Depends(get_current_user),
):
    return crud_hr.create_payslip(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))

@router.delete("/payslips/{payslip_id}/")
def delete_payslip(
    payslip_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    success = crud_hr.delete_payslip(db, payslip_id=payslip_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Payslip not found")
    return {"status": "success"}

@router.post("/payslips/calculate/")
def calculate_payslip_endpoint(
    employee_id: UUID,
    month: int,
    year: int,
    bonus: float = 0,
    deductions: float = 0,
    overtime_hours: float = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Calculate payslip values before creation."""
    try:
        return crud_hr.calculate_payslip(
            db,
            employee_id=employee_id,
            tenant_id=current_user.get("tenant_id"),
            month=month,
            year=year,
            bonus=bonus,
            deductions=deductions,
            overtime_hours=overtime_hours
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/payslips/{payslip_id}/pdf/")
def generate_payslip_pdf_endpoint(
    payslip_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Generate and get PDF for a payslip."""
    pdf_url = crud_hr.generate_payslip_pdf(db, payslip_id=payslip_id, tenant_id=current_user.get("tenant_id"))
    if not pdf_url:
        raise HTTPException(status_code=404, detail="Payslip not found")
    return {"pdf_url": pdf_url}

# --- Additional Endpoints ---

@router.get("/contracts/expiring/")
def get_expiring_contracts(
    days: int = Query(60, description="Days ahead to check"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get contracts expiring within specified days."""
    return crud_hr.get_expiring_contracts(db, tenant_id=current_user.get("tenant_id"), days=days)

@router.post("/contracts/{contract_id}/renew/")
def renew_contract_endpoint(
    contract_id: UUID,
    new_end_date: date,
    new_salary: Optional[float] = None,
    new_job_title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Renew an existing contract."""
    contract = crud_hr.renew_contract(
        db,
        contract_id=contract_id,
        tenant_id=current_user.get("tenant_id"),
        new_end_date=new_end_date,
        new_salary=new_salary,
        new_job_title=new_job_title
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.get("/leave-requests/team-on-leave/")
def get_team_on_leave(
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get employees currently on leave."""
    return crud_hr.get_team_on_leave(db, tenant_id=current_user.get("tenant_id"), target_date=target_date)

@router.get("/last-employee-number/")
def read_last_employee_number(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get the last employee number for the tenant."""
    return crud_hr.get_last_employee_number(db, tenant_id=current_user.get("tenant_id"))
