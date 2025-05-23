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

  const loadAppraisal = async () => {
    if (!appraisalId) return
    setLoading(true)
    setError(null)
    try {
      const res = await axios.get(`http://localhost:8000/get_candidates/${appraisalId}`)
      
      // Transform numeric fields
      const transformedSubject = {
        ...res.data.subject,
        lat: parseFloat(res.data.subject.lat),
        lon: parseFloat(res.data.subject.lon),
        gla: parseFloat(res.data.subject.gla.replace(/[^\d.]/g, '')),
        lot_size: parseFloat(res.data.subject.lot_size.replace(/[^\d.]/g, ''))
      }
      
      const transformedCandidates = res.data.candidates.map(c => ({
        ...c,
        lat: parseFloat(c.latitude),
        lon: parseFloat(c.longitude),
        gla: parseFloat((c.gla || '').replace(/[^\d.]/g, '')),
        lot_size: parseFloat((c.lot_size_sf || '').replace(/[^\d.]/g, ''))
      }))

      setSubject(transformedSubject)
      setCandidates(transformedCandidates)
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
      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to find comps')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl mb-4">Property Comp Finder</h1>
      
      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <div className="mb-6">
        <label className="block mb-2 font-medium">Select Appraisal ID</label>
        <div className="flex items-center gap-2">
          <select
            value={appraisalId}
            onChange={e => setAppraisalId(e.target.value)}
            className="p-2 border rounded w-full max-w-xs bg-white"
            disabled={loading || appraisalIds.length === 0}
          >
            <option value="" disabled>Select an Appraisal ID</option>
            {appraisalIds.map(id => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>
          <button
            onClick={loadAppraisal}
            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 whitespace-nowrap disabled:opacity-50"
            disabled={!appraisalId || loading}
          >
            {loading ? 'Loading...' : 'Load Property'}
          </button>
        </div>
      </div>

      {subject && (
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h2 className="text-xl mb-2 font-semibold">Subject Property</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="font-medium">Address:</p>
                <p>{subject.address}</p>
              </div>
              <div>
                <p className="font-medium">GLA:</p>
                <p>{subject.gla.toLocaleString()} sqft</p>
              </div>
              <div>
                <p className="font-medium">Lot Size:</p>
                <p>{subject.lot_size.toLocaleString()} sqft</p>
              </div>
              <div>
                <p className="font-medium">Year Built:</p>
                <p>{subject.year_built}</p>
              </div>
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
      
      {results && (
        <div className="mt-8">
          <h2 className="text-xl mb-4 font-semibold">Top 3 Comparable Properties</h2>
          <div className="space-y-4">
            {results.comps.map((comp, i) => (
              <div key={i} className="p-4 border rounded-lg bg-white shadow-sm">
                <h3 className="font-bold text-lg mb-2">Comp #{i+1}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="font-medium">Address:</p>
                    <p>{comp.address}</p>
                  </div>
                  <div>
                    <p className="font-medium">Sale Price:</p>
                    <p>${comp.close_price?.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="font-medium">Size:</p>
                    <p>{comp.gla?.toLocaleString()} sqft</p>
                  </div>
                  <div>
                    <p className="font-medium">Distance:</p>
                    <p>{Math.round(comp.distance * 100) / 100} miles</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}