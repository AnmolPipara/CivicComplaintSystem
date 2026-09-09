import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { complaintAPI } from '../services/api'
import { Button, Card, CardContent, Badge, PriorityBadge, StatusBadge, EmptyState, LoadingState, Skeleton } from '../components/UI'
import { Plus, FileText, Clock, MapPin, ChevronRight, RefreshCw, Filter, X, Flag, UserCheck, Loader, CheckCircle2, XCircle, AlertCircle } from 'lucide-react'
import { formatRelativeTime, formatDate, getStatusConfig, classNames, truncate } from '../utils/helpers'

const STATUS_ORDER = ['submitted', 'prioritized', 'assigned', 'in_progress', 'resolved', 'rejected']

export function CitizenDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [complaints, setComplaints] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ status: '', priority: '' })
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 10

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
    setFilters({ status: '', priority: '' })
    setPage(1)
  }

  const hasActiveFilters = filters.status || filters.priority

  if (loading && complaints.length === 0) {
    return (
      <div className="page-container">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-heading-lg font-bold text-text-primary">My Complaints</h1>
            <p className="text-body text-text-secondary mt-1">Track the status of your civic complaints</p>
          </div>
          <Link to="/submit" className="btn-primary">
            <Plus className="h-4 w-4" />
            New Complaint
          </Link>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
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

  const getStatusStep = (status) => STATUS_ORDER.indexOf(status)

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-heading-lg font-bold text-text-primary">My Complaints</h1>
          <p className="text-body text-text-secondary mt-1">Track the status of your civic complaints</p>
        </div>
        <Link to="/submit" className="btn-primary">
          <Plus className="h-4 w-4" />
          New Complaint
        </Link>
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
                className="input w-auto px-3 py-2 text-body-sm"
                aria-label="Filter by status"
              >
                <option value="">All Status</option>
                {STATUS_ORDER.map((status) => {
                  const config = getStatusConfig(status)
                  return (
                    <option key={status} value={status}>
                      {config.label}
                    </option>
                  )
                })}
              </select>
              <select
                value={filters.priority}
                onChange={(e) => handleFilterChange('priority', e.target.value)}
                className="input w-auto px-3 py-2 text-body-sm"
                aria-label="Filter by priority"
              >
                <option value="">All Priorities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
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

      {/* Complaints List */}
      {error && (
        <Card className="mb-6 border-red-200 bg-red-50">
          <CardContent className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3 text-red-700">
              <AlertCircle className="h-5 w-5" />
              <span>{error}</span>
            </div>
            <Button variant="ghost" size="sm" onClick={fetchComplaints}>
              <RefreshCw className="h-4 w-4" />
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {complaints.length === 0 && !error && (
        <EmptyState
          icon={FileText}
          title="No complaints yet"
          description="You haven't submitted any complaints. Start by reporting a civic issue in your area."
          action={
            <Link to="/submit" className="btn-primary">
              <Plus className="h-4 w-4" />
              File Your First Complaint
            </Link>
          }
        />
      )}

      {complaints.length > 0 && (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {complaints.map((complaint) => (
              <ComplaintCard key={complaint.id} complaint={complaint} />
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

function ComplaintCard({ complaint }) {
  const config = getStatusConfig(complaint.status)
  const IconComponent = getIconComponent(config.icon)
  const statusStep = STATUS_ORDER.indexOf(complaint.status)
  const totalSteps = STATUS_ORDER.length
  const progress = ((statusStep + 1) / totalSteps) * 100

  return (
    <Card className="overflow-hidden hover:shadow-card-hover transition-shadow">
      <div className="p-4">
        {/* Header with priority and status */}
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

        {/* Meta info */}
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

        {/* Progress indicator */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-caption text-text-muted mb-1.5">
            <span>Progress</span>
            <span className="font-medium text-text-secondary">{config.label}</span>
          </div>
          <div className="h-1.5 bg-surface-elevated rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between mt-1.5">
            {STATUS_ORDER.slice(0, statusStep + 1).map((step, idx) => (
              <div
                key={step}
                className={classNames(
                  'flex flex-col items-center gap-1',
                  idx <= statusStep ? 'text-primary-500' : 'text-text-muted'
                )}
              >
                <div
                  className={classNames(
                    'w-2 h-2 rounded-full border-2 transition-colors',
                    idx < statusStep ? 'bg-primary-500 border-primary-500' :
                    idx === statusStep ? 'bg-primary-500 border-primary-500' :
                    'bg-white border-border'
                  )}
                />
                <span className="text-[10px] font-medium truncate w-20 text-center">
                  {getStatusConfig(step).label}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer actions */}
        <div className="flex items-center justify-between pt-3 border-t border-border">
          <Link
            to={`/complaint/${complaint.id}`}
            className="btn-ghost text-body-sm gap-1"
          >
            View Details
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
          <StatusBadge status={complaint.status} size="sm" />
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
