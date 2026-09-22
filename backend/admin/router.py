from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from fastapi import APIRouter, Depends, HTTPException, status, Query

from db.session import get_db
from models import (
    Complaint, Category, Department, User, Citizen, Admin,
    ComplaintStatus, Vote, ComplaintStatusHistory
)
from schemas import (
    ComplaintResponse, ComplaintListResponse, CategoryCreate, CategoryResponse,
    DepartmentCreate, DepartmentResponse
)
from common.auth import get_current_active_user, require_admin
from common.exceptions import NotFoundException, ValidationException

router = APIRouter(prefix="/api/admin", tags=["admin"])


# Dashboard KPIs
@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard KPI statistics"""
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    # Total open complaints
    open_statuses = [ComplaintStatus.PENDING, ComplaintStatus.WORKING]
    open_count = db.query(Complaint).filter(Complaint.status.in_(open_statuses)).count()
    
    # Resolved this week
    resolved_this_week = db.query(Complaint).filter(
        Complaint.status == ComplaintStatus.COMPLETED,
        Complaint.resolved_at >= week_ago
    ).count()
    
    # Avg resolution time (days)
    resolved_complaints = db.query(Complaint).filter(
        Complaint.status == ComplaintStatus.COMPLETED,
        Complaint.resolved_at.isnot(None)
    ).all()
    
    avg_resolution_days = 0
    if resolved_complaints:
        total_days = sum((c.resolved_at - c.created_at).total_seconds() / 86400 for c in resolved_complaints)
        avg_resolution_days = round(total_days / len(resolved_complaints), 1)
    
    # By category
    by_category = db.query(
        Category.name,
        func.count(Complaint.id)
    ).join(Complaint).group_by(Category.name).all()
    
    # By status
    by_status = db.query(
        Complaint.status,
        func.count(Complaint.id)
    ).group_by(Complaint.status).all()
    
    # By department
    by_department = db.query(
        Department.display_name,
        func.count(Complaint.id)
    ).outerjoin(Complaint).group_by(Department.display_name).all()
    
    return {
        "open_complaints": open_count,
        "resolved_this_week": resolved_this_week,
        "avg_resolution_days": avg_resolution_days,
        "by_category": [{"category": c, "count": n} for c, n in by_category],
        "by_status": [{"status": s.value, "count": n} for s, n in by_status],
        "by_department": [{"department": d or "Unassigned", "count": n} for d, n in by_department],
    }


@router.get("/complaints", response_model=ComplaintListResponse)
async def list_all_complaints(
    page: int = 1,
    page_size: int = 50,
    status_filter: Optional[ComplaintStatus] = None,
    category_id: Optional[int] = None,
    department_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "upvote_count",
    sort_order: str = "desc",
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all complaints with advanced filtering and sorting"""
    query = db.query(Complaint)
    
    if status_filter:
        query = query.filter(Complaint.status == status_filter)
    if category_id:
        query = query.filter(Complaint.category_id == category_id)
    if department_id:
        query = query.filter(Complaint.department_id == department_id)
    if search:
        query = query.filter(Complaint.description.ilike(f"%{search}%"))
    
    # Sorting
    if sort_by == "upvote_count":
        sort_column = Complaint.upvote_count
    elif sort_by == "created_at":
        sort_column = Complaint.created_at
    else:
        sort_column = Complaint.upvote_count

    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    total = query.count()
    complaints = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return ComplaintListResponse(
        complaints=complaints,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint_detail(
    complaint_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get full complaint detail with history"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise NotFoundException("Complaint not found")
    return complaint


@router.put("/complaints/{complaint_id}/assign")
async def assign_complaint(
    complaint_id: int,
    department_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign complaint to department"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise NotFoundException("Complaint not found")
    
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise NotFoundException("Department not found")
    
    complaint.department_id = department_id
    if not complaint.assigned_at:
        complaint.assigned_at = datetime.utcnow()
    complaint.updated_at = datetime.utcnow()
    
    # Record history
    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        previous_status=complaint.status,
        new_status=complaint.status,
        changed_by=current_user.id,
        notes=f"Assigned to {department.display_name}"
    )
    db.add(history)
    
    db.commit()
    
    return {"message": "Complaint assigned successfully", "complaint": complaint}


# Category management
@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new complaint category"""
    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all categories"""
    return db.query(Category).filter(Category.is_active == True).all()


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundException("Category not found")
    
    for key, value in category_data.model_dump().items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Deactivate category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundException("Category not found")
    
    category.is_active = False
    db.commit()
    return {"message": "Category deactivated"}


# Department management
@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_data: DepartmentCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new department"""
    department = Department(**dept_data.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.get("/departments", response_model=List[DepartmentResponse])
async def list_departments(
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all departments"""
    return db.query(Department).filter(Department.is_active == True).all()


# Reports
@router.get("/reports/resolution-time-trend")
async def get_resolution_time_trend(
    days: int = 30,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get resolution time trend over specified days"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily resolution counts and avg time
    results = db.query(
        func.date(Complaint.resolved_at).label('date'),
        func.count(Complaint.id).label('count'),
        func.avg(
            func.extract('epoch', Complaint.resolved_at - Complaint.created_at) / 86400
        ).label('avg_days')
    ).filter(
        Complaint.status == ComplaintStatus.COMPLETED,
        Complaint.resolved_at >= start_date
    ).group_by(func.date(Complaint.resolved_at)).all()
    
    return [
        {"date": str(r.date), "resolved_count": r.count, "avg_resolution_days": round(r.avg_days or 0, 1)}
        for r in results
    ]


@router.get("/reports/complaints-by-category")
async def get_complaints_by_category(
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get complaint distribution by category"""
    results = db.query(
        Category.name,
        Category.display_name,
        func.count(Complaint.id)
    ).outerjoin(Complaint).group_by(Category.id).all()
    
    return [
        {"category": c, "display_name": d, "count": n}
        for c, d, n in results
    ]


@router.get("/reports/complaints-by-department")
async def get_complaints_by_department(
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get complaint distribution by department"""
    results = db.query(
        Department.display_name,
        func.count(Complaint.id)
    ).outerjoin(Complaint).group_by(Department.id).all()
    
    return [
        {"department": d or "Unassigned", "count": n}
        for d, n in results
    ]