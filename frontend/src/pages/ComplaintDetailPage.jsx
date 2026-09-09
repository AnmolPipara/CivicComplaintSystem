import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { complaintAPI, notificationAPI } from '../services/api'
import { Button, Card, CardContent, Badge, PriorityBadge, StatusBadge, Modal, Alert, EmptyState, LoadingState } from '../components/UI'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { 
  MapPin, Clock, User, Camera, MessageSquare, ThumbsUp, 
  ChevronLeft, ChevronRight, X, Share2, Download, 
  AlertTriangle, AlertCircle, Info, FileText, Flag, 
  UserCheck, Loader, CheckCircle2, XCircle,
  ArrowLeft, Star
} from 'lucide-react'
import { formatDate, formatDateTime, formatRelativeTime, getStatusConfig, classNames, truncate, getInitials, generateAvatarColor } from '../utils/helpers'

const STATUS_ORDER = ['submitted', 'prioritized', 'assigned', 'in_progress', 'resolved', 'rejected']

// Fix Leaflet marker icon
import L from 'leaflet'
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

export function ComplaintDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user, isCitizen, isAdmin, isDepartment } = useAuth()
  const [complaint, setComplaint] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [upvoting, setUpvoting] = useState(false)
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [feedbackRating, setFeedbackRating] = useState(0)
  const [submittingFeedback, setSubmittingFeedback] = useState(false)
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
        priority: complaint.upvote_count + 1 > 10 ? 'high' : complaint.priority,
      }))
    } catch (err) {
      console.error('Upvote failed:', err)
    } finally {
      setUpvoting(false)
    }
  }

  const handleRemoveUpvote = async () => {
    if (!complaint || upvoting) return
    setUpvoting(true)
    try {
      await complaintAPI.removeUpvote(id)
      setComplaint((prev) => ({
        ...prev,
        upvote_count: Math.max(0, prev.upvote_count - 1),
      }))
    } catch (err) {
      console.error('Remove upvote failed:', err)
    } finally {
      setUpvoting(false)
    }
  }

  const handleSubmitFeedback = async () => {
    if (!feedback.trim() || submittingFeedback) return
    setSubmittingFeedback(true)
    try {
      // In production, send feedback to API
      console.log('Feedback submitted:', { complaintId: id, rating: feedbackRating, message: feedback })
      setShowFeedbackModal(false)
      setFeedback('')
      setFeedbackRating(0)
    } catch (err) {
      console.error('Feedback failed:', err)
    } finally {
      setSubmittingFeedback(false)
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

  const config = getStatusConfig(complaint.status)
  const IconComponent = getIconComponent(config.icon)
  const statusStep = STATUS_ORDER.indexOf(complaint.status)
  const evidenceUrls = complaint.evidence_urls ? JSON.parse(complaint.evidence_urls) : []

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
          <PriorityBadge priority={complaint.priority} size="lg" />
          <StatusBadge status={complaint.status} size="lg" />
        </div>
      </div>

      {error && (
        <Alert variant="danger" className="mb-6" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description Card */}
          <Card>
            <CardContent className="p-5">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-heading-sm font-semibold text-text-primary">Description</h2>
                <div className="flex items-center gap-2">
                  <Badge variant="primary">{complaint.category?.display_name}</Badge>
                </div>
              </div>
              <p className="text-body text-text-primary whitespace-pre-wrap">{complaint.description}</p>
              
              <div className="mt-4 flex flex-wrap items-center gap-4 text-body-sm text-text-secondary">
                <span className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  {complaint.location?.area_name || complaint.location?.address || 'Location not specified'}
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
                {evidenceUrls.length > 1 && (
                  <div className="mt-4 grid grid-cols-5 gap-2">
                    {evidenceUrls.map((url, idx) => (
                      <button
                        key={idx}
                        onClick={() => setImageIndex(idx)}
                        className={classNames(
                          'aspect-square rounded-button overflow-hidden border-2 transition-all',
                          idx === imageIndex ? 'border-primary-500' : 'border-transparent hover:border-border'
                        )}
                      >
                        <img src={url} alt={`Thumbnail ${idx + 1}`} className="w-full h-full object-cover" />
                      </button>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Location Map */}
          {complaint.location && (
            <Card>
              <CardContent className="p-5">
                <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Location</h2>
                <div className="rounded-card overflow-hidden border border-border" style={{ height: '300px' }}>
                  <MapContainer
                    center={[complaint.location.latitude, complaint.location.longitude]}
                    zoom={16}
                    scrollWheelZoom={false}
                    className="h-full w-full"
                  >
                    <TileLayer
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    <Marker position={[complaint.location.latitude, complaint.location.longitude]}>
                      <Popup>
                        <div className="text-body-sm">
                          <p className="font-medium">{complaint.location.area_name || complaint.location.address?.split(',')[0]}</p>
                          <p className="text-text-muted truncate max-w-[200px]">{complaint.location.address}</p>
                        </div>
                      </Popup>
                    </Marker>
                  </MapContainer>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {complaint.location.area_name && <Badge variant="info">{complaint.location.area_name}</Badge>}
                  {complaint.location.landmark && <Badge variant="primary">{complaint.location.landmark}</Badge>}
                  <Badge variant="default">{complaint.location.city}, {complaint.location.state}</Badge>
                  {complaint.location.pincode && <Badge variant="default">{complaint.location.pincode}</Badge>}
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
                        {isCurrent && <div className="absolute inset-1 bg-white" />}
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
                            {historyEntry.notes ? `${historyEntry.notes} • ` : ''}
                            {formatDateTime(historyEntry.created_at)}
                            {historyEntry.changed_by && ` • by User #${historyEntry.changed_by}`}
                          </p>
                        )}
                        {!historyEntry && idx <= statusStep && (
                          <p className="mt-1 text-body-sm text-text-muted pl-6">Completed</p>
                        )}
                        {!historyEntry && idx > statusStep && (
                          <p className="mt-1 text-body-sm text-text-muted pl-6">Pending</p>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Upvote Section */}
          <Card>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    onClick={complaint.user_voted ? handleRemoveUpvote : handleUpvote}
                    disabled={upvoting}
                    className={classNames(
                      'flex items-center gap-2 px-4 py-2 rounded-button border transition-colors',
                      complaint.user_voted
                        ? 'bg-primary-50 border-primary-200 text-primary-600'
                        : 'bg-surface-elevated border-border text-text-secondary hover:bg-surface-hover'
                    )}
                    aria-label={complaint.user_voted ? 'Remove upvote' : 'Upvote'}
                    aria-pressed={complaint.user_voted}
                  >
                    <ThumbsUp className={classNames('h-5 w-5', complaint.user_voted ? 'text-primary-500' : '')} />
                    <span className="font-medium">{complaint.upvote_count}</span>
                  </button>
                  <div className="hidden sm:block text-body-sm text-text-muted">
                    {complaint.user_voted ? 'You upvoted this' : 'Upvote to increase priority'}
                  </div>
                </div>
                {(isAdmin || isDepartment) && (
                  <div className="flex items-center gap-2">
                    <Button variant="secondary" size="sm">
                      <Share2 className="h-4 w-4" />
                      Share
                    </Button>
                    <Button variant="secondary" size="sm">
                      <Download className="h-4 w-4" />
                      Export
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Feedback */}
          {complaint.status === 'resolved' && isCitizen && (
            <Card>
              <CardContent className="p-5">
                <h2 className="text-heading-sm font-semibold text-text-primary mb-4">How was the resolution?</h2>
                <p className="text-body text-text-secondary mb-4">Your feedback helps us improve our service.</p>
                <button
                  onClick={() => setShowFeedbackModal(true)}
                  className="btn-primary"
                >
                  <Star className="h-4 w-4" />
                  Give Feedback
                </button>
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
                        <p className="text-body text-text-primary">{entry.notes || `Status changed to ${getStatusConfig(entry.new_status).label}`}</p>
                        <p className="text-caption text-text-muted mt-0.5">
                          {formatDateTime(entry.created_at)}
                          {entry.changed_by && ` • by User #${entry.changed_by}`}
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
                  <dd className="font-medium text-text-primary">{complaint.category?.display_name}</dd>
                </div>
                <div>
                  <dt className="text-text-muted">Priority</dt>
                  <dd className="flex items-center gap-2">
                    <PriorityBadge priority={complaint.priority} />
                    <span className="text-text-muted">({complaint.priority_score?.toFixed(2) || '0.00'})</span>
                  </dd>
                </div>
                <div>
                  <dt className="text-text-muted">Status</dt>
                  <dd className="flex items-center gap-2">
                    <StatusBadge status={complaint.status} />
                  </dd>
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
                {complaint.started_at && (
                  <div>
                    <dt className="text-text-muted">Work Started</dt>
                    <dd className="font-medium text-text-primary">{formatDateTime(complaint.started_at)}</dd>
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
                  <dt className="text-text-muted">Upvotes</dt>
                  <dd className="font-medium text-text-primary">{complaint.upvote_count}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          {/* Submitted By */}
          <Card>
            <CardContent className="p-5">
              <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Submitted By</h2>
              <div className="flex items-center gap-3">
                <div className={classNames('w-12 h-12 rounded-full flex items-center justify-center font-semibold text-white', generateAvatarColor(complaint.citizen?.user?.full_name || 'Citizen'))}>
                  {getInitials(complaint.citizen?.user?.full_name || 'Citizen')}
                </div>
                <div>
                  <p className="font-medium text-text-primary">{complaint.citizen?.user?.full_name || 'Anonymous'}</p>
                  <p className="text-body-sm text-text-muted">Citizen</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Admin Actions */}
          {(isAdmin || isDepartment) && complaint.status !== 'resolved' && (
            <Card className="border-primary-200 bg-primary-50">
              <CardContent className="p-5">
                <h2 className="text-heading-sm font-semibold text-primary-700 mb-4">Actions</h2>
                <div className="space-y-2">
                  {complaint.status === 'submitted' || complaint.status === 'prioritized' ? (
                    <Button variant="primary" className="w-full" onClick={() => navigate(`/admin/complaints/${complaint.id}`)}>
                      Assign Department
                    </Button>
                  ) : complaint.status === 'assigned' ? (
                    <Button variant="primary" className="w-full">
                      Start Work
                    </Button>
                  ) : complaint.status === 'in_progress' ? (
                    <Button variant="success" className="w-full">
                      Mark Resolved
                    </Button>
                  ) : null}
                  <Button variant="secondary" className="w-full">
                    View in Admin Panel
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Feedback Modal */}
      <Modal
        isOpen={showFeedbackModal}
        onClose={() => setShowFeedbackModal(false)}
        title="Rate Your Experience"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-body text-text-secondary">How satisfied are you with the resolution?</p>
          
          <div className="flex items-center justify-center gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setFeedbackRating(star)}
                className="p-1 text-3xl transition-colors"
                aria-label={`Rate ${star} out of 5 stars`}
              >
                <span className={classNames(
                  feedbackRating >= star ? 'text-amber-400' : 'text-border'
                )}>★</span>
              </button>
            ))}
          </div>
          
          <Textarea
            label="Your Feedback (optional)"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Tell us more about your experience..."
            rows={3}
          />
          
          <div className="flex gap-3">
            <Button variant="secondary" className="flex-1" onClick={() => setShowFeedbackModal(false)}>
              Cancel
            </Button>
            <Button className="flex-1" onClick={handleSubmitFeedback} loading={submittingFeedback} disabled={!feedback.trim() && feedbackRating === 0}>
              Submit Feedback
            </Button>
          </div>
        </div>
      </Modal>
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
    'alert-triangle': AlertTriangle,
    'alert-circle': AlertCircle,
  }
  return icons[name] || FileText
}
