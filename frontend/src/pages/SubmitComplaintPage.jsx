import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { complaintAPI } from '../services/api'
import { useForm } from '../hooks/useForm'
import { Button, Input, Textarea, Card, CardContent, Alert, Badge } from '../components/UI'
import { Camera, X, CheckCircle2, ArrowRight } from 'lucide-react'
import { classNames, formatErrorMessage } from '../utils/helpers'
import { MapPicker } from '../components/MapPicker'

const CATEGORIES = [
  { value: 1, label: 'Pothole / Road Damage', icon: 'road' },
  { value: 2, label: 'Garbage / Waste', icon: 'trash-2' },
  { value: 3, label: 'Water Leakage', icon: 'droplets' },
  { value: 4, label: 'Streetlight Issue', icon: 'lamp' },
  { value: 5, label: 'Sewage Overflow', icon: 'alert-triangle' },
  { value: 6, label: 'Traffic Signal', icon: 'traffic-light' },
  { value: 7, label: 'Footpath / Sidewalk', icon: 'footprints' },
  { value: 8, label: 'Drainage / Waterlogging', icon: 'wind' },
]

export function SubmitComplaintPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [previewImages, setPreviewImages] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const fileInputRef = useRef(null)

  const { values, errors, handleChange, handleBlur, handleSubmit, setFieldValue } = useForm({
    initialValues: {
      description: '',
      category_id: '',
      location: '',
      latitude: null,
      longitude: null,
      evidence_files: [],
    },
    validate: (values) => {
      const errs = {}
      if (!values.description.trim()) errs.description = 'Description is required'
      else if (values.description.length < 20) errs.description = 'Description must be at least 20 characters'
      if (!values.category_id) errs.category_id = 'Please select a category'
      if (!values.location.trim()) errs.location = 'Please enter a location'
      return errs
    },
    onSubmit: async (values) => {
      setError('')
      setSubmitting(true)
      try {
        const formData = new FormData()
        formData.append('description', values.description)
        formData.append('category_id', values.category_id)
        formData.append('location', values.location)
        if (values.latitude && values.longitude) {
          formData.append('latitude', values.latitude)
          formData.append('longitude', values.longitude)
        }
        
        previewImages.forEach((file) => {
          formData.append('evidence_files', file.file)
        })

        await complaintAPI.create(formData)
        setSuccess(true)
        setTimeout(() => navigate('/dashboard'), 2000)
      } catch (err) {
        setError(formatErrorMessage(err, 'Failed to submit complaint. Please try again.'))
      } finally {
        setSubmitting(false)
      }
    },
  })

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files)
    const validFiles = files.filter(f => f.type.startsWith('image/') && f.size <= 5 * 1024 * 1024)
    
    if (validFiles.length !== files.length) {
      setError('Some files were rejected. Only images up to 5MB are allowed.')
    }
    
    const newPreviews = validFiles.map(file => ({
      file,
      url: URL.createObjectURL(file),
    }))
    
    setPreviewImages((prev) => [...prev, ...newPreviews].slice(0, 5))
    fileInputRef.current.value = ''
  }

  const removeImage = (index) => {
    setPreviewImages((prev) => prev.filter((_, i) => i !== index))
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-surface-elevated bg-mesh">
        <Card className="w-full max-w-md text-center p-8 shadow-elevated">
          <div className="w-14 h-14 rounded-xl bg-emerald-500/15 border border-emerald-500/20 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="h-7 w-7 text-emerald-400" />
          </div>
          <h2 className="text-heading-md font-bold text-text-primary mb-2 tracking-tight">Complaint Submitted!</h2>
          <p className="text-body-sm text-text-secondary">Your complaint has been received and is being processed.</p>
          <Button onClick={() => navigate('/dashboard')} className="mt-6 w-full">
            View Dashboard
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface-elevated bg-mesh">
      <div className="max-w-4xl mx-auto px-4 py-6">
        {error && (
          <Alert variant="danger" className="mb-6" dismissible onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6" noValidate>
          {/* Step 1: Category Selection */}
          <Card>
            <CardContent className="p-5">
              <h2 className="text-heading-sm font-semibold text-text-primary mb-4">What type of issue?</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat.value}
                    type="button"
                    onClick={() => setFieldValue('category_id', cat.value)}
                    className={classNames(
                      'relative p-4 rounded-button border-2 transition-all duration-200 text-left',
                      values.category_id === cat.value
                        ? 'border-primary-500 bg-primary-500/10 shadow-glow-primary'
                        : 'border-border-strong hover:border-primary-500/30 hover:bg-surface-hover'
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <div className={classNames(
                        'w-10 h-10 rounded-lg flex items-center justify-center',
                        values.category_id === cat.value ? 'bg-primary-500' : 'bg-surface-hover/50'
                      )}>
                        <CategoryIcon name={cat.icon} className={classNames('h-5 w-5', values.category_id === cat.value ? 'text-white' : 'text-text-secondary')} />
                      </div>
                      <span className="text-body-sm font-medium text-text-primary">{cat.label}</span>
                    </div>
                    {values.category_id === cat.value && (
                      <CheckCircle2 className="absolute top-2 right-2 h-5 w-5 text-primary-500" />
                    )}
                  </button>
                ))}
              </div>
              {errors.category_id && (
                <p className="mt-2 text-body-sm text-red-600" role="alert">{errors.category_id}</p>
              )}
            </CardContent>
          </Card>

          {/* Step 2: Location */}
          <Card>
            <CardContent className="p-5">
              <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Where is the issue?</h2>
              <div className="space-y-4">
                <Input
                  label="Location Description"
                  name="location"
                  value={values.location}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={errors.location}
                  placeholder="Enter the location details (e.g. Near Central Park, Main Street)"
                />
                
                <div>
                  <label className="block text-body-sm font-medium text-text-secondary mb-1">
                    Pinpoint on Map (Optional)
                  </label>
                  <MapPicker 
                    value={{ lat: values.latitude, lng: values.longitude, address: values.location }} 
                    onChange={(pos) => {
                      setFieldValue('latitude', pos.lat);
                      setFieldValue('longitude', pos.lng);
                      if (pos.address) {
                        setFieldValue('location', pos.address);
                      }
                    }} 
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Step 3: Description */}
          <Card>
            <CardContent className="p-5">
              <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Describe the issue</h2>
              <Textarea
                label="Description"
                name="description"
                value={values.description}
                onChange={handleChange}
                onBlur={handleBlur}
                error={errors.description}
                placeholder="Provide a detailed description of the issue. Include relevant details like when you noticed it, any safety concerns, and specific landmarks..."
                rows={5}
              />
              <div className="flex justify-end text-caption text-text-muted mt-1">
                {values.description.length}/5000 characters
              </div>
            </CardContent>
          </Card>

          {/* Step 4: Evidence Upload */}
          <Card>
            <CardContent className="p-5">
              <h2 className="text-heading-sm font-semibold text-text-primary mb-4">Add photos (optional)</h2>
              <div className="border-2 border-dashed border-border rounded-card p-6">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageUpload}
                  className="hidden"
                  id="evidence-upload"
                  disabled={previewImages.length >= 5}
                />
                <label
                  htmlFor="evidence-upload"
                  className={classNames(
                    'flex flex-col items-center justify-center cursor-pointer',
                    previewImages.length >= 5 && 'opacity-50 cursor-not-allowed'
                  )}
                >
                  <Camera className="h-10 w-10 text-text-muted mb-3" />
                  <p className="text-body text-text-secondary text-center">
                    {previewImages.length > 0
                      ? `${previewImages.length}/5 photos added. Click to add more.`
                      : 'Click or drag photos here (max 5, 5MB each)'}
                  </p>
                </label>
              </div>

              {previewImages.length > 0 && (
                <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3">
                  {previewImages.map((img, index) => (
                    <div key={index} className="relative aspect-square rounded-button overflow-hidden border border-border">
                      <img src={img.url} alt={`Evidence ${index + 1}`} className="w-full h-full object-cover" />
                      <button
                        type="button"
                        onClick={() => removeImage(index)}
                        className="absolute top-1 right-1 w-6 h-6 rounded-full bg-black/60 text-white flex items-center justify-center hover:bg-black/80 transition-colors"
                        aria-label="Remove photo"
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Submit */}
          <div className="flex gap-3">
            <Button type="submit" className="flex-1" size="lg" loading={submitting} disabled={submitting}>
              Submit Complaint
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button type="button" variant="secondary" className="flex-1" onClick={() => navigate('/dashboard')}>
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

function CategoryIcon({ name, className }) {
  const icons = {
    road: RoadIcon,
    'trash-2': TrashIcon,
    droplets: DropletsIcon,
    lamp: LampIcon,
    'alert-triangle': AlertTriangleIcon,
    'traffic-light': TrafficLightIcon,
    footprints: FootprintsIcon,
    wind: WindIcon,
  }
  const Icon = icons[name] || AlertCircleIcon
  return <Icon className={className} />
}

function RoadIcon({ className }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><line x1="12" y1="2" x2="12" y2="22"/></svg>
}
function TrashIcon({ className }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
}
function DropletsIcon({ className }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2.69a5.5 5.5 0 0 1 10.24 3.6 4.5 4.5 0 0 0-8.48 5.88 5.5 5.5 0 0 1 8.48-5.88 4.5 4.5 0 0 0-10.24 0 5.5 5.5 0 0 1 10.24 3.6z"/><path d="M6 17.31a5.5 5.5 0 0 1 10.24-3.6 4.5 4.5 0 0 0 8.48 5.88 5.5 5.5 0 0 1-8.48 5.88 4.5 4.5 0 0 0 10.24 0 5.5 5.5 0 0 1-10.24-3.6z"/></svg>
}
function LampIcon({ className }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2a7 7 0 1 0 10 7H2a7 7 0 1 0 10-7z"/><path d="M12 12v9"/><path d="M9 21h6"/></svg>
}
function AlertTriangleIcon({ className }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
}
function TrafficLightIcon({ className }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="18" rx="2"/><circle cx="12" cy="8" r="2"/><circle cx="12" cy="13" r="2"/><circle cx="12" cy="18" r="2"/></svg>
}
function FootprintsIcon({ className }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 20s-1.5-2.5-3-4"/><path d="M15 20s1.5-2.5 3-4"/><path d="M9 10V4"/><path d="M15 16v-6"/><path d="M9 14a5 5 0 0 1 5-5 5 5 0 0 1 5 5"/><path d="M15 18a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/></svg>
}
function WindIcon({ className }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/></svg>
}
function AlertCircleIcon({ className }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
}