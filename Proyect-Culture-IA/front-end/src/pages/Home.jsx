import Header from '../components/layout/Header'
import PlaceGrid from '../components/places/PlaceGrid'
import TouristMap from '../components/map/TouristMap'

function Home() {
  return (
    <>
      <Header />
      <main>
        <section className="hero">
          <h1>Descubre lugares turísticos</h1>
          <p>Explora destinos, consulta detalles y traza rutas.</p>
        </section>

        <section className="catalog">
          <PlaceGrid />
        </section>

        <section className="map-section">
          <h2>Mapa y rutas</h2>
          <TouristMap />
        </section>
      </main>
    </>
  )
}

export default Home