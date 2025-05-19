'use client'
import { useState } from 'react'
import axios from 'axios'

export default function Home() {
  const [subject, setSubject] = useState({
    gla: '',
    lot_size: '',
    // ... other fields
  })
  const [results, setResults] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      const response = await axios.post('http://localhost:8000/get_comps', {
        ...subject,
        candidates: [] // This should be filled with the actual candidates
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      setResults(response.data)
    } catch (err) {
      console.error('API Error:', err)
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl mb-4">Property Comp Finder</h1>
      
      <form onSubmit={handleSubmit} className="max-w-md">
        <div className="grid gap-4">
          <div>
            <label className="block">Living Area (sqft)</label>
            <input
              type="number"
              value={subject.gla}
              onChange={e => setSubject({...subject, gla: e.target.value})}
              className="w-full p-2 border rounded"
            />
          </div>
          
          {/* Add other fields */}
          
          <button
            type="submit"
            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
          >
            Find Comps
          </button>
        </div>
      </form>

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