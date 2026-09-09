import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { complaintAPI } from '../services/api'
import { useForm } from '../hooks/useForm'
import { Button, Input, Textarea, Select, Card, CardContent, Alert, Badge } from '../components/UI'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { MapPin, Camera, X, Loader2, CheckCircle2, ArrowRight } from 'lucide-react'
import { classNames } from '../utils/helpers'

// Default location (Mumbai)
const DEFAULT_CENTER = [19.0760, 72.8777]
const DEFAULT_ZOOM = 12

const CATEGORIES = [
  { value: 'pothole', label: 'Pothole / Road Damage', icon: 'road' },
  { value: 'garbage', label: 'Garbage / Waste', icon: 'trash-2' },
  { value: 'water_leakage', label: 'Water Leakage', icon: 'droplets' },
  { value: 'streetlight', label: 'Streetlight Issue', icon: 'lamp' },
  { value: 'sewage_overflow', label: 'Sewage Overflow', icon: 'alert-triangle' },
  { value: 'traffic_signal', label: 'Traffic Signal', icon: 'traffic-light' },
  { value: 'footpath', label: 'Footpath / Sidewalk', icon: 'footprints' },
  { value: 'drainage', label: 'Drainage / Waterlogging', icon: 'wind' },
]

// Fix Leaflet marker icon issue
import L from 'leaflet'
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

export function SubmitComplaintPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [selectedLocation, setSelectedLocation] = useState(null)
  const [locationSearch, setLocationSearch] = useState('')
  const [locationSuggestions, setLocationSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [previewImages, setPreviewImages] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [mapKey, setMapKey] = useState(0)
  const fileInputRef = useRef(null)
  const locationInputRef = useRef(null)

  const { values, errors, handleChange, handleBlur, handleSubmit, setFieldValue } = useForm({
    initialValues: {
      description: '',
      category_id: '',
      evidence_files: [],
    },
    validate: (values) => {
      const errs = {}
      if (!values.description.trim()) errs.description = 'Description is required'
      else if (values.description.length < 20) errs.description = 'Description must be at least 20 characters'
      if (!values.category_id) errs.category_id = 'Please select a category'
      if (!selectedLocation) errs.location = 'Please select a location on the map'
      return errs
    },
    onSubmit: async (values) => {
      setError('')
      setSubmitting(true)
      try {
        const formData = new FormData()
        formData.append('description', values.description)
        formData.append('category_id', values.category_id)
        formData.append('latitude', selectedLocation.lat.toString())
        formData.append('longitude', selectedLocation.lng.toString())
        if (selectedLocation.address) formData.append('address', selectedLocation.address)
        if (selectedLocation.landmark) formData.append('landmark', selectedLocation.landmark)
        if (selectedLocation.area_name) formData.append('area_name', selectedLocation.area_name)
        if (selectedLocation.city) formData.append('city', selectedLocation.city)
        if (selectedLocation.state) formData.append('state', selectedLocation.state)
        if (selectedLocation.pincode) formData.append('pincode', selectedLocation.pincode)
        
        previewImages.forEach((file) => {
          formData.append('evidence_files', file)
        })

        await complaintAPI.create(formData)
        setSuccess(true)
        setTimeout(() => navigate('/dashboard'), 2000)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to submit complaint. Please try again.')
      } finally {
        setSubmitting(false)
      }
    },
  })

  const handleMapClick = (e) => {
    const { lat, lng } = e.latlng
    reverseGeocode(lat, lng)
  }

  const reverseGeocode = async (lat, lng) => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`
      )
      const data = await response.json()
      
      const address = data.display_name || ''
      const area = data.address?.suburb || data.address?.neighbourhood || data.address?.quarter || ''
      const landmark = data.address?.amenity || data.address?.tourism || data.address?.landmark || ''
      const city = data.address?.city || data.address?.town || data.address?.village || 'Mumbai'
      const state = data.address?.state || 'Maharashtra'
      const pincode = data.address?.postcode || ''
      
      setSelectedLocation({ lat, lng, address, area_name: area, landmark, city, state, pincode })
      setLocationSearch(address.split(',')[0])
      setShowSuggestions(false)
      setMapKey((k) => k + 1) // Force map re-render
    } catch (err) {
      console.error('Reverse geocode failed:', err)
      setSelectedLocation({ lat, lng, address: `${lat.toFixed(4)}, ${lng.toFixed(4)}` })
    }
  }

  const searchLocations = async (query) => {
    if (!query || query.length < 2) {
      setLocationSuggestions([])
      setShowSuggestions(false)
      return
    }
    
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1&countrycodes=in`
      )
      const data = await response.json()
      setLocationSuggestions(data)
      setShowSuggestions(true)
    } catch (err) {
      console.error('Location search failed:', err)
    }
  }

  const selectSuggestion = (place) => {
    const lat = parseFloat(place.lat)
    const lng = parseFloat(place.lon)
    setSelectedLocation({
      lat,
      lng,
      address: place.display_name,
      area_name: place.address?.suburb || place.address?.neighbourhood || '',
      landmark: place.address?.amenity || place.address?.tourism || '',
      city: place.address?.city || place.address?.town || 'Mumbai',
      state: place.address?.state || 'Maharashtra',
      pincode: place.address?.postcode || '',
    })
    setLocationSearch(place.display_name.split(',')[0])
    setShowSuggestions(false)
    setMapKey((k) => k + 1)
  }

  const useCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser')
      return
    }
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords
        reverseGeocode(latitude, longitude)
      },
      (err) => {
        setError('Unable to retrieve your location. Please enable location access or select manually.')
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    )
  }

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
    setFieldValue('evidence_files', [...values.evidence_files, ...validFiles])
    fileInputRef.current.value = ''
  }

  const removeImage = (index) => {
    setPreviewImages((prev) => prev.filter((_, i) => i !== index))
    setFieldValue('evidence_files', values.evidence_files.filter((_, i) => i !== index))
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary-50 via-white to-surface-elevated">
        <Card className="w-full max-w-md text-center p-8">
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="h-8 w-8 text-green-600" />
          </div>
          <h2 className="text-heading-md font-bold text-text-primary mb-2">Complaint Submitted!</h2>
          <p className="text-body text-text-secondary">Your complaint has been received and is being prioritized.</p>
          <Button onClick={() => navigate('/dashboard')} className="mt-6 w-full">
            View Dashboard
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface-elevated">
      {/* Progress Header */}
      <div className="sticky top-16 z-30 bg-white/95 backdrop-blur-sm border-b border-border">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <h1 className="text-heading-sm font-semibold text-text-primary">New Complaint</h1>
            <div className="flex items-center gap-4 text-body-sm">
              <span className={classNames('px-2 py-0.5 rounded-full text-caption font-medium', 
                !selectedLocation ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
              )}>
                {selectedLocation ? 'Location Set' : 'Location Required'}
              </span>
              <span className={classNames('px-2 py-0.5 rounded-full text-caption font-medium',
                !values.category_id ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
              )}>
                {values.category_id ? 'Category Selected' : 'Category Required'}
              </span>
            </div>
          </div>
        </div>
      </div>

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
                      'relative p-4 rounded-button border-2 transition-all text-left',
                      values.category_id === cat.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-border hover:border-primary-300 hover:bg-surface-hover'
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <div className={classNames(
                        'w-10 h-10 rounded-lg flex items-center justify-center',
                        values.category_id === cat.value ? 'bg-primary-500' : 'bg-surface-elevated'
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

          {/* Step 2: Location Selection */}
          <Card>
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-heading-sm font-semibold text-text-primary">Where is the issue?</h2>
                <Button variant="secondary" size="sm" type="button" onClick={useCurrentLocation}>
                  <MapPin className="h-4 w-4" />
                  Use My Location
                </Button>
              </div>

              {/* Location Search */}
              <div className="relative mb-4">
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-text-muted" />
                  <input
                    ref={locationInputRef}
                    type="text"
                    value={locationSearch}
                    onChange={(e) => {
                      setLocationSearch(e.target.value)
                      searchLocations(e.target.value)
                    }}
                    onFocus={() => locationSearch.length >= 2 && setShowSuggestions(true)}
                    onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                    placeholder="Search for a place, landmark, or address..."
                    className="input pl-10"
                    aria-label="Search location"
                    autoComplete="off"
                  />
                </div>
                
                {showSuggestions && locationSuggestions.length > 0 && (
                  <div className="absolute z-50 w-full mt-1 bg-white rounded-card shadow-elevated border border-border overflow-hidden">
                    {locationSuggestions.map((place) => (
                      <button
                        key={place.place_id}
                        type="button"
                        onClick={() => selectSuggestion(place)}
                        className="w-full px-4 py-3 text-left hover:bg-surface-hover transition-colors border-b border-border last:border-0"
                      >
                        <p className="text-body-sm font-medium text-text-primary">{place.display_name.split(',')[0]}</p>
                        <p className="text-caption text-text-muted truncate">{place.display_name}</p>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Map */}
              <div className="relative rounded-card overflow-hidden border border-border" style={{ height: '350px' }}>
                <MapContainer
                  key={mapKey}
                  center={selectedLocation ? [selectedLocation.lat, selectedLocation.lng] : DEFAULT_CENTER}
                  zoom={selectedLocation ? 16 : DEFAULT_ZOOM}
                  scrollWheelZoom={true}
                  onClick={handleMapClick}
                  className="h-full w-full"
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  {selectedLocation && (
                    <Marker position={[selectedLocation.lat, selectedLocation.lng]}>
                      <Popup>
                        <div className="text-body-sm">
                          <p className="font-medium">{selectedLocation.area_name || selectedLocation.address?.split(',')[0]}</p>
                          <p className="text-text-muted truncate max-w-[200px]">{selectedLocation.address}</p>
                        </div>
                      </Popup>
                    </Marker>
                  )}
                </MapContainer>
                
                {!selectedLocation && (
                  <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm pointer-events-none">
                    <div className="text-center p-4">
                      <MapPin className="h-12 w-12 text-text-muted mx-auto mb-3" />
                      <p className="text-body text-text-secondary">Click on the map to select location</p>
                      <p className="text-caption text-text-muted mt-1">Or use "Use My Location" button</p>
                    </div>
                  </div>
                )}
              </div>

              {selectedLocation && (
                <div className="mt-4 p-3 bg-surface-elevated rounded-button border border-border">
                  <p className="text-body-sm font-medium text-text-primary">Selected Location</p>
                  <p className="text-caption text-text-muted mt-1">{selectedLocation.address}</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {selectedLocation.area_name && <Badge variant="info">{selectedLocation.area_name}</Badge>}
                    {selectedLocation.landmark && <Badge variant="primary">{selectedLocation.landmark}</Badge>}
                    <Badge variant="default">{selectedLocation.city}, {selectedLocation.state}</Badge>
                  </div>
                </div>
              )}

              {errors.location && (
                <p className="mt-2 text-body-sm text-red-600" role="alert">{errors.location}</p>
              )}
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