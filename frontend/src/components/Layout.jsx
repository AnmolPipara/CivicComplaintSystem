import React from 'react'
import { Link, useLocation, NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Button } from './UI'
import {
  LayoutDashboard,
  FileText,
  Bell,
  Settings,
  LogOut,
  User,
  BarChart3,
  Users,
  FolderKanban,
  MapPin,
  ChevronDown,
  Menu,
  X,
  Shield,
  Building2,
} from 'lucide-react'
import { classNames } from '../utils/helpers'

const NAV_ITEMS_CITIZEN = [
  { path: '/dashboard', label: 'My Complaints', icon: FileText },
  { path: '/submit', label: 'New Complaint', icon: MapPin },
  { path: '/feed', label: 'Public Feed', icon: FolderKanban },
]

const NAV_ITEMS_ADMIN = [
  { path: '/admin', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/admin/complaints', label: 'All Complaints', icon: FolderKanban },
  { path: '/admin/reports', label: 'Reports', icon: BarChart3 },
  { path: '/admin/categories', label: 'Categories', icon: Settings },
  { path: '/admin/departments', label: 'Departments', icon: Building2 },
  { path: '/admin/clusters', label: 'Clusters', icon: MapPin },
]

const NAV_ITEMS_DEPARTMENT = [
  { path: '/department', label: 'My Queue', icon: FolderKanban },
  { path: '/department/complaints', label: 'Assigned', icon: FileText },
]

export function Header() {
  const { user, logout, isAuthenticated, isAdmin, isDepartment, isCitizen } = useAuth()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false)
  const [userMenuOpen, setUserMenuOpen] = React.useState(false)

  const navItems = isAdmin ? NAV_ITEMS_ADMIN : isDepartment ? NAV_ITEMS_DEPARTMENT : NAV_ITEMS_CITIZEN

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-border">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Main navigation">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to={isAdmin || isDepartment ? '/admin' : '/dashboard'} className="flex items-center gap-2" aria-label="Civic Complaint System Home">
            <div className="w-9 h-9 rounded-lg bg-primary-500 flex items-center justify-center">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <span className="text-heading-sm font-semibold text-text-primary hidden sm:block">
              CivicSense
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path || 
                (item.path !== '/' && location.pathname.startsWith(item.path + '/'))
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => classNames(
                    'flex items-center gap-2 px-3 py-2 rounded-button text-body-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-50 text-primary-600'
                      : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </div>

          {/* Right side actions */}
          <div className="flex items-center gap-3">
            {/* Notifications */}
            {isAuthenticated && (
              <Link to="/notifications" className="relative p-2 rounded-button text-text-secondary hover:bg-surface-hover hover:text-text-primary transition-colors" aria-label="Notifications">
                <Bell className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-[10px] font-medium rounded-full flex items-center justify-center">3</span>
              </Link>
            )}

            {/* User Menu */}
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-1.5 rounded-button hover:bg-surface-hover transition-colors"
                  aria-expanded={userMenuOpen}
                  aria-haspopup="true"
                >
                  <div className={classNames('w-8 h-8 rounded-full flex items-center justify-center font-medium text-white', generateAvatarColor(user?.full_name || 'User'))}>
                    {getInitials(user?.full_name || 'User')}
                  </div>
                  <span className="hidden sm:block text-body-sm font-medium text-text-primary">{user?.full_name}</span>
                  <ChevronDown className="h-4 w-4 text-text-muted" />
                </button>

                {userMenuOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-card shadow-elevated border border-border overflow-hidden z-50 animate-fade-in">
                      <div className="px-4 py-3 border-b border-border">
                        <p className="text-body-sm font-medium text-text-primary">{user?.full_name}</p>
                        <p className="text-caption text-text-muted">{user?.email}</p>
                        <span className="mt-1 inline-block px-2 py-0.5 text-caption font-medium rounded-full bg-primary-100 text-primary-700 capitalize">{user?.role}</span>
                      </div>
                      <NavLink
                        to="/profile"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-3 px-4 py-2.5 text-body-sm text-text-secondary hover:bg-surface-hover"
                      >
                        <User className="h-4 w-4" />
                        Profile
                      </NavLink>
                      <NavLink
                        to="/settings"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-3 px-4 py-2.5 text-body-sm text-text-secondary hover:bg-surface-hover"
                      >
                        <Settings className="h-4 w-4" />
                        Settings
                      </NavLink>
                      <hr className="my-1 border-border" />
                      <button
                        onClick={logout}
                        className="flex items-center gap-3 w-full px-4 py-2.5 text-body-sm text-red-600 hover:bg-red-50"
                      >
                        <LogOut className="h-4 w-4" />
                        Sign Out
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="hidden sm:flex sm:items-center sm:gap-2">
                <Link to="/login" className="btn-ghost text-body-sm">Sign In</Link>
                <Link to="/register" className="btn-primary text-body-sm">Get Started</Link>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-button text-text-secondary hover:bg-surface-hover hover:text-text-primary"
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-menu"
              aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div id="mobile-menu" className="md:hidden py-4 border-t border-border animate-slide-up">
            <div className="flex flex-col gap-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={classNames(
                      'flex items-center gap-3 px-3 py-2.5 rounded-button text-body font-medium',
                      isActive
                        ? 'bg-primary-50 text-primary-600'
                        : 'text-text-secondary hover:bg-surface-hover'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    {item.label}
                  </NavLink>
                )
              })}
              <hr className="my-3 border-border" />
              {isAuthenticated ? (
                <button onClick={logout} className="flex items-center gap-3 px-3 py-2.5 text-body font-medium text-red-600 hover:bg-red-50 rounded-button">
                  <LogOut className="h-5 w-5" />
                  Sign Out
                </button>
              ) : (
                <div className="flex flex-col gap-2 pt-2">
                  <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="btn-secondary w-full justify-center">Sign In</Link>
                  <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="btn-primary w-full justify-center">Get Started</Link>
                </div>
              )}
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}

function generateAvatarColor(name) {
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

function getInitials(name) {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}