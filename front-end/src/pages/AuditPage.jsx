import { useCallback, useEffect, useState } from 'react'
import Header from '../components/layout/Header'
import { getAuditEventById, getAuditEvents, getAuditSummary } from '../services/auditService'

const EVENT_TYPES = [
  'import_batch_processed',
  'place_enriched',
  'score_calculated',
  'route_generated',
  'assistant_interaction',
  'coordinates_assigned',
  'place_created',
]

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('es-CO', {
    dateStyle: 'short',
    timeStyle: 'short',
  })
}

function toIsoParam(dateValue) {
  if (!dateValue) return undefined
  return new Date(dateValue).toISOString()
}

function AuditPage() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [filters, setFilters] = useState({
    event_type: '',
    source_service: '',
    reference_id: '',
    date_from: '',
    date_to: '',
    skip: 0,
    limit: 50,
  })

  const buildParams = useCallback(() => {
    const params = {
      skip: filters.skip,
      limit: filters.limit,
    }
    if (filters.event_type) params.event_type = filters.event_type
    if (filters.source_service) params.source_service = filters.source_service
    if (filters.reference_id) params.reference_id = filters.reference_id
    const dateFrom = toIsoParam(filters.date_from)
    const dateTo = toIsoParam(filters.date_to)
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    return params
  }, [filters])

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError('')

      const params = buildParams()
      const [eventsData, summaryData] = await Promise.all([
        getAuditEvents(params),
        getAuditSummary(params),
      ])

      setItems(eventsData?.items || [])
      setTotal(eventsData?.total ?? 0)
      setSummary(summaryData)
    } catch {
      setError('No se pudo cargar la auditoría. Verifica que el gateway y audit_api estén activos.')
      setItems([])
      setTotal(0)
      setSummary(null)
    } finally {
      setLoading(false)
    }
  }, [buildParams])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleFilterChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value, skip: 0 }))
  }

  const handleOpenDetail = async (event) => {
    setSelected(event)
    setDetailLoading(true)
    try {
      const detail = await getAuditEventById(event.id)
      setSelected(detail)
    } catch {
      setError('No se pudo cargar el detalle del evento.')
    } finally {
      setDetailLoading(false)
    }
  }

  const canGoPrev = filters.skip > 0
  const canGoNext = filters.skip + filters.limit < total

  return (
    <>
      <Header />

      <main className="page">
        <section className="hero">
          <div>
            <p className="eyebrow">Trazabilidad</p>
            <h1>Auditoría del sistema</h1>
            <p className="hero-text">
              Registro central de eventos funcionales: importaciones, enriquecimiento IA,
              scoring, rutas y asistente.
            </p>
          </div>
        </section>

        {summary && (
          <section className="section audit-summary">
            <div className="audit-summary-grid">
              <article className="audit-stat-card">
                <span>Total eventos</span>
                <strong>{summary.total}</strong>
              </article>
              <article className="audit-stat-card">
                <span>Tipos distintos</span>
                <strong>{Object.keys(summary.by_event_type || {}).length}</strong>
              </article>
              <article className="audit-stat-card">
                <span>Servicios origen</span>
                <strong>{Object.keys(summary.by_source_service || {}).length}</strong>
              </article>
            </div>
          </section>
        )}

        <section className="section">
          <div className="audit-filters">
            <label>
              Tipo de evento
              <select
                value={filters.event_type}
                onChange={(e) => handleFilterChange('event_type', e.target.value)}
              >
                <option value="">Todos</option>
                {EVENT_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Servicio origen
              <input
                type="text"
                placeholder="ej. ai-enrichment-service"
                value={filters.source_service}
                onChange={(e) => handleFilterChange('source_service', e.target.value)}
              />
            </label>

            <label>
              Referencia
              <input
                type="text"
                placeholder="place_id o batch_id"
                value={filters.reference_id}
                onChange={(e) => handleFilterChange('reference_id', e.target.value)}
              />
            </label>

            <label>
              Desde
              <input
                type="datetime-local"
                value={filters.date_from}
                onChange={(e) => handleFilterChange('date_from', e.target.value)}
              />
            </label>

            <label>
              Hasta
              <input
                type="datetime-local"
                value={filters.date_to}
                onChange={(e) => handleFilterChange('date_to', e.target.value)}
              />
            </label>

            <button type="button" className="btn-primary" onClick={loadData}>
              Actualizar
            </button>
          </div>

          {loading && <p className="section-note">Cargando eventos...</p>}
          {error && <p className="error-text">{error}</p>}

          {!loading && !error && items.length === 0 && (
            <p className="section-note">No hay eventos registrados con esos filtros.</p>
          )}

          {!loading && !error && items.length > 0 && (
            <>
              <p className="section-note">
                Mostrando {filters.skip + 1}–{Math.min(filters.skip + items.length, total)} de{' '}
                {total} eventos
              </p>
              <div className="audit-table-wrap">
                <table className="audit-table">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Tipo</th>
                      <th>Servicio</th>
                      <th>Referencia</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((event) => (
                      <tr key={event.id}>
                        <td>{formatDate(event.created_at)}</td>
                        <td>
                          <span className="badge">{event.event_type}</span>
                        </td>
                        <td>{event.source_service}</td>
                        <td className="audit-ref">{event.reference_id}</td>
                        <td>
                          <button
                            type="button"
                            className="btn-ghost"
                            onClick={() => handleOpenDetail(event)}
                          >
                            Ver detalle
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="audit-pagination">
                <button
                  type="button"
                  className="btn-ghost"
                  disabled={!canGoPrev}
                  onClick={() =>
                    setFilters((prev) => ({
                      ...prev,
                      skip: Math.max(prev.skip - prev.limit, 0),
                    }))
                  }
                >
                  Anterior
                </button>
                <span className="section-note">
                  Página {Math.floor(filters.skip / filters.limit) + 1}
                </span>
                <button
                  type="button"
                  className="btn-ghost"
                  disabled={!canGoNext}
                  onClick={() =>
                    setFilters((prev) => ({
                      ...prev,
                      skip: prev.skip + prev.limit,
                    }))
                  }
                >
                  Siguiente
                </button>
              </div>
            </>
          )}
        </section>
      </main>

      {selected && (
        <div className="audit-modal-backdrop" onClick={() => setSelected(null)}>
          <article
            className="audit-modal"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <header>
              <h2>Detalle del evento</h2>
              <button type="button" className="btn-ghost" onClick={() => setSelected(null)}>
                Cerrar
              </button>
            </header>
            {detailLoading ? (
              <p className="section-note">Cargando detalle...</p>
            ) : (
              <dl className="audit-detail-list">
                <dt>ID</dt>
                <dd className="audit-ref">{selected.id}</dd>
                <dt>Tipo</dt>
                <dd>{selected.event_type}</dd>
                <dt>Servicio</dt>
                <dd>{selected.source_service}</dd>
                <dt>Referencia</dt>
                <dd>{selected.reference_id}</dd>
                <dt>Fecha</dt>
                <dd>{formatDate(selected.created_at)}</dd>
                <dt>Resumen</dt>
                <dd>
                  <pre>{JSON.stringify(selected.payload_summary, null, 2)}</pre>
                </dd>
              </dl>
            )}
          </article>
        </div>
      )}
    </>
  )
}

export default AuditPage
