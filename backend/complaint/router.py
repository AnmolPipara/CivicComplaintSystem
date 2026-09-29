from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, nullslast
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse

from db.session import get_db
from models import (
    Complaint, Category, Department, 
    ComplaintStatus, Citizen, Vote, User, UserRole
)
from schemas import (
    ComplaintCreate, ComplaintUpdate, ComplaintResponse, 
    ComplaintListResponse, CategoryResponse, VoteCreate, VoteResponse
)
from common.auth import get_current_active_user, get_optional_current_user, require_admin, require_department, require_citizen
from common.exceptions import NotFoundException, ValidationException, ForbiddenException, UnauthorizedException
from common.geo import get_visibility_radius_km, calculate_haversine_distance_km, get_haversine_sql_expression
from common.email_service import send_complaint_notification

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def _attach_user_voted_to_complaints(complaints: List[Complaint], user: Optional[User], db: Session) -> None:
    """Attach boolean user_voted flag to complaints for the authenticated citizen."""
    if not complaints:
        return
    if not user or user.role != UserRole.CITIZEN:
        for c in complaints:
            setattr(c, "user_voted", False)
        return
    citizen = db.query(Citizen).filter(Citizen.user_id == user.id).first()
    if not citizen:
        for c in complaints:
            setattr(c, "user_voted", False)
        return
    complaint_ids = [c.id for c in complaints]
    voted_ids = set(
        r[0] for r in db.query(Vote.complaint_id).filter(
            Vote.citizen_id == citizen.id,
            Vote.complaint_id.in_(complaint_ids)
        ).all()
    )
    for c in complaints:
        setattr(c, "user_voted", c.id in voted_ids)


def _attach_user_voted_to_single(complaint: Optional[Complaint], user: Optional[User], db: Session) -> None:
    """Attach boolean user_voted flag to single complaint for the authenticated citizen."""
    if not complaint:
        return
    if not user or user.role != UserRole.CITIZEN:
        setattr(complaint, "user_voted", False)
        return
    citizen = db.query(Citizen).filter(Citizen.user_id == user.id).first()
    if not citizen:
        setattr(complaint, "user_voted", False)
        return
    has_voted = db.query(Vote.id).filter(
        Vote.citizen_id == citizen.id,
        Vote.complaint_id == complaint.id
    ).first() is not None
    setattr(complaint, "user_voted", has_voted)


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    background_tasks: BackgroundTasks,
    description: Optional[str] = Form(default=""),
    category_id: int = Form(...),
    location: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    evidence_files: List[UploadFile] = File(default=[]),
    current_user = Depends(require_citizen),
    db: Session = Depends(get_db)
):
    """Submit a new complaint with location and optional evidence"""
    description = description or ""
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
    
    # Assess complaint with LLM prioritization service
    from complaint.assessment import assess_complaint
    assessment = await assess_complaint(
        category_name=category.name,
        category_display=category.display_name,
        description=description,
        location=location,
        latitude=latitude,
        longitude=longitude,
        upvote_count=0
    )
    
    # Auto-assign department based on category if department_id is configured
    assigned_dept_id = category.department_id if category else None
    
    # Create complaint with full assessment and priority metrics
    complaint = Complaint(
        citizen_id=citizen.id,
        category_id=category_id,
        department_id=assigned_dept_id,
        assigned_at=datetime.utcnow() if assigned_dept_id else None,
        location=location,
        latitude=latitude,
        longitude=longitude,
        description=description,
        evidence_urls=evidence_urls,
        status=ComplaintStatus.PENDING,
        created_at=datetime.utcnow(),
        # Priority & Assessment fields
        severity_score=assessment.severity_score,
        impact_score=assessment.impact_score,
        urgency_score=assessment.urgency_score,
        priority_score=assessment.priority_score,
        priority_level=assessment.priority_level,
        assessment_status=assessment.assessment_status,
        assessment_reason=assessment.assessment_reason,
        assessment_confidence=assessment.assessment_confidence,
        missing_information=assessment.missing_information,
        needs_human_review=assessment.needs_human_review,
        is_safety_escalated=assessment.is_safety_escalated,
        # AI Audit trail
        ai_severity_score=assessment.ai_severity_score,
        ai_impact_score=assessment.ai_impact_score,
        ai_urgency_score=assessment.ai_urgency_score,
        ai_reason=assessment.ai_reason
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    
    # Send email notification to citizen
    background_tasks.add_task(
        send_complaint_notification,
        event_type="registered",
        complaint_id=complaint.id,
        recipient_email=current_user.email,
        recipient_name=current_user.full_name,
        category_name=category.display_name if category else "Civic Issue",
        location=complaint.location,
        description=complaint.description,
        timestamp=complaint.created_at
    )
    
    _attach_user_voted_to_single(complaint, current_user, db)
    return complaint


@router.get("", response_model=ComplaintListResponse)
async def list_complaints(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[ComplaintStatus] = None,
    status: Optional[ComplaintStatus] = None,
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
    
    effective_status = status_filter or status
    if effective_status:
        query = query.filter(Complaint.status == effective_status)
    if category_id:
        query = query.filter(Complaint.category_id == category_id)
    
    total = query.count()
    # Prioritize based on priority score (descending), upvotes, then creation date
    complaints = query.order_by(
        nullslast(desc(Complaint.priority_score)),
        desc(Complaint.upvote_count),
        desc(Complaint.created_at)
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    _attach_user_voted_to_complaints(complaints, current_user, db)
    
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
    status_filter: Optional[ComplaintStatus] = None,
    status: Optional[ComplaintStatus] = None,
    category_id: Optional[int] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    List complaints for public feed:
    - If authenticated citizen: return only incidents within 25 km of user's saved location.
    - If citizen has not saved a location: return empty list so unlocated incidents are not shown.
    - If unauthenticated: return empty list to enforce geographic restriction.
    - Admins retain authorized access across all locations.
    """
    query = db.query(Complaint)
    
    if current_user and current_user.role == UserRole.CITIZEN:
        citizen = db.query(Citizen).filter(Citizen.user_id == current_user.id).first()
        if not citizen or citizen.latitude is None or citizen.longitude is None:
            return ComplaintListResponse(complaints=[], total=0, page=page, page_size=page_size)
        
        radius_km = get_visibility_radius_km()
        dist_expr = get_haversine_sql_expression(
            citizen.latitude, citizen.longitude, Complaint.latitude, Complaint.longitude
        )
        query = query.filter(
            Complaint.latitude.isnot(None),
            Complaint.longitude.isnot(None),
            dist_expr <= radius_km
        )
    elif not current_user:
        # Unauthenticated visitor: require location by returning empty feed
        return ComplaintListResponse(complaints=[], total=0, page=page, page_size=page_size)
    
    effective_status = status_filter or status
    if effective_status:
        query = query.filter(Complaint.status == effective_status)
    if category_id:
        query = query.filter(Complaint.category_id == category_id)
        
    total = query.count()
    complaints = query.order_by(
        nullslast(desc(Complaint.priority_score)),
        desc(Complaint.upvote_count),
        desc(Complaint.created_at)
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    _attach_user_voted_to_complaints(complaints, current_user, db)
    
    return ComplaintListResponse(
        complaints=complaints,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Get complaint details with 25 km visibility check for citizens"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise NotFoundException("Complaint not found")
    
    # Admins and departments retain access across all locations
    if current_user and current_user.role in [UserRole.ADMIN, UserRole.DEPARTMENT]:
        _attach_user_voted_to_single(complaint, current_user, db)
        return complaint
    
    # Citizen checks
    if current_user and current_user.role == UserRole.CITIZEN:
        citizen = db.query(Citizen).filter(Citizen.user_id == current_user.id).first()
        # Author can always view their own complaint
        if citizen and complaint.citizen_id == citizen.id:
            _attach_user_voted_to_single(complaint, current_user, db)
            return complaint
        
        if not citizen or citizen.latitude is None or citizen.longitude is None:
            raise ValidationException("Please save your location to view incidents within your 25 km community radius.")
        
        if complaint.latitude is None or complaint.longitude is None:
            raise NotFoundException("Complaint not found or outside visibility radius")
        
        dist = calculate_haversine_distance_km(
            citizen.latitude, citizen.longitude, complaint.latitude, complaint.longitude
        )
        radius_km = get_visibility_radius_km()
        if dist > radius_km:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This incident is {dist:.1f} km away, which is outside your {radius_km:.0f} km community radius."
            )
        _attach_user_voted_to_single(complaint, current_user, db)
        return complaint
    
    raise UnauthorizedException("Please log in to view incident details.")


@router.put("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: int,
    update_data: ComplaintUpdate,
    background_tasks: BackgroundTasks,
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
            
            # Send email notification to citizen on status progression
            if old_status != update_data.status and update_data.status in (ComplaintStatus.WORKING, ComplaintStatus.COMPLETED):
                citizen = db.query(Citizen).filter(Citizen.id == complaint.citizen_id).first()
                citizen_user = citizen.user if citizen else None
                if citizen_user and citizen_user.email:
                    cat_obj = db.query(Category).filter(Category.id == complaint.category_id).first()
                    cat_name = cat_obj.display_name if cat_obj else "Civic Complaint"
                    event_type = "working" if update_data.status == ComplaintStatus.WORKING else "completed"
                    background_tasks.add_task(
                        send_complaint_notification,
                        event_type=event_type,
                        complaint_id=complaint.id,
                        recipient_email=citizen_user.email,
                        recipient_name=citizen_user.full_name,
                        category_name=cat_name,
                        location=complaint.location,
                        description=complaint.description,
                        timestamp=datetime.utcnow()
                    )
        
        # Admin can update department
        if update_data.department_id is not None and current_user.role.value == "admin":
            complaint.department_id = update_data.department_id
            if not complaint.assigned_at:
                complaint.assigned_at = datetime.utcnow()
    
    complaint.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(complaint)
    
    _attach_user_voted_to_single(complaint, current_user, db)
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
    
    # 1 & 2. Verify user has saved location coordinates
    if citizen.latitude is None or citizen.longitude is None:
        raise ValidationException(
            "Please add your location before upvoting. You can only view and support incidents within 25 km of your saved location."
        )
    
    # 3. Verify incident coordinates exist
    if complaint.latitude is None or complaint.longitude is None:
        raise ValidationException("This incident cannot be upvoted because its geographic coordinates are not set.")
    
    # 4. Verify incident is within 25 km of user's saved location
    distance_km = calculate_haversine_distance_km(
        citizen.latitude, citizen.longitude, complaint.latitude, complaint.longitude
    )
    radius_km = get_visibility_radius_km()
    if distance_km > radius_km:
        raise ValidationException(
            f"This incident is {distance_km:.1f} km away, which is outside your {radius_km:.0f} km community radius. Upvoting is only permitted within {radius_km:.0f} km."
        )
    
    # 5. Verify incident status is pending (voting only allowed for pending complaints)
    current_status = complaint.status.value if hasattr(complaint.status, 'value') else complaint.status
    if current_status != "pending":
        raise ValidationException(
            f"Voting is only allowed when the incident status is pending (current status: {current_status})."
        )
    
    # 6. Check if already voted
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
    
    # Recalculate priority score using saved assessment components (No LLM call)
    from complaint.assessment import calculate_priority_score
    if complaint.severity_score is not None:
        new_score, new_level = calculate_priority_score(
            severity=complaint.severity_score,
            impact=complaint.impact_score if complaint.impact_score is not None else 35,
            urgency=complaint.urgency_score if complaint.urgency_score is not None else 35,
            upvote_count=complaint.upvote_count,
            is_safety_escalated=complaint.is_safety_escalated
        )
        complaint.priority_score = new_score
        complaint.priority_level = new_level
    
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
    if not complaint:
        raise NotFoundException("Complaint not found")
        
    current_status = complaint.status.value if hasattr(complaint.status, 'value') else complaint.status
    if current_status != "pending":
        raise ValidationException(
            f"Votes can only be modified when the incident status is pending (current status: {current_status})."
        )
    
    complaint.upvote_count = max(0, complaint.upvote_count - 1)
    # Recalculate priority score using saved assessment components (No LLM call)
    from complaint.assessment import calculate_priority_score
    if complaint.severity_score is not None:
        new_score, new_level = calculate_priority_score(
            severity=complaint.severity_score,
            impact=complaint.impact_score if complaint.impact_score is not None else 35,
            urgency=complaint.urgency_score if complaint.urgency_score is not None else 35,
            upvote_count=complaint.upvote_count,
            is_safety_escalated=complaint.is_safety_escalated
        )
        complaint.priority_score = new_score
        complaint.priority_level = new_level

    db.delete(vote)
    db.commit()
    
    return {"message": "Upvote removed"}