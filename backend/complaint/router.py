from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse

from db.session import get_db
from models import (
    Complaint, Category, Department, 
    ComplaintStatus, Citizen, Vote
)
from schemas import (
    ComplaintCreate, ComplaintUpdate, ComplaintResponse, 
    ComplaintListResponse, CategoryResponse, VoteCreate, VoteResponse
)
from common.auth import get_current_active_user, require_admin, require_department, require_citizen
from common.exceptions import NotFoundException, ValidationException, ForbiddenException

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    description: str = Form(...),
    category_id: int = Form(...),
    location: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    evidence_files: List[UploadFile] = File(default=[]),
    current_user = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    """Submit a new complaint with location and optional evidence"""
    # Validate category
    category = db.query(Category).filter(Category.id == category_id, Category.is_active == True).first()
    if not category:
        raise NotFoundException("Category not found or inactive")
    
    # Handle evidence uploads (mock - in production upload to S3/cloud storage)
    evidence_urls = []
    for file in evidence_files:
        if file.content_type and file.content_type.startswith("image/"):
            # Mock URL - replace with actual upload
            evidence_urls.append(f"/uploads/{file.filename}")
    
    # Get citizen profile
    citizen = db.query(Citizen).filter(Citizen.user_id == current_user.id).first()
    if not citizen:
        raise NotFoundException("Citizen profile not found")
    
    # Create complaint
    complaint = Complaint(
        citizen_id=citizen.id,
        category_id=category_id,
        location=location,
        latitude=latitude,
        longitude=longitude,
        description=description,
        evidence_urls=evidence_urls,
        status=ComplaintStatus.PENDING,
        created_at=datetime.utcnow()
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    
    return complaint


@router.get("", response_model=ComplaintListResponse)
async def list_complaints(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[ComplaintStatus] = None,
    category_id: Optional[int] = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List complaints with filters (citizens see only their own)"""
    query = db.query(Complaint)
    
    if current_user.role.value == "citizen":
        citizen = db.query(Citizen).filter(Citizen.user_id == current_user.id).first()
        if citizen:
            query = query.filter(Complaint.citizen_id == citizen.id)
        else:
            return ComplaintListResponse(complaints=[], total=0, page=page, page_size=page_size)
    elif current_user.role.value == "department":
        from models import Admin
        dept_user = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if dept_user and dept_user.department_id:
            query = query.filter(Complaint.department_id == dept_user.department_id)
    
    if status_filter:
        query = query.filter(Complaint.status == status_filter)
    if category_id:
        query = query.filter(Complaint.category_id == category_id)
    
    total = query.count()
    # Prioritize based on upvote count (descending) then creation date
    complaints = query.order_by(desc(Complaint.upvote_count), desc(Complaint.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return ComplaintListResponse(
        complaints=complaints,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/public", response_model=ComplaintListResponse)
async def list_public_complaints(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List complaints for public feed, sorted by upvotes"""
    query = db.query(Complaint)
    total = query.count()
    complaints = query.order_by(desc(Complaint.upvote_count), desc(Complaint.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return ComplaintListResponse(
        complaints=complaints,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get complaint details"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise NotFoundException("Complaint not found")
    
    # Allow public view for everyone
    return complaint


@router.put("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: int,
    update_data: ComplaintUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update complaint (admin/dept can update status/department)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise NotFoundException("Complaint not found")
    
    # Check permissions
    if current_user.role.value == "citizen":
        raise ForbiddenException("Citizens cannot update complaints after submission")
    
    elif current_user.role.value in ["admin", "department"]:
        if current_user.role.value == "department":
            from models import Admin
            dept_user = db.query(Admin).filter(Admin.user_id == current_user.id).first()
            if not dept_user or complaint.department_id != dept_user.department_id:
                raise ForbiddenException("Not authorized to update this complaint")
        
        # Admin/department can update status, department
        if update_data.status is not None:
            old_status = complaint.status
            complaint.status = update_data.status
            
            # Record status history
            from models import ComplaintStatusHistory
            history = ComplaintStatusHistory(
                complaint_id=complaint.id,
                previous_status=old_status,
                new_status=update_data.status,
                changed_by=current_user.id
            )
            db.add(history)
            
            # Update timestamps
            if update_data.status == ComplaintStatus.WORKING and not complaint.started_at:
                complaint.started_at = datetime.utcnow()
            elif update_data.status == ComplaintStatus.COMPLETED and not complaint.resolved_at:
                complaint.resolved_at = datetime.utcnow()
        
        # Admin can update department
        if update_data.department_id is not None and current_user.role.value == "admin":
            complaint.department_id = update_data.department_id
            if not complaint.assigned_at:
                complaint.assigned_at = datetime.utcnow()
    
    complaint.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(complaint)
    
    return complaint


@router.post("/{complaint_id}/upvote", response_model=VoteResponse)
async def upvote_complaint(
    complaint_id: int,
    current_user = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    """Upvote a complaint"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise NotFoundException("Complaint not found")
    
    citizen = db.query(Citizen).filter(Citizen.user_id == current_user.id).first()
    if not citizen:
        raise NotFoundException("Citizen profile not found")
    
    # Check if already voted
    existing_vote = db.query(Vote).filter(
        Vote.citizen_id == citizen.id,
        Vote.complaint_id == complaint_id
    ).first()
    
    if existing_vote:
        raise ValidationException("Already voted on this complaint")
    
    # Create vote
    vote = Vote(citizen_id=citizen.id, complaint_id=complaint_id)
    db.add(vote)
    
    # Update complaint upvote count
    complaint.upvote_count += 1
    
    db.commit()
    db.refresh(vote)
    
    return vote


@router.delete("/{complaint_id}/upvote")
async def remove_upvote(
    complaint_id: int,
    current_user = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    """Remove upvote from a complaint"""
    citizen = db.query(Citizen).filter(Citizen.user_id == current_user.id).first()
    if not citizen:
        raise NotFoundException("Citizen profile not found")
    
    vote = db.query(Vote).filter(
        Vote.citizen_id == citizen.id,
        Vote.complaint_id == complaint_id
    ).first()
    
    if not vote:
        raise NotFoundException("Vote not found")
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint:
        complaint.upvote_count = max(0, complaint.upvote_count - 1)
    
    db.delete(vote)
    db.commit()
    
    return {"message": "Upvote removed"}