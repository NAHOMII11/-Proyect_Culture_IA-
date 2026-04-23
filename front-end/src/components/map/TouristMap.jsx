import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-routing-machine'
import { mockPlaces } from '../../data/mockPlaces'

function RecenterMap({ position }) {
  const map = useMap()

  useEffect(() => {
    if (position) {
      map.flyTo(position, 15, { duration: 1 })
    }
  }, [map, position])

  return null
}

function RoutingMachine({ origin, destination }) {
  const map = useMap()

  useEffect(() => {
    if (!origin || !destination) return

    const routingControl = L.Routing.control({
      waypoints: [
        L.latLng(origin[0], origin[1]),
        L.latLng(destination[0], destination[1])
      ],
      routeWhileDragging: true,
      addWaypoints: false,
      draggableWaypoints: true,
      fitSelectedRoutes: true,
      showAlternatives: true,
      lineOptions: {
        styles: [{ color: '#0f766e', weight: 6 }]
      }
    }).addTo(map)

    return () => {
      map.removeControl(routingControl)
    }
  }, [map, origin, destination])

  return null
}

function TouristMap({ selectedPlace }) {
  const [userPosition, setUserPosition] = useState(null)
  const defaultCenter = [7.8939, -72.5078]

  useEffect(() => {
    if (!navigator.geolocation) return

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserPosition([
          position.coords.latitude,
          position.coords.longitude
        ])
      },
      (error) => {
        console.error('No se pudo obtener la ubicación:', error)
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    )
  }, [])

  const routeOrigin = userPosition || defaultCenter
  const routeDestination = selectedPlace
    ? [selectedPlace.lat, selectedPlace.lng]
    : null

  return (
    <div className="map-wrapper">
      <MapContainer
        center={userPosition || defaultCenter}
        zoom={13}
        style={{ height: '540px', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <RecenterMap position={userPosition} />

        {userPosition && (
          <Marker position={userPosition}>
            <Popup>Tu ubicación actual</Popup>
          </Marker>
        )}

        {mockPlaces.map((place) => (
          <Marker key={place.id} position={[place.lat, place.lng]}>
            <Popup>
              <strong>{place.name}</strong>
              <br />
              {place.city}
            </Popup>
          </Marker>
        ))}

        {routeDestination && (
          <RoutingMachine origin={routeOrigin} destination={routeDestination} />
        )}
      </MapContainer>
    </div>
  )
}

export default TouristMap