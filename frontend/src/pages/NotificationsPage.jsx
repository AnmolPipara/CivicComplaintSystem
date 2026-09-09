import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { notificationAPI } from '../services/api'
import { Card, CardContent, Badge, Button, EmptyState, LoadingState, Skeleton } from '../components/UI'
import { Bell, Mail, MessageSquare, Check, X, Clock, ChevronRight } from 'lucide-react'
import { formatDateTime, formatRelativeTime, classNames } from '../utils/helpers'

const CHANNEL_ICONS = {
  email: Mail,
  sms: MessageSquare,
  push: Bell,
  in_app: Bell,
}

const CHANNEL_COLORS = {
  email: 'text-blue-500 bg-blue-50',
  sms: 'text-green-500 bg-green-50',
  push: 'text-purple-500 bg-purple-50',
  in_app: 'text-primary-500 bg-primary-50',
}

export function NotificationsPage() {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [unreadOnly, setUnreadOnly] = useState(false)
  const [page, setPage] = useState(1)
  const pageSize = 20

  const fetchNotifications = async () => {
    try {
      setLoading(true)
      const response = await notificationAPI.list(unreadOnly, pageSize)
      setNotifications(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load notifications')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNotifications()
  }, [unreadOnly])

  const handleMarkRead = async (notificationId) => {
    try {
      await notificationAPI.markRead(notificationId)
      setNotifications((prev) =>
        prev.map((n) => (n.id === notificationId ? { ...n, status: 'read' } : n))
      )
    } catch (err) {
      console.error('Mark read failed:', err)
    }
  }

  const handleMarkAllRead = async () => {
    try {
      await notificationAPI.markAllRead()
      setNotifications((prev) => prev.map((n) => ({ ...n, status: 'read' })))
    } catch (err) {
      console.error('Mark all read failed:', err)
    }
  }

  const unreadCount = notifications.filter((n) => n.status !== 'read').length

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-heading-lg font-bold text-text-primary">Notifications</h1>
          <p className="text-body text-text-secondary mt-1">Stay updated on your complaints and system alerts</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={unreadOnly}
              onChange={(e) => setUnreadOnly(e.target.checked)}
              className="w-4 h-4 rounded border-border text-primary-500 focus:ring-primary-500"
            />
            <span className="text-body-sm text-text-secondary">Unread only</span>
          </label>
          {unreadCount > 0 && (
            <Button variant="secondary" size="sm" onClick={handleMarkAllRead}>
              <Check className="h-3.5 w-3.5" />
              Mark all read
            </Button>
          )}
        </div>
      </div>

      {error && (
        <Alert variant="danger" className="mb-6" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <Card key={i} className="p-4">
              <div className="flex items-start gap-3">
                <Skeleton variant="circular" width="10" height="10" className="mt-1" />
                <div className="flex-1 space-y-2">
                  <Skeleton variant="text" width="60%" />
                  <Skeleton variant="text" width="40%" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : notifications.length === 0 ? (
        <EmptyState
          icon={Bell}
          title={unreadOnly ? 'No unread notifications' : 'No notifications yet'}
          description={unreadOnly 
            ? 'All caught up! You have no unread notifications.'
            : 'Notifications will appear here when you receive updates on your complaints.'}
        />
      ) : (
        <div className="space-y-3">
          {notifications.map((notification) => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              onMarkRead={() => handleMarkRead(notification.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function NotificationCard({ notification, onMarkRead }) {
  const isUnread = notification.status !== 'read'
  const ChannelIcon = CHANNEL_ICONS[notification.channel] || Bell
  const channelColor = CHANNEL_COLORS[notification.channel] || CHANNEL_COLORS.in_app

  return (
    <Card
      className={classNames(
        'hover:shadow-card-hover transition-shadow',
        isUnread && 'bg-primary-50/50 border-primary-100'
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className={classNames('w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0', channelColor)}>
            <ChannelIcon className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <h3 className={classNames('font-medium text-text-primary', isUnread && 'font-semibold')}>
                  {notification.subject || 'Notification'}
                </h3>
                <p className="text-body-sm text-text-secondary mt-1">{notification.message}</p>
                <div className="flex items-center gap-3 mt-2 text-caption text-text-muted">
                  <span className="flex items-center gap-1">
                    <ChannelIcon className="h-3 w-3" />
                    {notification.channel.replace('_', ' ').toUpperCase()}
                  </span>
                  <span>{formatRelativeTime(notification.created_at)}</span>
                  {notification.complaint_id && (
                    <span className="flex items-center gap-1">
                      <ChevronRight className="h-3 w-3" />
                      Complaint #{notification.complaint_id}
                    </span>
                  )}
                </div>
              </div>
              {isUnread && (
                <Button variant="ghost" size="sm" onClick={onMarkRead} className="h-8">
                  <Check className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
