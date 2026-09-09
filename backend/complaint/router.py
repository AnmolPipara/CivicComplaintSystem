from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse

from db.session import get_db
from models import (
    Complaint, Category, Location, Department, 
    ComplaintStatus, PriorityLevel, Citizen, Vote, Notification, NotificationChannel
)
from schemas import (
    ComplaintCreate, ComplaintUpdate, ComplaintResponse, 
    ComplaintListResponse, CategoryResponse, LocationCreate, LocationResponse,
    VoteCreate, VoteResponse
)
from common.auth import get_current_active_user, require_admin, require_department, require_citizen
from common.exceptions import NotFoundException, ValidationException, ForbiddenException
from priority_engine.engine import get_priority_engine, get_priority_queue, get_location_trie

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    description: str = Form(...),
    category_id: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(None),
    landmark: str = Form(None),
    area_name: str = Form(None),
    city: str = Form("Mumbai"),
    state: str = Form("Maharashtra"),
    pincode: str = Form(None),
    evidence_files: List[UploadFile] = File(default=[]),
    current_user = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    """Submit a new complaint with location and optional evidence"""
    # Validate category
    category = db.query(Category).filter(Category.id == category_id, Category.is_active == True).first()
    if not category:
        raise NotFoundException("Category not found or inactive")
    
    # Create or find location
    location = Location(
        latitude=latitude,
        longitude=longitude,
        address=address,
        landmark=landmark,
        area_name=area_name,
        city=city,
        state=state,
        pincode=pincode,
        is_sensitive_zone=0,  # Will be determined by background job
        created_at=datetime.utcnow().timestamp()
    )
    db.add(location)
    db.flush()
    
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
        location_id=location.id,
        description=description,
        evidence_urls=str(evidence_urls),
        status=ComplaintStatus.SUBMITTED,
        priority=PriorityLevel.LOW,  # Will be calculated
        priority_score=0.0,
        created_at=datetime.utcnow()
    )
    db.add(complaint)
    db.flush()
    
    # Calculate priority
    engine = get_priority_engine()
    priority_result = engine.calculate_priority(
        category=category,
        location=location,
        created_at=complaint.created_at,
        upvote_count=0
    )
    
    complaint.priority = priority_result.priority
    complaint.priority_score = priority_result.priority_score
    complaint.status = ComplaintStatus.PRIORITIZED
    
    # Add to priority queue
    pq = get_priority_queue()
    pq.push(complaint, priority_result.priority_score)
    
    # Add location to trie
    trie = get_location_trie()
    if area_name:
        trie.insert(area_name, location.id)
    if landmark:
        trie.insert(landmark, location.id)
    
    db.commit()
    db.refresh(complaint)
    
    # Send notification (async in production)
    await send_complaint_notification(complaint, db)
    
    return complaint


@router.get("", response_model=ComplaintListResponse)
async def list_complaints(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[ComplaintStatus] = None,
    priority_filter: Optional[PriorityLevel] = None,
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
    
    if status_filter:
        query = query.filter(Complaint.status == status_filter)
    if priority_filter:
        query = query.filter(Complaint.priority == priority_filter)
    if category_id:
        query = query.filter(Complaint.category_id == category_id)
    
    total = query.count()
    complaints = query.order_by(desc(Complaint.created_at)).offset(
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
    
    # Check access
    if current_user.role.value == "citizen":
        citizen = db.query(Citizen).filter(Citizen.user_id == current_user.id).first()
        if not citizen or complaint.citizen_id != citizen.id:
            raise ForbiddenException("Not authorized to view this complaint")
    
    return complaint


@router.put("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: int,
    update_data: ComplaintUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update complaint (citizen can update description, admin/dept can update status/priority)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise NotFoundException("Complaint not found")
    
    # Check permissions
    if current_user.role.value == "citizen":
        citizen = db.query(Citizen).filter(Citizen.user_id == current_user.id).first()
        if not citizen or complaint.citizen_id != citizen.id:
            raise ForbiddenException("Not authorized")
        # Citizens can only update description
        if update_data.description is not None:
            complaint.description = update_data.description
    elif current_user.role.value in ["admin", "department"]:
        # Admin/department can update status, priority, department
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
            if update_data.status == ComplaintStatus.ASSIGNED and not complaint.assigned_at:
                complaint.assigned_at = datetime.utcnow()
            elif update_data.status == ComplaintStatus.IN_PROGRESS and not complaint.started_at:
                complaint.started_at = datetime.utcnow()
            elif update_data.status == ComplaintStatus.RESOLVED and not complaint.resolved_at:
                complaint.resolved_at = datetime.utcnow()
                # Remove from priority queue
                pq = get_priority_queue()
                pq.remove(complaint.id)
        
        if update_data.priority is not None:
            complaint.priority = update_data.priority
        
        if update_data.department_id is not None:
            complaint.department_id = update_data.department_id
        
        if update_data.description is not None:
            complaint.description = update_data.description
    
    complaint.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(complaint)
    
    # Send notification on status change
    if update_data.status is not None:
        await send_status_change_notification(complaint, update_data.status, db)
    
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
    
    # Recalculate priority
    engine = get_priority_engine()
    category = db.query(Category).filter(Category.id == complaint.category_id).first()
    location = db.query(Location).filter(Location.id == complaint.location_id).first()
    
    if category and location:
        priority_result = engine.calculate_priority(
            category=category,
            location=location,
            created_at=complaint.created_at,
            upvote_count=complaint.upvote_count
        )
        complaint.priority = priority_result.priority
        complaint.priority_score = priority_result.priority_score
        
        # Update priority queue
        pq = get_priority_queue()
        pq.update_priority(complaint.id, priority_result.priority_score, complaint.created_at)
    
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
        
        # Recalculate priority
        engine = get_priority_engine()
        category = db.query(Category).filter(Category.id == complaint.category_id).first()
        location = db.query(Location).filter(Location.id == complaint.location_id).first()
        
        if category and location:
            priority_result = engine.calculate_priority(
                category=category,
                location=location,
                created_at=complaint.created_at,
                upvote_count=complaint.upvote_count
            )
            complaint.priority = priority_result.priority
            complaint.priority_score = priority_result.priority_score
            
            pq = get_priority_queue()
            pq.update_priority(complaint.id, priority_result.priority_score, complaint.created_at)
    
    db.delete(vote)
    db.commit()
    
    return {"message": "Upvote removed"}


@router.get("/locations/search", response_model=List[LocationResponse])
async def search_locations(
    q: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Search locations by prefix (uses trie)"""
    trie = get_location_trie()
    location_ids = trie.search_prefix(q)[:limit]
    
    if not location_ids:
        return []
    
    locations = db.query(Location).filter(Location.id.in_(location_ids)).all()
    return locations


async def send_complaint_notification(complaint: Complaint, db: Session):
    """Send notification on complaint submission"""
    citizen = db.query(Citizen).filter(Citizen.id == complaint.citizen_id).first()
    if not citizen or not citizen.user:
        return
    
    # Create in-app notification
    notification = Notification(
        recipient_id=citizen.user_id,
        complaint_id=complaint.id,
        channel=NotificationChannel.IN_APP,
        subject="Complaint Submitted",
        message=f"Your complaint #{complaint.id} has been submitted and is being prioritized.",
        status="sent",
        sent_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()


async def send_status_change_notification(complaint: Complaint, new_status: ComplaintStatus, db: Session):
    """Send notification on status change"""
    citizen = db.query(Citizen).filter(Citizen.id == complaint.citizen_id).first()
    if not citizen or not citizen.user:
        return
    
    status_messages = {
        ComplaintStatus.PRIORITIZED: "Your complaint has been prioritized.",
        ComplaintStatus.ASSIGNED: "Your complaint has been assigned to a department.",
        ComplaintStatus.IN_PROGRESS: "Work has started on your complaint.",
        ComplaintStatus.RESOLVED: "Your complaint has been resolved!",
        ComplaintStatus.REJECTED: "Your complaint was rejected. Please contact support for details."
    }
    
    message = status_messages.get(new_status, f"Your complaint status changed to {new_status.value}.")
    
    notification = Notification(
        recipient_id=citizen.user_id,
        complaint_id=complaint.id,
        channel=NotificationChannel.IN_APP,
        subject=f"Complaint #{complaint.id} Status Update",
        message=message,
        status="sent",
        sent_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()