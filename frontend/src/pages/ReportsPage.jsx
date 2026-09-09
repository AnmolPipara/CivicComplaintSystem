import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { adminAPI } from '../services/api'
import { Card, CardContent, Select, Button, Alert } from '../components/UI'
import { 
  BarChart3, TrendingUp, Download, RefreshCw, 
  Calendar, FileText, Users, Building2, MapPin, X
} from 'lucide-react'
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, 
  PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { formatDate, formatNumber, classNames } from '../utils/helpers'

const CHART_COLORS = ['#2d8ab4', '#166534', '#ad6800', '#c0152f', '#6b21a8', '#0891b2', '#ea580c', '#65a30d']

export function ReportsPage() {
  const { user, isAdmin } = useAuth()
  const [timeRange, setTimeRange] = useState('30')
  const [loading, setLoading] = useState(true)
  const [resolutionTrend, setResolutionTrend] = useState([])
  const [categoryData, setCategoryData] = useState([])
  const [departmentData, setDepartmentData] = useState([])
  const [priorityData, setPriorityData] = useState([])
  const [error, setError] = useState(null)

  const fetchReports = async () => {
    try {
      setLoading(true)
      const [trend, byCategory, byDept, byPriority] = await Promise.all([
        adminAPI.reports.resolutionTrend(parseInt(timeRange)),
        adminAPI.reports.complaintsByCategory(),
        adminAPI.reports.complaintsByDepartment(),
        adminAPI.reports.priorityDistribution(),
      ])
      setResolutionTrend(trend.data)
      setCategoryData(byCategory.data)
      setDepartmentData(byDept.data)
      setPriorityData(byPriority.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load reports')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReports()
  }, [timeRange])

  if (!isAdmin) {
    return <div className="page-container">Access denied</div>
  }

  const priorityColors = {
    high: '#c0152f',
    medium: '#ad6800',
    low: '#166534',
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-heading-lg font-bold text-text-primary">Reports & Analytics</h1>
          <p className="text-body text-text-secondary mt-1">Track complaint trends and department performance</p>
        </div>
        <div className="flex items-center gap-3">
          <Select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            options={[
              { value: '7', label: 'Last 7 days' },
              { value: '30', label: 'Last 30 days' },
              { value: '90', label: 'Last 90 days' },
              { value: '365', label: 'Last year' },
            ]}
            placeholder="Time range"
            className="w-auto"
          />
          <Button variant="secondary" onClick={fetchReports} loading={loading}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
          <Button variant="secondary">
            <Download className="h-4 w-4" />
            Export PDF
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="danger" className="mb-6" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {loading ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : (
        <>
          {/* Resolution Time Trend */}
          <Card className="mb-6">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-heading-sm font-semibold text-text-primary">Resolution Time Trend</h2>
                <span className="text-body-sm text-text-muted">Average days to resolve</span>
              </div>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={resolutionTrend} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorResolution" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2d8ab4" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#2d8ab4" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fill: '#94a3b8', fontSize: 12 }}
                      tickFormatter={(value) => formatDate(value)}
                    />
                    <YAxis 
                      tick={{ fill: '#94a3b8', fontSize: 12 }}
                      tickFormatter={(value) => `${value.toFixed(1)}d`}
                    />
                    <Tooltip 
                      formatter={(value, name) => [
                        name === 'avg_resolution_days' ? value.toFixed(1) : value,
                        name === 'avg_resolution_days' ? 'Avg Days' : 'Resolved'
                      ]}
                      labelFormatter={(value) => formatDate(value)}
                    />
                    <Area
                      type="monotone"
                      dataKey="avg_resolution_days"
                      stroke="#2d8ab4"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorResolution)"
                    />
                    <Line
                      type="monotone"
                      dataKey="resolved_count"
                      stroke="#166534"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      dot={false}
                      yAxisId="right"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Category & Department Distribution */}
          <div className="grid gap-6 lg:grid-cols-2 mb-6">
            <Card>
              <CardContent className="p-5">
                <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Complaints by Category</h2>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={categoryData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={2}
                        dataKey="count"
                        nameKey="category"
                        label={({ category, count, percent }) => 
                          `${category}: ${count} (${(percent * 100).toFixed(0)}%)`
                        }
                        labelLine={false}
                      >
                        {categoryData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [value, 'complaints']} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-5">
                <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Complaints by Department</h2>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={departmentData} layout="vertical" margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                      <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                      <YAxis 
                        dataKey="department" 
                        type="category" 
                        width={150} 
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                      />
                      <Tooltip formatter={(value) => [value, 'complaints']} />
                      <Bar 
                        dataKey="count" 
                        fill="#2d8ab4" 
                        radius={[0, 4, 4, 0]} 
                        maxBarWidth={40}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Priority Distribution & Status */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardContent className="p-5">
                <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Priority Distribution</h2>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={priorityData}
                        cx="50%"
                        cy="50%"
                        innerRadius={70}
                        outerRadius={100}
                        paddingAngle={3}
                        dataKey="count"
                        nameKey="priority"
                        label={({ priority, count, percent }) => 
                          `${priority.toUpperCase()}: ${count} (${(percent * 100).toFixed(0)}%)`
                        }
                        labelLine={false}
                      >
                        {priorityData.map((item) => (
                          <Cell key={item.priority} fill={priorityColors[item.priority] || CHART_COLORS[0]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [value, 'complaints']} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-5">
                <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Key Metrics Summary</h2>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <MetricCard
                    title="Total Complaints"
                    value={categoryData.reduce((sum, c) => sum + c.count, 0)}
                    icon={FileText}
                    color="#2d8ab4"
                  />
                  <MetricCard
                    title="Categories"
                    value={categoryData.length}
                    icon={FileText}
                    color="#6b21a8"
                  />
                  <MetricCard
                    title="Departments"
                    value={departmentData.length}
                    icon={Building2}
                    color="#0891b2"
                  />
                  <MetricCard
                    title="Avg Resolution"
                    value={`${resolutionTrend.reduce((sum, d) => sum + (d.avg_resolution_days || 0), 0) / Math.max(resolutionTrend.length, 1) || 0}`.toFixed(1)}
                    icon={Calendar}
                    color="#ea580c"
                    suffix=" days"
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}

function CardSkeleton() {
  return (
    <Card className="p-5 h-96">
      <Skeleton variant="text" width="40%" className="mb-4" />
      <Skeleton variant="rectangular" height="300" />
    </Card>
  )
}

function MetricCard({ title, value, icon: Icon, color, suffix = '' }) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-body-sm text-text-secondary">{title}</p>
          <p className="text-heading-md font-bold text-text-primary mt-1">
            {formatNumber(value)}{suffix}
          </p>
        </div>
        <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
          <Icon className="h-5 w-5" style={{ color }} />
        </div>
      </div>
    </Card>
  )
}
