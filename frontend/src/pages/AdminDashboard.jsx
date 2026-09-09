import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { adminAPI, complaintAPI } from '../services/api'
import { 
  Card, CardContent, Badge, PriorityBadge, StatusBadge, Button, 
  Select, Input, Modal, Alert, EmptyState, LoadingState, Skeleton 
} from '../components/UI'
import {
  LayoutDashboard, FileText, Users, TrendingUp, AlertTriangle,
  Clock, CheckCircle2, Filter, X, MoreVertical, Edit, Trash2,
  ArrowUpDown, Download, BarChart3, Building2, MapPin, FolderKanban,
  Settings, ChevronLeft, ChevronRight
} from 'lucide-react'
import { formatDate, formatRelativeTime, getStatusConfig, classNames, truncate, formatNumber } from '../utils/helpers'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts'

const STATUS_ORDER = ['submitted', 'prioritized', 'assigned', 'in_progress', 'resolved', 'rejected']

export function AdminDashboard() {
  const { user, isAdmin } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [complaints, setComplaints] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    category_id: '',
    department_id: '',
    search: '',
    sort_by: 'priority_score',
    sort_order: 'desc',
  })
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [categories, setCategories] = useState([])
  const [departments, setDepartments] = useState([])
  const pageSize = 20
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [selectedComplaint, setSelectedComplaint] = useState(null)
  const [assignDeptId, setAssignDeptId] = useState('')

  const fetchStats = async () => {
    try {
      const response = await adminAPI.stats()
      setStats(response.data)
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  const fetchComplaints = async () => {
    try {
      setLoading(true)
      const params = { page, page_size: pageSize, ...filters }
      const response = await adminAPI.complaints(params)
      setComplaints(response.data.complaints)
      setTotal(response.data.total)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load complaints')
    } finally {
      setLoading(false)
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await adminAPI.categories()
      setCategories(response.data)
    } catch (err) {
      console.error('Failed to fetch categories:', err)
    }
  }

  const fetchDepartments = async () => {
    try {
      const response = await adminAPI.departments()
      setDepartments(response.data)
    } catch (err) {
      console.error('Failed to fetch departments:', err)
    }
  }

  useEffect(() => {
    fetchStats()
    fetchComplaints()
    fetchCategories()
    fetchDepartments()
  }, [page, filters])

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
    setPage(1)
  }

  const clearFilters = () => {
    setFilters({
      status: '',
      priority: '',
      category_id: '',
      department_id: '',
      search: '',
      sort_by: 'priority_score',
      sort_order: 'desc',
    })
    setPage(1)
  }

  const hasActiveFilters = filters.status || filters.priority || filters.category_id || filters.department_id || filters.search

  const handleAssign = async (complaint) => {
    setSelectedComplaint(complaint)
    setAssignDeptId('')
    setShowAssignModal(true)
  }

  const confirmAssign = async () => {
    if (!selectedComplaint || !assignDeptId) return
    try {
      await adminAPI.assign(selectedComplaint.id, parseInt(assignDeptId))
      fetchComplaints()
      fetchStats()
      setShowAssignModal(false)
      setSelectedComplaint(null)
    } catch (err) {
      console.error('Assign failed:', err)
    }
  }

  const handleResolve = async (complaintId) => {
    if (!window.confirm('Mark this complaint as resolved?')) return
    try {
      await adminAPI.resolve(complaintId)
      fetchComplaints()
      fetchStats()
    } catch (err) {
      console.error('Resolve failed:', err)
    }
  }

  const handleUndo = async (complaintId) => {
    if (!window.confirm('Undo the last action on this complaint?')) return
    try {
      await adminAPI.undo(complaintId)
      fetchComplaints()
      fetchStats()
    } catch (err) {
      console.error('Undo failed:', err)
    }
  }

  if (!isAdmin) {
    return <div className="page-container">Access denied</div>
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-heading-lg font-bold text-text-primary">Admin Dashboard</h1>
          <p className="text-body text-text-secondary mt-1">Manage and monitor civic complaints</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={fetchComplaints}>
            <Icon name="refresh" className="h-4 w-4" />
            Refresh
          </Button>
          <Button variant="primary" onClick={() => navigate('/admin/reports')}>
            <BarChart3 className="h-4 w-4" />
            View Reports
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6">
          <StatCard
            title="Open Complaints"
            value={stats.open_complaints}
            icon={FileText}
            iconColor="text-primary-500"
            bgColor="bg-primary-50"
            trend={stats.resolved_this_week > 0 ? `+${stats.resolved_this_week} resolved this week` : null}
            trendColor="text-green-600"
          />
          <StatCard
            title="High Priority"
            value={stats.high_priority}
            icon={AlertTriangle}
            iconColor="text-red-500"
            bgColor="bg-red-50"
            trend="Requires immediate attention"
            trendColor="text-red-600"
          />
          <StatCard
            title="Resolved This Week"
            value={stats.resolved_this_week}
            icon={CheckCircle2}
            iconColor="text-green-500"
            bgColor="bg-green-50"
            trend={`Avg ${stats.avg_resolution_days} days to resolve`}
            trendColor="text-text-muted"
          />
          <StatCard
            title="Avg Resolution Time"
            value={`${stats.avg_resolution_days} days`}
            icon={Clock}
            iconColor="text-amber-500"
            bgColor="bg-amber-50"
            trend="Target: < 7 days"
            trendColor="text-text-muted"
          />
        </div>
      )}

      {/* Charts Row */}
      {stats && (
        <div className="grid gap-6 lg:grid-cols-2 mb-6">
          <Card>
            <CardContent className="p-5">
              <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Complaints by Category</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={stats.by_category}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="count"
                      nameKey="category"
                      label={({ category, count, percent }) => `${category}: ${count} (${(percent * 100).toFixed(0)}%)`}
                      labelLine={false}
                    >
                      {stats.by_category.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [value, 'complaints']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-5">
              <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Complaints by Status</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats.by_status} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis dataKey="status" type="category" width={120} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <Tooltip formatter={(value) => [value, 'complaints']} />
                    <Bar dataKey="count" fill="#2d8ab4" radius={[0, 4, 4, 0]} maxBarWidth={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-text-muted" />
              <span className="text-body-sm font-medium text-text-secondary">Filters:</span>
            </div>
            <div className="flex flex-wrap gap-3 flex-1">
              <input
                type="text"
                placeholder="Search complaints..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="input flex-1 min-w-[200px]"
                aria-label="Search complaints"
              />
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
                value={filters.category_id}
                onChange={(e) => handleFilterChange('category_id', e.target.value)}
                className="input w-auto"
                aria-label="Filter by category"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>{cat.display_name}</option>
                ))}
              </select>
              <select
                value={filters.department_id}
                onChange={(e) => handleFilterChange('department_id', e.target.value)}
                className="input w-auto"
                aria-label="Filter by department"
              >
                <option value="">All Departments</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>{dept.display_name}</option>
                ))}
              </select>
              <select
                value={filters.sort_by}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                className="input w-auto"
                aria-label="Sort by"
              >
                <option value="priority_score">Priority Score</option>
                <option value="created_at">Date Created</option>
                <option value="upvote_count">Upvotes</option>
                <option value="status">Status</option>
              </select>
              <select
                value={filters.sort_order}
                onChange={(e) => handleFilterChange('sort_order', e.target.value)}
                className="input w-auto"
                aria-label="Sort order"
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
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

      {/* Complaints Table */}
      {error && (
        <Alert variant="danger" className="mb-6" dismissible onClose={() => setError('')}>
          {error}
          <Button variant="ghost" size="sm" onClick={fetchComplaints}>Retry</Button>
        </Alert>
      )}

      {loading && complaints.length === 0 ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <Card key={i} className="p-4">
              <div className="flex items-center gap-4">
                <Skeleton variant="circular" width="40" height="40" />
                <div className="flex-1 space-y-2">
                  <Skeleton variant="text" width="40%" />
                  <Skeleton variant="text" width="60%" />
                </div>
                <Skeleton variant="text" width="80px" />
              </div>
            </Card>
          ))}
        </div>
      ) : complaints.length === 0 ? (
        <EmptyState
          icon={FolderKanban}
          title="No complaints found"
          description="No complaints match your current filters. Try adjusting your search criteria."
          action={<Button variant="ghost" onClick={clearFilters}>Clear Filters</Button>}
        />
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full" role="table">
              <thead>
                <tr className="border-b border-border text-left text-body-sm font-medium text-text-muted">
                  <th className="pb-3 px-4">Complaint</th>
                  <th className="pb-3 px-4 hidden md:table-cell">Category</th>
                  <th className="pb-3 px-4 hidden lg:table-cell">Location</th>
                  <th className="pb-3 px-4">Priority</th>
                  <th className="pb-3 px-4">Status</th>
                  <th className="pb-3 px-4 hidden md:table-cell">Department</th>
                  <th className="pb-3 px-4">Submitted</th>
                  <th className="pb-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {complaints.map((complaint) => (
                  <tr key={complaint.id} className="hover:bg-surface-hover transition-colors">
                    <td className="py-4 px-4">
                      <div>
                        <p className="font-medium text-text-primary">#{complaint.id}</p>
                        <p className="text-body-sm text-text-secondary line-clamp-1 max-w-xs">
                          {truncate(complaint.description, 80)}
                        </p>
                      </div>
                    </td>
                    <td className="py-4 px-4 hidden md:table-cell">
                      <Badge variant="primary">{complaint.category?.display_name}</Badge>
                    </td>
                    <td className="py-4 px-4 hidden lg:table-cell">
                      <p className="text-body-sm text-text-secondary max-w-xs truncate">
                        {complaint.location?.area_name || complaint.location?.address || '—'}
                      </p>
                    </td>
                    <td className="py-4 px-4">
                      <PriorityBadge priority={complaint.priority} size="sm" />
                    </td>
                    <td className="py-4 px-4">
                      <StatusBadge status={complaint.status} size="sm" />
                    </td>
                    <td className="py-4 px-4 hidden md:table-cell">
                      <span className="text-body-sm text-text-secondary">
                        {complaint.department?.display_name || 'Unassigned'}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className="text-body-sm text-text-secondary">
                        {formatRelativeTime(complaint.created_at)}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" onClick={() => navigate(`/admin/complaints/${complaint.id}`)}>
                          View
                        </Button>
                        {complaint.status !== 'resolved' && complaint.status !== 'rejected' && (
                          <>
                            {!complaint.department_id && (
                              <Button variant="secondary" size="sm" onClick={() => handleAssign(complaint)}>
                                Assign
                              </Button>
                            )}
                            {complaint.status === 'in_progress' && (
                              <Button variant="success" size="sm" onClick={() => handleResolve(complaint.id)}>
                                Resolve
                              </Button>
                            )}
                            {complaint.status !== 'submitted' && (
                              <Button variant="ghost" size="sm" onClick={() => handleUndo(complaint.id)}>
                                Undo
                              </Button>
                            )}
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {total > pageSize && (
            <div className="mt-6 flex items-center justify-between">
              <span className="text-body-sm text-text-secondary">
                Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} complaints
              </span>
              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="px-3 text-body-sm text-text-secondary">
                  Page {page} of {Math.ceil(total / pageSize)}
                </span>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(Math.ceil(total / pageSize), p + 1))}
                  disabled={page === Math.ceil(total / pageSize)}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Assign Modal */}
      <Modal
        isOpen={showAssignModal}
        onClose={() => { setShowAssignModal(false); setSelectedComplaint(null); }}
        title="Assign Department"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-body text-text-secondary">
            Assign complaint <strong>#{selectedComplaint?.id}</strong> to a department:
          </p>
          <Select
            label="Department"
            options={departments.map(d => ({ value: d.id, label: d.display_name }))}
            placeholder="Select department"
            value={assignDeptId}
            onChange={(e) => setAssignDeptId(e.target.value)}
          />
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="secondary" onClick={() => { setShowAssignModal(false); setSelectedComplaint(null); }}>
              Cancel
            </Button>
            <Button onClick={confirmAssign} disabled={!assignDeptId}>
              Assign
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

function StatCard({ title, value, icon: Icon, iconColor, bgColor, trend, trendColor }) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-body-sm text-text-secondary">{title}</p>
          <p className="text-heading-lg font-bold text-text-primary mt-1">{formatNumber(value)}</p>
          {trend && (
            <p className={classNames('text-body-sm mt-1', trendColor)}>{trend}</p>
          )}
        </div>
        <div className={classNames('w-12 h-12 rounded-lg flex items-center justify-center', bgColor)}>
          <Icon className={classNames('h-6 w-6', iconColor)} />
        </div>
      </div>
    </Card>
  )
}

const CHART_COLORS = ['#2d8ab4', '#166534', '#ad6800', '#c0152f', '#6b21a8', '#0891b2', '#ea580c', '#65a30d']

function Icon({ name, className }) {
  const icons = {
    refresh: RefreshIcon,
    FileText,
    AlertTriangle,
    CheckCircle2,
    Clock,
  }
  const Component = icons[name]
  return Component ? <Component className={className} /> : null
}

function RefreshIcon({ className }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M23 4v6h-6"/><path d="M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
}