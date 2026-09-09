import { formatDistanceToNow, format } from 'date-fns'

export function formatDate(dateString) {
  if (!dateString) return '—'
  try {
    return format(new Date(dateString), 'MMM d, yyyy')
  } catch {
    return '—'
  }
}

export function formatDateTime(dateString) {
  if (!dateString) return '—'
  try {
    return format(new Date(dateString), 'MMM d, yyyy h:mm a')
  } catch {
    return '—'
  }
}

export function formatRelativeTime(dateString) {
  if (!dateString) return '—'
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true })
  } catch {
    return '—'
  }
}

export function getPriorityConfig(priority) {
  const configs = {
    high: {
      label: 'HIGH',
      icon: 'alert-triangle',
      bg: 'bg-priority-high-bg',
      border: 'border-priority-high-border',
      text: 'text-priority-high-text',
      iconColor: 'text-priority-high-icon',
    },
    medium: {
      label: 'MEDIUM',
      icon: 'alert-circle',
      bg: 'bg-priority-medium-bg',
      border: 'border-priority-medium-border',
      text: 'text-priority-medium-text',
      iconColor: 'text-priority-medium-icon',
    },
    low: {
      label: 'LOW',
      icon: 'info',
      bg: 'bg-priority-low-bg',
      border: 'border-priority-low-border',
      text: 'text-priority-low-text',
      iconColor: 'text-priority-low-icon',
    },
  }
  return configs[priority?.toLowerCase()] || configs.low
}

export function getStatusConfig(status) {
  const configs = {
    submitted: { label: 'Submitted', icon: 'file-text', bg: 'bg-status-submitted-bg', text: 'text-status-submitted-text', border: 'border-status-submitted-border' },
    prioritized: { label: 'Prioritized', icon: 'flag', bg: 'bg-status-prioritized-bg', text: 'text-status-prioritized-text', border: 'border-status-prioritized-border' },
    assigned: { label: 'Assigned', icon: 'user-check', bg: 'bg-status-assigned-bg', text: 'text-status-assigned-text', border: 'border-status-assigned-border' },
    in_progress: { label: 'In Progress', icon: 'loader', bg: 'bg-status-in_progress-bg', text: 'text-status-in_progress-text', border: 'border-status-in_progress-border' },
    resolved: { label: 'Resolved', icon: 'check-circle-2', bg: 'bg-status-resolved-bg', text: 'text-status-resolved-text', border: 'border-status-resolved-border' },
    rejected: { label: 'Rejected', icon: 'x-circle', bg: 'bg-status-rejected-bg', text: 'text-status-rejected-text', border: 'border-status-rejected-border' },
  }
  return configs[status] || configs.submitted
}

export function getCategoryIcon(categoryName) {
  const icons = {
    pothole: 'road',
    garbage: 'trash-2',
    water_leakage: 'droplets',
    streetlight: 'lamp',
    sewage_overflow: 'alert-triangle',
    traffic_signal: 'traffic-light',
    footpath: 'footprints',
    drainage: 'wind',
  }
  return icons[categoryName] || 'alert-circle'
}

export function getCategoryDisplayName(categoryName) {
  const names = {
    pothole: 'Pothole / Road Damage',
    garbage: 'Garbage / Waste',
    water_leakage: 'Water Leakage',
    streetlight: 'Streetlight Issue',
    sewage_overflow: 'Sewage Overflow',
    traffic_signal: 'Traffic Signal',
    footpath: 'Footpath / Sidewalk',
    drainage: 'Drainage / Waterlogging',
  }
  return names[categoryName] || categoryName
}

export function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

export function truncate(str, length = 100) {
  if (!str) return ''
  if (str.length <= length) return str
  return str.slice(0, length).trim() + '…'
}

export function generateAvatarColor(name) {
  const colors = [
    'bg-primary-500', 'bg-emerald-500', 'bg-amber-500', 'bg-rose-500',
    'bg-violet-500', 'bg-cyan-500', 'bg-indigo-500', 'bg-orange-500',
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

export function getInitials(name) {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function debounce(fn, delay) {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

export function formatNumber(num) {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}