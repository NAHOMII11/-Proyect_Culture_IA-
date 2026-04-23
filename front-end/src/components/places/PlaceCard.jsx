function PlaceCard({ place, onSelect }) {
  return (
    <article className="place-card" onClick={() => onSelect(place)}>
      <img src={place.imagelink} alt={place.name} className="place-image" />

      <div className="place-body">
        <span className="badge">{place.category}</span>
        <h3>{place.name}</h3>
        <p>{place.description}</p>
        <p className="place-address">
          <strong>Dirección:</strong> {place.address || 'Sin dirección'}
        </p>
      </div>
    </article>
  )
}

export default PlaceCard