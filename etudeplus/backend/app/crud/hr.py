from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date

from app.models import Employee, Contract, LeaveRequest, Payslip
from app.schemas.hr import (
    EmployeeCreate, EmployeeUpdate,
    ContractCreate, ContractUpdate,
    LeaveRequestCreate, LeaveRequestUpdate,
    PayslipCreate, PayslipUpdate
)

# --- Employee ---
def get_employees(db: Session, tenant_id: UUID) -> List[Employee]:
    return db.query(Employee).filter(Employee.tenant_id == tenant_id).order_by(Employee.last_name).all()

def get_employee(db: Session, employee_id: UUID, tenant_id: UUID) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.id == employee_id, Employee.tenant_id == tenant_id).first()

def create_employee(db: Session, obj_in: EmployeeCreate, tenant_id: UUID) -> Employee:
    db_obj = Employee(
        **obj_in.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_employee(db: Session, employee_id: UUID, obj_in: EmployeeUpdate, tenant_id: UUID) -> Optional[Employee]:
    db_obj = get_employee(db, employee_id, tenant_id)
    if not db_obj:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_employee(db: Session, employee_id: UUID, tenant_id: UUID) -> bool:
    db_obj = get_employee(db, employee_id, tenant_id)
    if not db_obj:
        return False
    db.delete(db_obj)
    db.commit()
    return True

# --- Contract ---
def get_contracts(db: Session, tenant_id: UUID) -> List[Contract]:
    return db.query(Contract).filter(Contract.tenant_id == tenant_id).order_by(Contract.start_date.desc()).all()

def get_contract(db: Session, contract_id: UUID, tenant_id: UUID) -> Optional[Contract]:
    return db.query(Contract).filter(Contract.id == contract_id, Contract.tenant_id == tenant_id).first()

def create_contract(db: Session, obj_in: ContractCreate, tenant_id: UUID) -> Contract:
    if obj_in.is_current:
        # Reset others for this employee
        db.query(Contract).filter(
            Contract.tenant_id == tenant_id, 
            Contract.employee_id == obj_in.employee_id
        ).update({"is_current": False})
    
    db_obj = Contract(
        **obj_in.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_contract(db: Session, contract_id: UUID, obj_in: ContractUpdate, tenant_id: UUID) -> Optional[Contract]:
    db_obj = get_contract(db, contract_id, tenant_id)
    if not db_obj:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    if update_data.get("is_current"):
        db.query(Contract).filter(
            Contract.tenant_id == tenant_id, 
            Contract.employee_id == db_obj.employee_id,
            Contract.id != contract_id
        ).update({"is_current": False})
        
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_contract(db: Session, contract_id: UUID, tenant_id: UUID) -> bool:
    db_obj = get_contract(db, contract_id, tenant_id)
    if not db_obj:
        return False
    db.delete(db_obj)
    db.commit()
    return True

# --- Leave Request ---
def get_leave_requests(db: Session, tenant_id: UUID) -> List[LeaveRequest]:
    return db.query(LeaveRequest).filter(LeaveRequest.tenant_id == tenant_id).order_by(LeaveRequest.created_at.desc()).all()

def get_leave_request(db: Session, leave_id: UUID, tenant_id: UUID) -> Optional[LeaveRequest]:
    return db.query(LeaveRequest).filter(LeaveRequest.id == leave_id, LeaveRequest.tenant_id == tenant_id).first()

def create_leave_request(db: Session, obj_in: LeaveRequestCreate, tenant_id: UUID) -> LeaveRequest:
    db_obj = LeaveRequest(
        **obj_in.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_leave_status(db: Session, leave_id: UUID, obj_in: LeaveRequestUpdate, tenant_id: UUID) -> Optional[LeaveRequest]:
    db_obj = get_leave_request(db, leave_id, tenant_id)
    if not db_obj:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- Payslip ---
def get_payslips(db: Session, tenant_id: UUID) -> List[Payslip]:
    return db.query(Payslip).filter(Payslip.tenant_id == tenant_id).order_by(Payslip.period_year.desc(), Payslip.period_month.desc()).all()

def get_payslip(db: Session, payslip_id: UUID, tenant_id: UUID) -> Optional[Payslip]:
    return db.query(Payslip).filter(Payslip.id == payslip_id, Payslip.tenant_id == tenant_id).first()

def create_payslip(db: Session, obj_in: PayslipCreate, tenant_id: UUID) -> Payslip:
    db_obj = Payslip(
        **obj_in.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_payslip(db: Session, payslip_id: UUID, obj_in: PayslipUpdate, tenant_id: UUID) -> Optional[Payslip]:
    db_obj = get_payslip(db, payslip_id, tenant_id)
    if not db_obj:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_payslip(db: Session, payslip_id: UUID, tenant_id: UUID) -> bool:
    db_obj = get_payslip(db, payslip_id, tenant_id)
    if not db_obj:
        return False
    db.delete(db_obj)
    db.commit()
    return True

def get_last_employee_number(db: Session, tenant_id: UUID) -> Optional[str]:
    employee = db.query(Employee).filter(Employee.tenant_id == tenant_id).order_by(Employee.created_at.desc()).first()
    return employee.employee_number if employee else None


# --- Employee Statistics ---

def get_employee_statistics(db: Session, tenant_id: UUID) -> dict:
    """Get HR statistics for dashboard."""
    from sqlalchemy import func
    
    # Total employees
    total = db.query(func.count(Employee.id)).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_active == True
    ).scalar()
    
    # By department
    by_department = db.query(
        Employee.department,
        func.count(Employee.id).label('count')
    ).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_active == True,
        Employee.department.isnot(None)
    ).group_by(Employee.department).all()
    
    # By job title
    by_job_title = db.query(
        Employee.job_title,
        func.count(Employee.id).label('count')
    ).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_active == True,
        Employee.job_title.isnot(None)
    ).group_by(Employee.job_title).all()
    
    # Recent hires (last 30 days)
    from datetime import timedelta
    thirty_days_ago = date.today() - timedelta(days=30)
    recent_hires = db.query(func.count(Employee.id)).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_active == True,
        Employee.hire_date >= thirty_days_ago
    ).scalar()
    
    # Pending leave requests
    pending_leaves = db.query(func.count(LeaveRequest.id)).filter(
        LeaveRequest.tenant_id == tenant_id,
        LeaveRequest.status == 'pending'
    ).scalar()
    
    # Contracts expiring soon (next 60 days)
    sixty_days_later = date.today() + timedelta(days=60)
    expiring_contracts = db.query(func.count(Contract.id)).filter(
        Contract.tenant_id == tenant_id,
        Contract.is_current == True,
        Contract.end_date.isnot(None),
        Contract.end_date <= sixty_days_later
    ).scalar()
    
    return {
        'total_employees': total,
        'by_department': [{'department': r[0], 'count': r[1]} for r in by_department],
        'by_job_title': [{'job_title': r[0], 'count': r[1]} for r in by_job_title],
        'recent_hires': recent_hires,
        'pending_leave_requests': pending_leaves,
        'expiring_contracts': expiring_contracts,
    }


def get_employees_by_department(db: Session, tenant_id: UUID, department: str) -> List[Employee]:
    """Get employees filtered by department."""
    return db.query(Employee).filter(
        Employee.tenant_id == tenant_id,
        Employee.department == department,
        Employee.is_active == True
    ).order_by(Employee.last_name).all()


def search_employees(db: Session, tenant_id: UUID, query: str) -> List[Employee]:
    """Search employees by name, employee number, or email."""
    search_pattern = f"%{query}%"
    return db.query(Employee).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_active == True,
        (Employee.first_name.ilike(search_pattern) |
         Employee.last_name.ilike(search_pattern) |
         Employee.employee_number.ilike(search_pattern) |
         Employee.email.ilike(search_pattern))
    ).order_by(Employee.last_name).all()


# --- Leave Balance Management ---

def get_leave_balance(db: Session, employee_id: UUID, tenant_id: UUID, year: int = None) -> dict:
    """Calculate leave balance for an employee."""
    from datetime import datetime
    year = year or date.today().year
    
    employee = get_employee(db, employee_id, tenant_id)
    if not employee:
        return None
    
    # Default annual leave entitlement (can be customized per employee/contract)
    annual_entitlement = 30  # days
    
    # Get approved leaves for the year
    approved_leaves = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.tenant_id == tenant_id,
        LeaveRequest.status == 'approved',
        LeaveRequest.start_date >= date(year, 1, 1),
        LeaveRequest.end_date < date(year + 1, 1, 1)
    ).all()
    
    used_days = sum(leave.total_days for leave in approved_leaves)
    
    # Calculate pro-rated entitlement for new employees
    if employee.hire_date.year == year:
        months_worked = 12 - employee.hire_date.month + 1
        annual_entitlement = (annual_entitlement / 12) * months_worked
    
    return {
        'employee_id': employee_id,
        'year': year,
        'annual_entitlement': annual_entitlement,
        'used_days': used_days,
        'remaining_days': annual_entitlement - used_days,
    }


def get_team_on_leave(db: Session, tenant_id: UUID, target_date: date = None) -> List[dict]:
    """Get employees currently on leave."""
    target_date = target_date or date.today()
    
    leaves = db.query(LeaveRequest, Employee).join(
        Employee, LeaveRequest.employee_id == Employee.id
    ).filter(
        LeaveRequest.tenant_id == tenant_id,
        LeaveRequest.status == 'approved',
        LeaveRequest.start_date <= target_date,
        LeaveRequest.end_date >= target_date
    ).all()
    
    return [{
        'employee_id': leave.Employee.id,
        'employee_name': f"{leave.Employee.first_name} {leave.Employee.last_name}",
        'leave_type': leave.LeaveRequest.leave_type,
        'return_date': leave.LeaveRequest.end_date,
    } for leave in leaves]


# --- Salary Calculations ---

def calculate_payslip(
    db: Session,
    employee_id: UUID,
    tenant_id: UUID,
    month: int,
    year: int,
    bonus: float = 0,
    deductions: float = 0,
    overtime_hours: float = 0,
    overtime_rate: float = 1.25
) -> dict:
    """
    Calculate payslip details based on contract and attendance.
    Returns calculated values for payslip creation.
    """
    from datetime import timedelta
    
    # Get current contract
    contract = db.query(Contract).filter(
        Contract.employee_id == employee_id,
        Contract.tenant_id == tenant_id,
        Contract.is_current == True
    ).first()
    
    if not contract:
        raise ValueError("No active contract found for employee")
    
    # Base calculations
    base_salary = contract.gross_monthly_salary
    hourly_rate = base_salary / (contract.weekly_hours * 4.33)  # Average weeks per month
    
    # Overtime
    overtime_pay = overtime_hours * hourly_rate * overtime_rate
    
    # Gross salary
    gross_salary = base_salary + bonus + overtime_pay
    
    # Social contributions (example rates - adjust based on local laws)
    social_security_rate = 0.042  # 4.2%
    unemployment_rate = 0.007    # 0.7%
    retirement_rate = 0.06       # 6%
    
    social_security = gross_salary * social_security_rate
    unemployment = gross_salary * unemployment_rate
    retirement = gross_salary * retirement_rate
    
    # Total deductions
    total_deductions = social_security + unemployment + retirement + deductions
    
    # Taxable income (simplified)
    taxable_income = gross_salary - total_deductions
    
    # Income tax (progressive - simplified)
    if taxable_income <= 150000:
        income_tax = 0
    elif taxable_income <= 300000:
        income_tax = (taxable_income - 150000) * 0.10
    elif taxable_income <= 500000:
        income_tax = 15000 + (taxable_income - 300000) * 0.20
    else:
        income_tax = 55000 + (taxable_income - 500000) * 0.30
    
    # Net salary
    net_salary = gross_salary - total_deductions - income_tax
    
    return {
        'employee_id': employee_id,
        'month': month,
        'year': year,
        'base_salary': base_salary,
        'overtime_hours': overtime_hours,
        'overtime_pay': overtime_pay,
        'bonus': bonus,
        'gross_salary': gross_salary,
        'deductions': {
            'social_security': social_security,
            'unemployment': unemployment,
            'retirement': retirement,
            'other_deductions': deductions,
            'income_tax': income_tax,
            'total': total_deductions + income_tax,
        },
        'net_salary': net_salary,
        'currency': 'XAF',  # Default currency
    }


def generate_payslip_pdf(db: Session, payslip_id: UUID, tenant_id: UUID) -> str:
    """Generate PDF for a payslip and return the URL."""
    payslip = get_payslip(db, payslip_id, tenant_id)
    if not payslip:
        return None
    
    # Get employee details
    employee = get_employee(db, payslip.employee_id, tenant_id)
    
    # TODO: Implement actual PDF generation with reportlab or weasyprint
    # For now, return a placeholder URL
    pdf_url = f"/storage/payslips/{payslip_id}.pdf"
    
    # Update payslip with PDF URL
    payslip.pdf_url = pdf_url
    db.commit()
    
    return pdf_url


# --- Contract Management ---

def get_expiring_contracts(db: Session, tenant_id: UUID, days: int = 60) -> List[Contract]:
    """Get contracts expiring within specified days."""
    from datetime import timedelta
    
    end_date_threshold = date.today() + timedelta(days=days)
    
    return db.query(Contract).filter(
        Contract.tenant_id == tenant_id,
        Contract.is_current == True,
        Contract.end_date.isnot(None),
        Contract.end_date <= end_date_threshold,
        Contract.end_date >= date.today()
    ).order_by(Contract.end_date).all()


def renew_contract(
    db: Session,
    contract_id: UUID,
    tenant_id: UUID,
    new_end_date: date,
    new_salary: float = None,
    new_job_title: str = None
) -> Contract:
    """Renew an existing contract."""
    contract = get_contract(db, contract_id, tenant_id)
    if not contract:
        return None
    
    # Mark current contract as not current
    contract.is_current = False
    
    # Create new contract
    new_contract = Contract(
        contract_number=f"{contract.contract_number}-R",  # Add renewal suffix
        contract_type=contract.contract_type,
        start_date=contract.end_date + timedelta(days=1) if contract.end_date else date.today(),
        end_date=new_end_date,
        job_title=new_job_title or contract.job_title,
        gross_monthly_salary=new_salary or contract.gross_monthly_salary,
        weekly_hours=contract.weekly_hours,
        employee_id=contract.employee_id,
        tenant_id=tenant_id,
        is_current=True,
    )
    
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    
    return new_contract


# --- Bulk Operations ---

def bulk_create_employees(db: Session, employees_data: List[EmployeeCreate], tenant_id: UUID) -> List[Employee]:
    """Create multiple employees at once."""
    employees = []
    for data in employees_data:
        employee = Employee(**data.model_dump(), tenant_id=tenant_id)
        db.add(employee)
        employees.append(employee)
    
    db.commit()
    for emp in employees:
        db.refresh(emp)
    
    return employees


def export_employees_csv(db: Session, tenant_id: UUID) -> str:
    """Export employees to CSV format."""
    import csv
    import io
    
    employees = get_employees(db, tenant_id)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Employee Number', 'First Name', 'Last Name', 'Email', 'Phone',
        'Job Title', 'Department', 'Hire Date', 'Status'
    ])
    
    # Data
    for emp in employees:
        writer.writerow([
            emp.employee_number,
            emp.first_name,
            emp.last_name,
            emp.email or '',
            emp.phone or '',
            emp.job_title or '',
            emp.department or '',
            emp.hire_date,
            'Active' if emp.is_active else 'Inactive'
        ])
    
    return output.getvalue()
