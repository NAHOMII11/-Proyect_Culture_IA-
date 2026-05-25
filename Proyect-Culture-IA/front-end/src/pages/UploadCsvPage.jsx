import { useEffect, useMemo, useState } from 'react'
import Header from '../components/layout/Header'
import Papa from 'papaparse'
import { uploadCsvFile } from '../services/qualityService'
import { getAllPlaces, updatePlace, deletePlace } from '../services/placesService'
import RegisterForm from '../components/auth/RegisterForm'
import { API } from '../config/api'

const PAGE_SIZE = 20

function UploadCsvPage() {
  const [file, setFile] = useState(null)
  const [rows, setRows] = useState([])
  const [columns, setColumns] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [coordsLoading, setCoordSLoading] = useState(false)
  const [coordsMessage, setCoordMessage] = useState('')

  const [places, setPlaces] = useState([])
  const [tableLoading, setTableLoading] = useState(false)
  const [tableError, setTableError] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editingRow, setEditingRow] = useState({})
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({
    name: '',
    category: '',
    address: '',
    status: '',
    description: ''
  })

  useEffect(() => {
    const loadPlaces = async () => {
      try {
        setTableLoading(true)
        setTableError('')
        const data = await getAllPlaces()
        setPlaces(data)
      } catch (err) {
        setTableError('No fue posible cargar la tabla de lugares')
      } finally {
        setTableLoading(false)
      }
    }

    loadPlaces()
  }, [])

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (!selectedFile) return

    setFile(selectedFile)
    setMessage('')
    setError('')
    setResult(null)

    Papa.parse(selectedFile, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        setRows(results.data)
        setColumns(Object.keys(results.data?.[0] || {}))
      }
    })
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Debes seleccionar un archivo CSV')
      return
    }

    setLoading(true)
    setError('')
    setMessage('')
    setResult(null)

    try {
      const data = await uploadCsvFile(file)
      setResult(data)
      setMessage('Archivo enviado correctamente')
    } catch (err) {
      setError(err?.response?.data?.detail || 'No fue posible enviar el archivo')
    } finally {
      setLoading(false)
    }
  }

  const filteredPlaces = useMemo(() => {
    return places.filter((place) => {
      const nameMatch = place.name?.toLowerCase().includes(filters.name.toLowerCase())
      const categoryMatch = place.category?.toLowerCase().includes(filters.category.toLowerCase())
      const addressMatch = place.address?.toLowerCase().includes(filters.address.toLowerCase())
      const statusMatch = place.status?.toLowerCase().includes(filters.status.toLowerCase())
      const descriptionMatch = place.description?.toLowerCase().includes(filters.description.toLowerCase())
      

      return nameMatch && categoryMatch && addressMatch && statusMatch && descriptionMatch
    })
  }, [places, filters])

  const uniqueValues = useMemo(() => {
    const collect = (key) => [...new Set(places.map((p) => p[key]).filter(Boolean))]
    return {
      name: collect('name'),
      category: collect('category'),
      address: collect('address'),
      status: collect('status'),
      description: collect('description')
    }
  }, [places])

  const totalPages = Math.max(1, Math.ceil(filteredPlaces.length / PAGE_SIZE))
  const paginatedPlaces = filteredPlaces.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  useEffect(() => {
    if (page > totalPages) setPage(1)
  }, [totalPages, page])

  const updateFilter = (key, value) => {
    setPage(1)
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  const toggleSelectAll = (checked) => {
    if (checked) {
      setSelectedIds(new Set(paginatedPlaces.map((p) => p.id)))
    } else {
      setSelectedIds(new Set())
    }
  }

  const toggleSelectOne = (id) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const startEdit = (row) => {
    setEditingId(row.id)
    setEditingRow({ ...row })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditingRow({})
  }

  const saveEdit = async () => {
    try {
      const payload = {
        name: editingRow.name,
        category: editingRow.category,
        description: editingRow.description,
        address: editingRow.address,
        imagelink: editingRow.imagelink,
        status: editingRow.status,
        latitude: editingRow.latitude,
        longitude: editingRow.longitude
      }

      const updated = await updatePlace(editingId, payload)

      setPlaces((prev) =>
        prev.map((p) => (p.id === editingId ? { ...p, ...updated } : p))
      )

      setMessage('Registro actualizado correctamente')
      cancelEdit()
    } catch (err) {
      setError(err?.response?.data?.detail || 'No fue posible actualizar el registro')
    }
  }

  const handleDeleteSelected = async () => {
    if (selectedIds.size === 0) return

    try {
      await Promise.all([...selectedIds].map((id) => deletePlace(id)))
      setPlaces((prev) => prev.filter((p) => !selectedIds.has(p.id)))
      setSelectedIds(new Set())
      setMessage('Registros eliminados correctamente')
    } catch (err) {
      setError(err?.response?.data?.detail || 'No fue posible eliminar los registros')
    }
  }

  const handleCellChange = (key, value) => {
    setEditingRow((prev) => ({ ...prev, [key]: value }))
  }

  const handleGenerateCoords = async () => {
    try {
      setCoordSLoading(true)
      setCoordMessage('Procesando...')
      
      const geoResponse = await fetch(API.gateway('v1_geo', 'geo/asignar'))
      
      if (!geoResponse.ok) {
        setCoordMessage('Error al asignar coordenadas')
        return
      }

      setCoordMessage('Enriqueciendo datos...')
      
      for (let i = 0; i < 2; i++) {
        try {
          const enrichResponse = await fetch(API.gateway('v1_iaenri', 'enrichments/enriquecer'), {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
          })
          
          if (!enrichResponse.ok) {
            console.error(`Enriquecimiento ${i + 1} falló`)
          }
        } catch (err) {
          console.error(`Error en enriquecimiento ${i + 1}:`, err)
        }
      }
      
      setCoordMessage('Puntuando lugares...')
      
      try {
        const analyticsResponse = await fetch(API.gateway('v1_analytics', 'analytics/puntuar'), {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (!analyticsResponse.ok) {
          console.error('Error en puntuación de lugares')
        }
      } catch (err) {
        console.error('Error en API de analytics:', err)
      }
      
      setCoordMessage('✓ Datos procesados exitosamente')
      
      setTimeout(() => {
        setCoordMessage('')
      }, 3000)
    } catch (err) {
      setCoordMessage('Error de conexión')
      console.error(err)
    } finally {
      setCoordSLoading(false)
    }
  }

  return (
    <>
      <Header />

      <main className="page">
        <section className="section">
          <div className="section-head">
            <h1>Cargar archivo CSV</h1>
            <p>Sube el archivo con la información de los lugares turísticos.</p>
          </div>

          <div className="upload-box">
            <input type="file" accept=".csv" onChange={handleFileChange} />
          </div>

          <div style={{ marginTop: '16px' }}>
            <button
              className="btn btn-primary"
              type="button"
              onClick={handleUpload}
              disabled={!file || loading}
            >
              {loading ? 'Enviando...' : 'Enviar a la API'}
            </button>
          </div>

          {message && <p style={{ color: 'green', marginTop: '12px' }}>{message}</p>}
          {error && <p className="error-text">{error}</p>}

          {result && (
            <div style={{ marginTop: '16px' }}>
              <h3>Respuesta de la API</h3>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}

          {rows.length > 0 && (
            <div className="table-wrap" style={{ marginTop: '18px' }}>
              <table>
                <thead>
                  <tr>
                    {columns.map((column) => (
                      <th key={column}>{column}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, index) => (
                    <tr key={index}>
                      {columns.map((column) => (
                        <td key={column}>{row[column]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="section">
          <div className="section-head">
            <h2>Tabla de lugares</h2>
            <p>Filtros, edición y eliminación desde la API.</p>
          </div>

          <div className="filters-table">
            {['name', 'category', 'address', 'status', 'description'].map((key) => (
              <div key={key} className="filter-field">
                <label>{key}</label>
                <input
                  type="text"
                  list={`${key}-options`}
                  value={filters[key]}
                  onChange={(e) => updateFilter(key, e.target.value)}
                  placeholder={`Filtrar por ${key}`}
                />
                <datalist id={`${key}-options`}>
                  {uniqueValues[key].map((value) => (
                    <option key={value} value={value} />
                  ))}
                </datalist>
              </div>
            ))}
          </div>

          <div style={{ marginBottom: '12px' }}>
            <button
              className="btn btn-primary"
              type="button"
              onClick={handleDeleteSelected}
              disabled={selectedIds.size === 0}
            >
              Eliminar seleccionados
            </button>
          </div>

          {tableLoading && <p>Cargando tabla...</p>}
          {tableError && <p className="error-text">{tableError}</p>}

          {!tableLoading && !tableError && (
            <>
              <div className="table-wrap table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>
                        <input
                          type="checkbox"
                          checked={
                            paginatedPlaces.length > 0 &&
                            paginatedPlaces.every((p) => selectedIds.has(p.id))
                          }
                          onChange={(e) => toggleSelectAll(e.target.checked)}
                        />
                      </th>
                      <th>name</th>
                      <th>category</th>
                      <th>description</th>
                      <th>address</th>
                      <th>imagelink</th>
                      <th>latitude</th>
                      <th>longitude</th>
                      <th>status</th>
                      <th>actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedPlaces.map((place) => {
                      const isEditing = editingId === place.id
                      const current = isEditing ? editingRow : place

                      return (
                        <tr key={place.id}>
                          <td>
                            <input
                              type="checkbox"
                              checked={selectedIds.has(place.id)}
                              onChange={() => toggleSelectOne(place.id)}
                            />
                          </td>

                          {['name', 'category', 'description', 'address', 'imagelink', 'latitude', 'longitude', 'tags', 'importance_score', 'status'].map(
                            (key) => (
                              <td key={key}>
                                {isEditing ? (
                                  <input
                                    className="table-input"
                                    value={current[key] ?? ''}
                                    onChange={(e) => handleCellChange(key, e.target.value)}
                                  />
                                ) : (
                                  current[key] ?? ''
                                )}
                              </td>
                            )
                          )}

                          <td>
                            {isEditing ? (
                              <>
                                <button className="btn btn-primary btn-sm" type="button" onClick={saveEdit}>
                                  Guardar
                                </button>
                                <button className="btn btn-ghost btn-sm" type="button" onClick={cancelEdit}>
                                  Cancelar
                                </button>
                              </>
                            ) : (
                              <button className="btn btn-ghost btn-sm" type="button" onClick={() => startEdit(place)}>
                                Editar
                              </button>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              <div className="pagination">
                <button
                  className="btn btn-ghost"
                  type="button"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Anterior
                </button>

                <span>
                  Página {page} de {totalPages}
                </span>

                <button
                  className="btn btn-ghost"
                  type="button"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  Siguiente
                </button>
              </div>
            </>
          )}
        </section>
        {localStorage.getItem('token') && (
          <section className="section">
            <div style={{ marginBottom: '16px' }}>
              <button
                className="btn-ai-assistant"
                type="button"
                onClick={handleGenerateCoords}
                disabled={coordsLoading}
              >
                <span className="ai-icon">✨</span>
                <span className="ai-text">
                  {coordsLoading ? 'Procesando datos...' : 'Asistente IA - Enriquecer Datos'}
                </span>
                {coordsLoading && <span className="ai-spinner"></span>}
              </button>
              {coordsMessage && (
                <p style={{
                  marginTop: '12px',
                  padding: '10px 16px',
                  borderRadius: '8px',
                  fontSize: '0.9rem',
                  backgroundColor: coordsMessage.startsWith('✓') ? '#d1fae5' : coordsMessage.includes('Procesando') || coordsMessage.includes('Enriqueciendo') ? '#dbeafe' : '#fee2e2',
                  color: coordsMessage.startsWith('✓') ? '#065f46' : coordsMessage.includes('Procesando') || coordsMessage.includes('Enriqueciendo') ? '#0c4a6e' : '#7f1d1d',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  {coordsMessage.startsWith('✓') ? '✓' : coordsMessage.includes('Procesando') || coordsMessage.includes('Enriqueciendo') ? '⏳' : '⚠️'}
                  {coordsMessage}
                </p>
              )}
            </div>
            <style>{`
              .btn-ai-assistant {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                position: relative;
                overflow: hidden;
              }
              
              .btn-ai-assistant:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
              }
              
              .btn-ai-assistant:active:not(:disabled) {
                transform: translateY(0);
              }
              
              .btn-ai-assistant:disabled {
                opacity: 0.8;
                cursor: not-allowed;
              }
              
              .ai-icon {
                font-size: 1.3rem;
                animation: float 2s ease-in-out infinite;
              }
              
              .ai-text {
                flex: 1;
                text-align: center;
              }
              
              .ai-spinner {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-top-color: white;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
              }
              
              @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-4px); }
              }
              
              @keyframes spin {
                to { transform: rotate(360deg); }
              }
            `}</style>
            <div className="section-head">
              <h2>Registrar usuario</h2>
              <p>Solo disponible después de iniciar sesión.</p>
            </div>
            <div className="auth-card">
              <RegisterForm />
            </div>
          </section>
        )}
      </main>
    </>
  )
}

export default UploadCsvPage