import React, { useState, useEffect } from 'react'
import { Modal, Button, Input, Alert } from './UI'
import { MapPicker } from './MapPicker'
import { MapPin, Info, CheckCircle2, AlertCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { formatErrorMessage } from '../utils/helpers'

export function LocationModal({
  isOpen,
  onClose,
  onSuccess,
  title = "Set Your Community Location",
  explanation = "Please add your location before upvoting. You can only view and support incidents within 25 km of your saved location.",
  confirmText = "Save Community Location"
}) {
  const { user, updateProfile, fetchUser } = useAuth()
  const [address, setAddress] = useState('')
  const [latitude, setLatitude] = useState(null)
  const [longitude, setLongitude] = useState(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  // Prepopulate if user already has a saved location
  useEffect(() => {
    if (isOpen) {
      setAddress(user?.address || '')
      setLatitude(user?.latitude != null ? Number(user?.latitude) : null)
      setLongitude(user?.longitude != null ? Number(user?.longitude) : null)
      setError('')
    }
  }, [isOpen, user])

  const handleMapChange = (pos) => {
    if (!pos) return
    setLatitude(pos.lat != null ? Number(pos.lat) : null)
    setLongitude(pos.lng != null ? Number(pos.lng) : null)
    if (pos.address) {
      setAddress(pos.address)
    }
  }

  const handleSave = async (e) => {
    if (e) e.preventDefault()
    setError('')

    if (latitude == null || longitude == null) {
      setError('Please pinpoint your location on the map or use the search box to set valid coordinates.')
      return
    }

    if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
      setError('Coordinates are outside valid geographic range.')
      return
    }

    setSaving(true)
    try {
      const payload = {
        address: address.trim() || undefined,
        latitude: Number(latitude),
        longitude: Number(longitude)
      }

      await updateProfile(payload)
      if (fetchUser) {
        await fetchUser()
      }

      if (onSuccess) {
        onSuccess({ address: address.trim(), latitude: Number(latitude), longitude: Number(longitude) })
      }
      onClose()
    } catch (err) {
      setError(formatErrorMessage(err, 'Failed to update location. Please try again.'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {
        if (!saving) onClose()
      }}
      title={title}
      size="lg"
    >
      <div className="space-y-4">
        {/* Explanation Alert */}
        <div className="p-3.5 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-start gap-3 text-body-sm text-primary-200">
          <Info className="h-5 w-5 text-primary-400 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            {explanation}
          </div>
        </div>

        {error && (
          <Alert variant="danger" dismissible onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Address Input */}
        <div>
          <Input
            label="Community / Neighborhood Address"
            placeholder="e.g. Bandra West, Mumbai or your locality"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            disabled={saving}
          />
        </div>

        {/* Pinpoint Map Picker */}
        <div>
          <label className="block text-body-sm font-medium text-text-secondary mb-1.5 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <MapPin className="h-4 w-4 text-primary-400" />
              Pinpoint on Map (Sets your 25 km reference point)
            </span>
            {latitude != null && longitude != null && (
              <span className="font-mono text-xs text-primary-400 bg-primary-500/10 px-2 py-0.5 rounded-badge border border-primary-500/20">
                {latitude.toFixed(4)}, {longitude.toFixed(4)}
              </span>
            )}
          </label>
          <div className="border border-border rounded-xl overflow-hidden shadow-sm">
            <MapPicker
              value={{ lat: latitude, lng: longitude, address }}
              onChange={handleMapChange}
            />
          </div>
          <p className="text-caption text-text-muted mt-1.5">
            Click anywhere on the map, use the search bar, or click GPS to set your community center. Your exact residential address is never made public.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-border">
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            loading={saving}
            disabled={saving || latitude == null || longitude == null}
          >
            <CheckCircle2 className="h-4 w-4" />
            {confirmText}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
