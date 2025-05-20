'use client'
import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Home() {
  const [appraisalId, setAppraisalId] = useState('')
  const [subject, setSubject] = useState(null)
  const [candidates, setCandidates] = useState([])
  const [results, setResults] = useState(null)

  // Load available appraisal IDs
  useEffect(() => {
    axios.get('http://localhost:8000/get_appraisal_ids')
      .then(res => setAppraisalIds(res.data))
      .catch(console.error)
  }, [])

  const loadAppraisal = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/get_candidates/${appraisalId}`)
      setSubject(res.data.subject)
      setCandidates(res.data.candidates)
    } catch (err) {
      console.error('Error loading appraisal:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await axios.post('http://localhost:8000/get_comps', {
        subject: subject,
        candidates: candidates
      })
      setResults(response.data)
    } catch (err) {
      console.error('API Error:', err)
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl mb-4">Property Comp Finder</h1>
      
      <div className="mb-6">
        <label className="block mb-2">Select Appraisal ID</label>
        <input
          type="text"
          value={appraisalId}
          onChange={e => setAppraisalId(e.target.value)}
          className="p-2 border rounded mr-2"
        />
        <button
          onClick={loadAppraisal}
          className="bg-gray-200 p-2 rounded hover:bg-gray-300"
        >
          Load Property
        </button>
      </div>

      {subject && (
        <form onSubmit={handleSubmit}>
          {/* Display subject property info */}
          <div className="mb-6">
            <h2 className="text-xl mb-2">Subject Property</h2>
            <p>GLA: {subject.gla} sqft</p>
            <p>Lot Size: {subject.lot_size}</p>
            {/* Add other subject details */}
          </div>

          <button
            type="submit"
            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
          >
            Find Comps
          </button>
        </form>
      )}
      
      {results && (
        <div className="mt-8">
          <h2 className="text-xl mb-4">Top 3 Comps</h2>
          <div className="space-y-4">
            {results.comps.map((comp, i) => (
              <div key={i} className="p-4 border rounded">
                <h3 className="font-bold">Comp #{i+1}</h3>
                <p>Size: {comp.gla} sqft</p>
                {/* Show other comp details */}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}