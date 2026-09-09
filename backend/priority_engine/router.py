from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from db.session import get_db
from models import Complaint, Category, Location, PriorityLevel, ComplaintStatus
from schemas import (
    PriorityCalculationRequest,
    PriorityCalculationResponse,
    ComplaintResponse,
    ComplaintListResponse
)
from common.auth import get_current_active_user, require_admin, require_department
from common.exceptions import NotFoundException, ValidationException
from priority_engine.engine import (
    PriorityEngine,
    PriorityQueue,
    LocationTrie,
    get_priority_engine,
    get_priority_queue,
    get_location_trie
)

router = APIRouter(prefix="/api/priority", tags=["priority"])


@router.post("/calculate", response_model=PriorityCalculationResponse)
async def calculate_priority(
    request: PriorityCalculationRequest,
    db: Session = Depends(get_db),
    engine: PriorityEngine = Depends(get_priority_engine)
):
    """Calculate priority for a new complaint (preview)"""
    category = db.query(Category).filter(Category.id == request.category_id).first()
    location = db.query(Location).filter(Location.id == request.location_id).first()
    
    if not category:
        raise NotFoundException("Category not found")
    if not location:
        raise NotFoundException("Location not found")
    
    return engine.calculate_priority(
        category=category,
        location=location,
        created_at=request.created_at,
        upvote_count=request.upvote_count
    )


@router.post("/recalculate/{complaint_id}", response_model=PriorityCalculationResponse)
async def recalculate_complaint_priority(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
    engine: PriorityEngine = Depends(get_priority_engine),
    pq: PriorityQueue = Depends(get_priority_queue)
):
    """Manually trigger priority recalculation for a complaint"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise NotFoundException("Complaint not found")
    
    result = engine.recalculate_for_complaint(complaint, db)
    
    # Update complaint in database
    complaint.priority = result.priority
    complaint.priority_score = result.priority_score
    complaint.updated_at = datetime.utcnow()
    db.commit()
    
    # Update priority queue
    pq.update_priority(complaint.id, result.priority_score, complaint.created_at)
    
    return result


@router.post("/recalculate-all")
async def recalculate_all_priorities(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
    engine: PriorityEngine = Depends(get_priority_engine),
    pq: PriorityQueue = Depends(get_priority_queue)
):
    """Background job: recalculate priorities for all active complaints"""
    complaints = db.query(Complaint).filter(
        Complaint.status.in_([
            ComplaintStatus.SUBMITTED,
            ComplaintStatus.PRIORITIZED,
            ComplaintStatus.ASSIGNED,
            ComplaintStatus.IN_PROGRESS
        ])
    ).all()
    
    updated = 0
    for complaint in complaints:
        try:
            result = engine.recalculate_for_complaint(complaint, db)
            old_priority = complaint.priority
            complaint.priority = result.priority
            complaint.priority_score = result.priority_score
            complaint.updated_at = datetime.utcnow()
            
            # Update queue
            pq.update_priority(complaint.id, result.priority_score, complaint.created_at)
            
            if old_priority != result.priority:
                updated += 1
        except Exception as e:
            # Log error but continue
            print(f"Error recalculating complaint {complaint.id}: {e}")
    
    db.commit()
    return {"updated": updated, "total_processed": len(complaints)}


@router.get("/queue/top", response_model=List[ComplaintResponse])
async def get_top_priority_complaints(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(require_department),
    pq: PriorityQueue = Depends(get_priority_queue)
):
    """Get top N complaints from priority queue (for department dashboard)"""
    top_items = pq.get_top_n(limit)
    complaint_ids = [item.complaint_id for item in top_items]
    
    if not complaint_ids:
        return []
    
    complaints = db.query(Complaint).filter(Complaint.id.in_(complaint_ids)).all()
    complaint_map = {c.id: c for c in complaints}
    
    # Return in priority order
    return [complaint_map[cid] for cid in complaint_ids if cid in complaint_map]


@router.get("/queue/stats")
async def get_queue_stats(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
    pq: PriorityQueue = Depends(get_priority_queue)
):
    """Get priority queue statistics"""
    high_count = db.query(Complaint).filter(
        Complaint.priority == PriorityLevel.HIGH,
        Complaint.status.in_([
            ComplaintStatus.SUBMITTED,
            ComplaintStatus.PRIORITIZED,
            ComplaintStatus.ASSIGNED,
            ComplaintStatus.IN_PROGRESS
        ])
    ).count()
    
    medium_count = db.query(Complaint).filter(
        Complaint.priority == PriorityLevel.MEDIUM,
        Complaint.status.in_([
            ComplaintStatus.SUBMITTED,
            ComplaintStatus.PRIORITIZED,
            ComplaintStatus.ASSIGNED,
            ComplaintStatus.IN_PROGRESS
        ])
    ).count()
    
    low_count = db.query(Complaint).filter(
        Complaint.priority == PriorityLevel.LOW,
        Complaint.status.in_([
            ComplaintStatus.SUBMITTED,
            ComplaintStatus.PRIORITIZED,
            ComplaintStatus.ASSIGNED,
            ComplaintStatus.IN_PROGRESS
        ])
    ).count()
    
    return {
        "queue_size": pq.size(),
        "high_priority": high_count,
        "medium_priority": medium_count,
        "low_priority": low_count,
    }