import { useEffect, useMemo, useState } from 'react'
import Header from '../components/layout/Header'
import Papa from 'papaparse'
import { uploadCsvFile } from '../services/qualityService'
import { getAllPlaces, updatePlace, deletePlace } from '../services/placesService'

const PAGE_SIZE = 20

function UploadCsvPage() {
  const [file, setFile] = useState(null)
  const [rows, setRows] = useState([])
  const [columns, setColumns] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

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

                          {['name', 'category', 'description', 'address', 'imagelink', 'latitude', 'longitude', 'status'].map(
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
      </main>
    </>
  )
}

export default UploadCsvPage