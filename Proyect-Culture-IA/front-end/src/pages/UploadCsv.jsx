import { useState } from 'react'
import Papa from 'papaparse'

function UploadCsv() {
  const [rows, setRows] = useState([])

  const handleFile = (e) => {
    const file = e.target.files[0]
    if (!file) return

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        setRows(results.data)
      }
    })
  }

  return (
    <main className="upload-page">
      <h1>Cargar lugares turísticos</h1>
      <input type="file" accept=".csv" onChange={handleFile} />
      <pre>{JSON.stringify(rows, null, 2)}</pre>
    </main>
  )
}

export default UploadCsv