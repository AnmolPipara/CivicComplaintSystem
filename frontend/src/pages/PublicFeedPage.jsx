import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { complaintAPI } from '../services/api'
import { Card, PriorityBadge, StatusBadge, Badge, EmptyState, LoadingState, Skeleton, Button } from '../components/UI'
import { MapPin, Clock, ThumbsUp, ChevronRight, Filter, X, Eye, Share2, Heart, FileText, Flag, UserCheck, Loader, CheckCircle2, XCircle, Plus } from 'lucide-react'
import { formatRelativeTime, getStatusConfig, classNames, truncate } from '../utils/helpers'

const STATUS_ORDER = ['submitted', 'prioritized', 'assigned', 'in_progress', 'resolved', 'rejected']

export function PublicFeedPage() {
  const { user, isAuthenticated } = useAuth()
  const [complaints, setComplaints] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ status: '', priority: '', category: '' })
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 12
  const [upvoting, setUpvoting] = useState({})

  const fetchComplaints = async () => {
    try {
      setLoading(true)
      const params = { page, page_size: pageSize, ...filters }
      const response = await complaintAPI.list(params)
      setComplaints(response.data.complaints)
      setTotal(response.data.total)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load complaints')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchComplaints()
  }, [page, filters])

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
    setPage(1)
  }

  const clearFilters = () => {
    setFilters({ status: '', priority: '', category: '' })
    setPage(1)
  }

  const handleUpvote = async (complaintId) => {
    if (!isAuthenticated) {
      alert('Please sign in to upvote complaints')
      return
    }
    if (upvoting[complaintId]) return
    
    setUpvoting((prev) => ({ ...prev, [complaintId]: true }))
    try {
      await complaintAPI.upvote(complaintId)
      setComplaints((prev) => prev.map((c) => 
        c.id === complaintId ? { ...c, upvote_count: c.upvote_count + 1, user_voted: true } : c
      ))
    } catch (err) {
      console.error('Upvote failed:', err)
    } finally {
      setUpvoting((prev) => ({ ...prev, [complaintId]: false }))
    }
  }

  const hasActiveFilters = filters.status || filters.priority || filters.category

  if (loading && complaints.length === 0) {
    return (
      <div className="page-container">
        <div className="mb-6">
          <h1 className="text-heading-lg font-bold text-text-primary">Public Complaint Feed</h1>
          <p className="text-body text-text-secondary mt-1">Browse and support civic complaints in your community</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="p-5">
              <Skeleton variant="text" width="60%" />
              <Skeleton variant="text" width="40%" className="mt-2" />
              <Skeleton variant="rectangular" height="80px" className="mt-4" />
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-heading-lg font-bold text-text-primary">Public Complaint Feed</h1>
          <p className="text-body text-text-secondary mt-1">Browse and support civic complaints in your community</p>
        </div>
        {isAuthenticated && (
          <Link to="/submit" className="btn-primary">
            <Plus className="h-4 w-4" />
            Report Issue
          </Link>
        )}
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-text-muted" />
              <span className="text-body-sm font-medium text-text-secondary">Filters:</span>
            </div>
            <div className="flex flex-wrap gap-3">
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="input w-auto"
                aria-label="Filter by status"
              >
                <option value="">All Status</option>
                {STATUS_ORDER.map((status) => {
                  const config = getStatusConfig(status)
                  return <option key={status} value={status}>{config.label}</option>
                })}
              </select>
              <select
                value={filters.priority}
                onChange={(e) => handleFilterChange('priority', e.target.value)}
                className="input w-auto"
                aria-label="Filter by priority"
              >
                <option value="">All Priorities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="input w-auto"
                aria-label="Filter by category"
              >
                <option value="">All Categories</option>
                <option value="pothole">Pothole / Road Damage</option>
                <option value="garbage">Garbage / Waste</option>
                <option value="water_leakage">Water Leakage</option>
                <option value="streetlight">Streetlight Issue</option>
                <option value="sewage_overflow">Sewage Overflow</option>
                <option value="traffic_signal">Traffic Signal</option>
                <option value="footpath">Footpath / Sidewalk</option>
                <option value="drainage">Drainage / Waterlogging</option>
              </select>
              {hasActiveFilters && (
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  <X className="h-3.5 w-3.5" />
                  Clear
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="danger" className="mb-6" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {complaints.length === 0 && !error && (
        <EmptyState
          icon={Eye}
          title="No complaints found"
          description="No complaints match your current filters. Try adjusting your search criteria."
          action={<Button variant="ghost" onClick={clearFilters}>Clear Filters</Button>}
        />
      )}

      {complaints.length > 0 && (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {complaints.map((complaint) => (
              <PublicComplaintCard
                key={complaint.id}
                complaint={complaint}
                onUpvote={() => handleUpvote(complaint.id)}
                upvoting={upvoting[complaint.id]}
                isAuthenticated={isAuthenticated}
              />
            ))}
          </div>

          {/* Pagination */}
          {total > pageSize && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <span className="text-body-sm text-text-secondary">
                Page {page} of {Math.ceil(total / pageSize)}
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage((p) => Math.min(Math.ceil(total / pageSize), p + 1))}
                disabled={page === Math.ceil(total / pageSize)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function PublicComplaintCard({ complaint, onUpvote, upvoting, isAuthenticated }) {
  const config = getStatusConfig(complaint.status)
  const IconComponent = getIconComponent(config.icon)

  return (
    <Card className="overflow-hidden hover:shadow-card-hover transition-shadow h-full flex flex-col">
      <div className="p-4 flex-1">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-body font-semibold text-text-primary line-clamp-1">
              {complaint.category?.display_name || complaint.category_id}
            </h3>
            <p className="text-body-sm text-text-secondary mt-0.5 line-clamp-2">
              {truncate(complaint.description, 120)}
            </p>
          </div>
          <PriorityBadge priority={complaint.priority} size="sm" />
        </div>

        {/* Meta */}
        <div className="flex flex-wrap items-center gap-3 text-body-sm text-text-secondary mb-3">
          <span className="flex items-center gap-1">
            <MapPin className="h-3.5 w-3.5" />
            {complaint.location?.area_name || complaint.location?.address || 'Unknown location'}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" />
            {formatRelativeTime(complaint.created_at)}
          </span>
        </div>

        {/* Progress */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-caption text-text-muted mb-1.5">
            <span>Status Progress</span>
            <StatusBadge status={complaint.status} size="sm" />
          </div>
          <div className="h-1.5 bg-surface-elevated rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 transition-all duration-500"
              style={{ width: `${((STATUS_ORDER.indexOf(complaint.status) + 1) / STATUS_ORDER.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-border">
          <Link
            to={`/complaint/${complaint.id}`}
            className="btn-ghost text-body-sm gap-1"
          >
            <Eye className="h-3.5 w-3.5" />
            View Details
          </Link>
          <button
            onClick={onUpvote}
            disabled={upvoting || !isAuthenticated}
            className={classNames(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-button text-body-sm font-medium transition-colors',
              complaint.user_voted
                ? 'bg-primary-50 text-primary-600 border-primary-200'
                : 'bg-surface-elevated text-text-secondary border-border hover:bg-surface-hover'
            )}
            aria-label={complaint.user_voted ? 'Remove upvote' : 'Upvote'}
            aria-pressed={complaint.user_voted}
          >
            <ThumbsUp className={classNames('h-4 w-4', complaint.user_voted ? 'text-primary-500' : '')} />
            <span>{complaint.upvote_count}</span>
          </button>
        </div>
      </div>
    </Card>
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
  }
  return icons[name] || FileText
}
