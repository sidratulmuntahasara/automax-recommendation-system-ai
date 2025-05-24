'use client'
import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Home() {
  const [appraisalId, setAppraisalId] = useState('')
  const [appraisalIds, setAppraisalIds] = useState([])
  const [subject, setSubject] = useState(null)
  const [candidates, setCandidates] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
        const fetchIds = async () => {
      try {
        const res = await axios.get('http://localhost:8000/get_appraisal_ids')
        setAppraisalIds(res.data)
      } catch (err) {
        setError('Backend service unavailable - make sure it\'s running on port 8000')
      }
    }
    fetchIds()
  }, [])

  const safeParseFloat = (value, fallback = 0) => {
    try {
      const cleaned = String(value).replace(/[^\d.]/g, '')
      return parseFloat(cleaned) || fallback
    } catch {
      return fallback
    }
  }

  const loadAppraisal = async () => {
    if (!appraisalId) return
    setLoading(true)
    setError(null)
    
    try {
      const res = await axios.get(`http://localhost:8000/get_candidates/${appraisalId}`)
      
      // Transform subject property
      const rawSubject = res.data.subject || {}
      const transformedSubject = {
        address: rawSubject.address || 'Address not available',
        lat: safeParseFloat(rawSubject.lat),
        lon: safeParseFloat(rawSubject.lon),
        gla: safeParseFloat(rawSubject.gla),
        lot_size: safeParseFloat(rawSubject.lot_size),
        year_built: rawSubject.year_built || 'N/A',
        effective_date: rawSubject.effective_date || 'Unknown'
      }

      // Transform candidates
      const transformedCandidates = (res.data.candidates || []).map(c => ({
        address: c.address || 'Address not available',
        close_price: c.close_price ? parseInt(c.close_price) : 0,
        lat: safeParseFloat(c.latitude),
        lon: safeParseFloat(c.longitude),
        gla: safeParseFloat(c.gla),
        lot_size_sf: safeParseFloat(c.lot_size_sf),
        close_date: c.close_date || 'Unknown',
        beds: c.beds || 0,
        baths: c.baths || 0
      }))

      setSubject(transformedSubject)
      setCandidates(transformedCandidates.filter(c => c.lat && c.lon)) // Filter invalid locations
      setResults(null)
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load property data')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post('http://localhost:8000/get_comps', {
        subject: subject,
        candidates: candidates
      })
      
      setResults({
        comps: response.data.comps.map(comp => ({
          ...comp,
          distance: comp.distance ? Math.round(comp.distance * 100) / 100 : 0
        }))
      })
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to find comparables')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl mb-4">Property Recommendation System</h1>
      
      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Appraisal ID Selection */}
      <div className="mb-6">
        <label className="block mb-2 font-medium">Select Appraisal ID</label>
        <div className="flex items-center gap-2">
          <select
            value={appraisalId}
            onChange={e => setAppraisalId(e.target.value)}
            className="p-2 border rounded w-full max-w-xs bg-white"
            disabled={loading || appraisalIds.length === 0}
          >
            <option value="" disabled>Select a Property</option>
            {appraisalIds.map(appraisal => (
              <option 
                key={appraisal.id} 
                value={appraisal.id}
              >
                {appraisal.address} (ID: {appraisal.id})
              </option>
            ))}
          </select>
          <button
            onClick={loadAppraisal}
            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:opacity-50"
            disabled={!appraisalId || loading}
          >
            {loading ? 'Loading...' : 'Load Property'}
          </button>
        </div>
      </div>

      {/* Subject Property Display */}
      {subject && (
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h2 className="text-xl mb-2 font-semibold">Subject Property</h2>
            <div className="grid grid-cols-2 gap-4">
              <PropertyField label="Address" value={subject.address} />
              <PropertyField label="GLA" value={`${subject.gla.toLocaleString()} sqft`} />
              <PropertyField label="Lot Size" value={`${subject.lot_size.toLocaleString()} sqft`} />
              <PropertyField label="Year Built" value={subject.year_built} />
            </div>
          </div>

          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Find Comparable Properties'}
          </button>
        </form>
      )}

      {/* Results Display */}
      {results && (
        <div className="mt-8">
          <h2 className="text-xl mb-4 font-semibold">Top Comparable Properties</h2>
          <div className="space-y-4">
            {results.comps.length > 0 ? (
              results.comps.map((comp, i) => (
                <div key={i} className="p-4 border rounded-lg bg-white shadow-sm">
                  <h3 className="font-bold text-lg mb-2">Comp #{i+1}</h3>
                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <PropertyField label="Address" value={comp.address} />
                    <PropertyField label="Sale Price" value={`$${comp.close_price?.toLocaleString() || 'N/A'}`} />
                    <PropertyField label="Size" value={`${comp.gla?.toLocaleString()} sqft`} />
                    <PropertyField label="Distance" value={`${comp.distance} miles`} />
                  </div>
                  {comp.reasons?.length > 0 && (
                    <div className="pt-3 border-t">
                      <p className="text-sm font-medium text-gray-600">Matching Features:</p>
                      <ul className="list-disc list-inside">
                        {comp.reasons.map((reason, j) => (
                          <li key={j} className="text-sm text-gray-500">{reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="p-4 text-center text-gray-500">
                No comparable properties found
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

const PropertyField = ({ label, value }) => (
  <div>
    <p className="font-medium">{label}:</p>
    <p className="truncate">{value || 'N/A'}</p>
  </div>
)