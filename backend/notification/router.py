from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from db.session import get_db
from models import Notification, NotificationChannel, User, Complaint
from schemas import NotificationResponse, NotificationCreate
from common.auth import get_current_active_user, require_admin
from common.exceptions import NotFoundException

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List notifications for current user"""
    query = db.query(Notification).filter(Notification.recipient_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.status != "read")
    
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    return notifications


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notification detail"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == current_user.id
    ).first()
    
    if not notification:
        raise NotFoundException("Notification not found")
    
    return notification


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == current_user.id
    ).first()
    
    if not notification:
        raise NotFoundException("Notification not found")
    
    notification.status = "read"
    db.commit()
    
    return {"message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_read(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.recipient_id == current_user.id,
        Notification.status != "read"
    ).update({"status": "read"})
    
    db.commit()
    
    return {"message": "All notifications marked as read"}


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    notification_data: NotificationCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Send notification to user (admin only)"""
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == notification_data.recipient_id).first()
    if not recipient:
        raise NotFoundException("Recipient not found")
    
    notification = Notification(
        recipient_id=notification_data.recipient_id,
        complaint_id=notification_data.complaint_id,
        channel=notification_data.channel,
        subject=notification_data.subject,
        message=notification_data.message,
        status="pending"
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # In production, actually send via email/SMS/push service
    # For now, mark as sent
    notification.status = "sent"
    notification.sent_at = datetime.utcnow()
    db.commit()
    
    return notification


@router.post("/broadcast")
async def broadcast_notification(
    message: str,
    subject: str = "System Notification",
    channel: NotificationChannel = NotificationChannel.IN_APP,
    role_filter: str = None,  # "citizen", "admin", "department"
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Broadcast notification to multiple users"""
    query = db.query(User).filter(User.is_active == True)
    
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    users = query.all()
    
    notifications = []
    for user in users:
        notification = Notification(
            recipient_id=user.id,
            channel=channel,
            subject=subject,
            message=message,
            status="sent",
            sent_at=datetime.utcnow()
        )
        notifications.append(notification)
    
    db.add_all(notifications)
    db.commit()
    
    return {"sent_count": len(notifications)}


# Background task to send pending notifications
async def process_pending_notifications(db: Session):
    """Process pending notifications (called by background worker)"""
    pending = db.query(Notification).filter(Notification.status == "pending").limit(100).all()
    
    for notification in pending:
        try:
            # In production, integrate with:
            # - Email service (SendGrid, AWS SES)
            # - SMS service (Twilio, AWS SNS)
            # - Push service (Firebase, OneSignal)
            
            if notification.channel == NotificationChannel.EMAIL:
                await send_email(notification)
            elif notification.channel == NotificationChannel.SMS:
                await send_sms(notification)
            elif notification.channel == NotificationChannel.PUSH:
                await send_push(notification)
            # IN_APP is already delivered via database
            
            notification.status = "sent"
            notification.sent_at = datetime.utcnow()
        except Exception as e:
            notification.status = "failed"
            print(f"Failed to send notification {notification.id}: {e}")
    
    db.commit()


async def send_email(notification: Notification):
    """Send email notification (stub)"""
    # Integrate with SendGrid, AWS SES, etc.
    print(f"EMAIL to user {notification.recipient_id}: {notification.subject}")
    pass


async def send_sms(notification: Notification):
    """Send SMS notification (stub)"""
    # Integrate with Twilio, AWS SNS, etc.
    print(f"SMS to user {notification.recipient_id}: {notification.message}")
    pass


async def send_push(notification: Notification):
    """Send push notification (stub)"""
    # Integrate with Firebase, OneSignal, etc.
    print(f"PUSH to user {notification.recipient_id}: {notification.subject}")
    pass