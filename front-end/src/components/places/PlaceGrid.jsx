import PlaceCard from './PlaceCard'

function PlaceGrid({ places, onSelect }) {
  return (
    <section className="places-grid places-scroll">
      {places.map((place) => (
        <PlaceCard key={place.id} place={place} onSelect={onSelect} />
      ))}
    </section>
  )
}

export default PlaceGrid