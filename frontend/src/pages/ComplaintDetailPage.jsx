import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { complaintAPI } from '../services/api'
import { Button, Card, CardContent, Badge, StatusBadge, Alert, LoadingState } from '../components/UI'
import { 
  MapPin, Clock, Info, FileText, Flag, 
  UserCheck, Loader, CheckCircle2, XCircle,
  ArrowLeft, ThumbsUp, ChevronLeft, ChevronRight
} from 'lucide-react'
import { formatDateTime, formatRelativeTime, getStatusConfig, classNames, getInitials, generateAvatarColor } from '../utils/helpers'

const STATUS_ORDER = ['pending', 'working', 'completed']

export function ComplaintDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user, isCitizen, isAdmin, isDepartment } = useAuth()
  const [complaint, setComplaint] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [upvoting, setUpvoting] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState(false)
  const [imageIndex, setImageIndex] = useState(0)

  const fetchComplaint = async () => {
    try {
      setLoading(true)
      const response = await complaintAPI.get(id)
      setComplaint(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load complaint')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchComplaint()
  }, [id])

  const handleUpvote = async () => {
    if (!complaint || upvoting) return
    setUpvoting(true)
    try {
      await complaintAPI.upvote(id)
      setComplaint((prev) => ({
        ...prev,
        upvote_count: prev.upvote_count + 1,
        user_voted: true
      }))
    } catch (err) {
      if (err.response?.status === 400 || err.response?.data?.detail === "Already voted on this complaint") {
        alert("You have already voted on this complaint.")
      } else {
        console.error('Upvote failed:', err)
      }
    } finally {
      setUpvoting(false)
    }
  }

  const handleStatusChange = async (newStatus) => {
    if (!complaint || updatingStatus) return
    setUpdatingStatus(true)
    try {
      await complaintAPI.update(id, { status: newStatus })
      await fetchComplaint()
    } catch (err) {
      console.error('Status update failed:', err)
      alert("Failed to update status. Are you authorized?")
    } finally {
      setUpdatingStatus(false)
    }
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="flex items-center justify-between mb-6">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          <LoadingState />
          <LoadingState />
          <LoadingState />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="flex items-center justify-between mb-6">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
        </div>
        <Alert variant="danger" className="max-w-2xl">
          <p className="font-medium">Failed to load complaint</p>
          <p className="text-body-sm mt-1">{error}</p>
        </Alert>
        <Button variant="primary" onClick={fetchComplaint} className="mt-4">
          Try Again
        </Button>
      </div>
    )
  }

  if (!complaint) return null

  const config = getStatusConfig(complaint.status || 'pending')
  const statusStep = STATUS_ORDER.indexOf(complaint.status || 'pending')
  
  let evidenceUrls = []
  if (Array.isArray(complaint.evidence_urls)) {
    evidenceUrls = complaint.evidence_urls
  } else if (typeof complaint.evidence_urls === 'string' && complaint.evidence_urls.trim() !== '') {
    try {
      evidenceUrls = JSON.parse(complaint.evidence_urls)
    } catch (e) {
      console.error('Failed to parse evidence_urls', e)
    }
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-heading-lg font-bold text-text-primary">Complaint #{complaint.id}</h1>
            <p className="text-body text-text-secondary">{complaint.category?.display_name || 'Unknown Category'}</p>
          </div>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <StatusBadge status={complaint.status || 'pending'} size="lg" />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description Card */}
          <Card>
            <CardContent className="p-5">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-heading-sm font-semibold text-text-primary">Description</h2>
                <div className="flex items-center gap-2">
                  <Badge variant="primary">{complaint.category?.display_name || 'General'}</Badge>
                </div>
              </div>
              <p className="text-body text-text-primary whitespace-pre-wrap">{complaint.description}</p>
              
              <div className="mt-4 flex flex-wrap items-center gap-4 text-body-sm text-text-secondary">
                <span className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  {complaint.location || 'Location not specified'}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  Submitted {formatRelativeTime(complaint.created_at)}
                </span>
                {complaint.resolved_at && (
                  <span className="flex items-center gap-1 text-green-600">
                    <CheckCircle2 className="h-4 w-4" />
                    Resolved {formatRelativeTime(complaint.resolved_at)}
                  </span>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Evidence Gallery */}
          {evidenceUrls.length > 0 && (
            <Card>
              <CardContent className="p-5">
                <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Evidence Photos</h2>
                <div className="relative">
                  <div className="aspect-video rounded-card overflow-hidden bg-surface-elevated">
                    <img
                      src={evidenceUrls[imageIndex]}
                      alt={`Evidence ${imageIndex + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  {evidenceUrls.length > 1 && (
                    <>
                      <button
                         onClick={() => setImageIndex((i) => (i - 1 + evidenceUrls.length) % evidenceUrls.length)}
                        className="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white/90 backdrop-blur flex items-center justify-center shadow-card hover:bg-white transition-colors"
                        aria-label="Previous image"
                      >
                        <ChevronLeft className="h-5 w-5 text-text-primary" />
                      </button>
                      <button
                        onClick={() => setImageIndex((i) => (i + 1) % evidenceUrls.length)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white/90 backdrop-blur flex items-center justify-center shadow-card hover:bg-white transition-colors"
                        aria-label="Next image"
                      >
                        <ChevronRight className="h-5 w-5 text-text-primary" />
                      </button>
                    </>
                  )}
                  <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1">
                    {evidenceUrls.map((_, idx) => (
                      <button
                        key={idx}
                        onClick={() => setImageIndex(idx)}
                        className={classNames(
                          'w-2 h-2 rounded-full transition-colors',
                          idx === imageIndex ? 'bg-white' : 'bg-white/50 hover:bg-white/75'
                        )}
                        aria-label={`View image ${idx + 1}`}
                      />
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Status Timeline */}
          <Card>
            <CardContent className="p-5">
              <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Status Timeline</h2>
              <div className="relative">
                <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border" />
                {STATUS_ORDER.map((step, idx) => {
                  const stepConfig = getStatusConfig(step)
                  const StepIcon = getIconComponent(stepConfig.icon)
                  const isCompleted = idx <= statusStep
                  const isCurrent = idx === statusStep
                  const historyEntry = complaint.status_history?.find(h => h.new_status === step)
                  
                  return (
                    <div key={step} className="relative pl-14 pb-6 last:pb-0 flex items-start">
                      <div className={classNames(
                        'absolute left-6 top-1 w-3 h-3 rounded-full border-3 flex-shrink-0 z-10',
                        isCompleted ? 'bg-primary-500 border-primary-500' : 'bg-white border-border'
                      )}>
                        {isCurrent && <div className="absolute inset-1 bg-white" /> }
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className={classNames('flex items-center gap-2', isCurrent ? 'text-primary-600' : 'text-text-secondary')}>
                          <StepIcon className={classNames('h-4 w-4', isCurrent ? 'text-primary-500' : '')} />
                          <span className={classNames('font-medium', isCurrent ? 'text-text-primary' : '')}>
                            {stepConfig.label}
                          </span>
                          {isCurrent && <span className="text-caption bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">Current</span>}
                        </div>
                        {historyEntry && (
                          <p className="mt-1 text-body-sm text-text-muted pl-6">
                            {formatDateTime(historyEntry.created_at)}
                          </p>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Upvote Section */}
          {isCitizen && (
            <Card>
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={handleUpvote}
                      disabled={upvoting || complaint.user_voted}
                      className={classNames(
                        'flex items-center gap-2 px-4 py-2 rounded-button border transition-colors',
                        complaint.user_voted
                          ? 'bg-primary-50 border-primary-200 text-primary-600'
                          : 'bg-surface-elevated border-border text-text-secondary hover:bg-surface-hover'
                      )}
                      aria-label="Upvote"
                    >
                      <ThumbsUp className={classNames('h-5 w-5', complaint.user_voted ? 'text-primary-500' : '')} />
                      <span className="font-medium">{complaint.upvote_count || 0}</span>
                    </button>
                    <div className="hidden sm:block text-body-sm text-text-muted">
                      {complaint.user_voted ? 'You upvoted this' : 'Upvote to increase priority'}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Comments/Updates */}
          {complaint.status_history && complaint.status_history.length > 0 && (
            <Card>
              <CardContent className="p-5">
                <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Updates</h2>
                <div className="space-y-4">
                  {complaint.status_history.slice().reverse().map((entry) => (
                    <div key={entry.id} className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                        <Info className="h-4 w-4 text-primary-500" />
                      </div>
                      <div className="flex-1">
                        <p className="text-body text-text-primary">Status changed to {getStatusConfig(entry.new_status).label}</p>
                        <p className="text-caption text-text-muted mt-0.5">
                          {formatDateTime(entry.created_at)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Info Card */}
          <Card>
            <CardContent className="p-5">
              <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Complaint Info</h2>
              <dl className="space-y-4 text-body-sm">
                <div>
                  <dt className="text-text-muted">Complaint ID</dt>
                  <dd className="font-mono text-text-primary">#{complaint.id}</dd>
                </div>
                <div>
                  <dt className="text-text-muted">Category</dt>
                  <dd className="font-medium text-text-primary">{complaint.category?.display_name || 'General'}</dd>
                </div>
                <div>
                  <dt className="text-text-muted">Status</dt>
                  <dd className="flex items-center gap-2">
                    <StatusBadge status={complaint.status || 'pending'} />
                  </dd>
                </div>
                <div>
                  <dt className="text-text-muted">Location</dt>
                  <dd className="font-medium text-text-primary">{complaint.location}</dd>
                </div>
                <div>
                  <dt className="text-text-muted">Submitted</dt>
                  <dd className="font-medium text-text-primary">{formatDateTime(complaint.created_at)}</dd>
                </div>
                {complaint.assigned_at && (
                  <div>
                    <dt className="text-text-muted">Assigned</dt>
                    <dd className="font-medium text-text-primary">{formatDateTime(complaint.assigned_at)}</dd>
                  </div>
                )}
                {complaint.resolved_at && (
                  <div>
                    <dt className="text-text-muted">Resolved</dt>
                    <dd className="font-medium text-green-600">{formatDateTime(complaint.resolved_at)}</dd>
                  </div>
                )}
                {complaint.department && (
                  <div>
                    <dt className="text-text-muted">Department</dt>
                    <dd className="font-medium text-text-primary">{complaint.department.display_name}</dd>
                  </div>
                )}
                <div>
                  <dt className="text-text-muted">Total Upvotes</dt>
                  <dd className="font-medium text-text-primary">{complaint.upvote_count || 0}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          {/* Department Actions */}
          {(isAdmin || isDepartment) && complaint.status !== 'completed' && (
            <Card className="border-primary-200 bg-primary-50">
              <CardContent className="p-5">
                <h2 className="text-heading-sm font-semibold text-primary-700 mb-4">Update Status</h2>
                <div className="space-y-2">
                  {complaint.status === 'pending' ? (
                    <Button variant="primary" className="w-full" onClick={() => handleStatusChange('working')} loading={updatingStatus}>
                      Mark as Working
                    </Button>
                  ) : complaint.status === 'working' ? (
                    <Button variant="success" className="w-full" onClick={() => handleStatusChange('completed')} loading={updatingStatus}>
                      Mark as Completed
                    </Button>
                  ) : null}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

function getIconComponent(name) {
  const icons = {
    'file-text': FileText,
    'flag': Flag,
    'user-check': UserCheck,
    'loader': Loader,
    'check-circle-2': CheckCircle2,
    'x-circle': XCircle,
    'info': Info,
  }
  return icons[name] || FileText
}
