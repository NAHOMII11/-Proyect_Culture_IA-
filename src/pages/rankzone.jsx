import { useEffect, useState } from 'react'
import Header from '../components/layout/Header'

const ANALYTICS_RANKING_URL = 'http://localhost:8000/api/v1_analytics/analytics/ranking'

function RankZonePage() {
	const [ranking, setRanking] = useState([])
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState('')

	useEffect(() => {
		const controller = new AbortController()

		const loadRanking = async () => {
			try {
				setLoading(true)
				setError('')

				const response = await fetch(ANALYTICS_RANKING_URL, {
					signal: controller.signal,
				})

				if (!response.ok) {
					throw new Error('No se pudo consultar el ranking')
				}

				const data = await response.json()

				if (!Array.isArray(data)) {
					throw new Error('La respuesta del ranking no tiene el formato esperado')
				}

				const normalized = data
					.map((item) => ({
						name: item?.name ?? 'Sin nombre',
						city: item?.city ?? 'Sin ciudad',
						score: Number(item?.score ?? 0),
					}))
					.sort((a, b) => b.score - a.score)

				setRanking(normalized)
			} catch (fetchError) {
				if (fetchError.name !== 'AbortError') {
					setError('No se pudo cargar el ranking. Verifica que analytics-service esté disponible.')
				}
			} finally {
				setLoading(false)
			}
		}

		loadRanking()

		return () => controller.abort()
	}, [])

	return (
		<>
			<Header />

			<main className="page">
				<section className="hero">
					<div>
						<p className="eyebrow">Analítica cultural</p>
						<h1>Ranking de lugares</h1>
						<p className="hero-text">
							Esta vista consulta directamente el servicio de analytics y presenta los lugares
							ordenados por su puntaje.
						</p>
					</div>
				</section>

				<section className="section">
					<div className="section-head">
						<h2>Resultados del ranking</h2>
					</div>

					{loading && <p className="section-note">Cargando ranking...</p>}
					{error && <p className="error-text">{error}</p>}

					{!loading && !error && ranking.length === 0 && (
						<p className="section-note">No hay resultados disponibles en este momento.</p>
					)}

					{!loading && !error && ranking.length > 0 && (
						<div className="ranking-grid">
							{ranking.map((item, index) => {
								const percentage = Math.max(0, Math.min(100, item.score * 100))

								return (
									<article key={`${item.name}-${item.city}-${index}`} className="ranking-card">
										<div className="ranking-position">#{index + 1}</div>

										<div className="ranking-main">
											<h3>{item.name}</h3>
											<div className="ranking-meta">
												<span className="badge">{item.city}</span>
												<span>Puntaje: {item.score.toFixed(2)}</span>
											</div>

											<div className="ranking-bar" aria-hidden="true">
												<div
													className="ranking-bar-fill"
													style={{ width: `${percentage}%` }}
												/>
											</div>
										</div>

										<div className="ranking-score">
											<strong>{Math.round(percentage)}%</strong>
											<p>Score</p>
										</div>
									</article>
								)
							})}
						</div>
					)}
				</section>
			</main>
		</>
	)
}

export default RankZonePage
