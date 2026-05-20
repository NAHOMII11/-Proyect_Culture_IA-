import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-routing-machine'
import { getAllPlaces } from '../../services/placesService'

// Icono personalizado para la ubicación del usuario
const userLocationIcon = L.divIcon({
  html: `
    <div style="
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #0f766e 0%, #115e59 100%);
      border: 3px solid white;
      border-radius: 50%;
      box-shadow: 0 4px 12px rgba(15, 118, 110, 0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      color: white;
      font-size: 20px;
      transform: translate(-20px, -20px);
    ">
      📍
    </div>
  `,
  className: 'user-location-icon',
  iconSize: [40, 40],
  popupAnchor: [0, -20]
})

// Icono personalizado para los lugares
const placeIcon = L.divIcon({
  html: `
    <div style="
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #ecfeff 0%, #cffafe 100%);
      border: 2px solid #0f766e;
      border-radius: 50%;
      box-shadow: 0 3px 10px rgba(15, 118, 110, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      transform: translate(-18px, -18px);
    ">
      📌
    </div>
  `,
  className: 'place-location-icon',
  iconSize: [36, 36],
  popupAnchor: [0, -18]
})

// Icono para el lugar seleccionado (más grande)
const selectedPlaceIcon = L.divIcon({
  html: `
    <div style="
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, #ecfeff 0%, #a5f3fc 100%);
      border: 3px solid #0f766e;
      border-radius: 50%;
      box-shadow: 0 4px 16px rgba(15, 118, 110, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      transform: translate(-22px, -22px);
      animation: pulse 2s infinite;
    ">
      ⭐
    </div>
    <style>
      @keyframes pulse {
        0%, 100% { box-shadow: 0 4px 16px rgba(15, 118, 110, 0.5); }
        50% { box-shadow: 0 4px 24px rgba(15, 118, 110, 0.8); }
      }
    </style>
  `,
  className: 'selected-place-icon',
  iconSize: [44, 44],
  popupAnchor: [0, -22]
})

function RecenterMap({ position }) {
  const map = useMap()

  useEffect(() => {
    if (position) {
      map.setView(position, 15, { animate: true, duration: 1 })
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

function TouristMap({ selectedPlace, places = [] }) {
  const [userPosition, setUserPosition] = useState(null)
  const [apiPlaces, setApiPlaces] = useState([])
  const defaultCenter = [7.8939, -72.5078]

  // Cargar lugares de la API
  useEffect(() => {
    const loadPlaces = async () => {
      try {
        const data = await getAllPlaces()
        const validPlaces = data.filter(
          (place) => place.latitude && place.longitude && 
          typeof place.latitude === 'number' && 
          typeof place.longitude === 'number' &&
          place.latitude > -90 && place.latitude < 90 &&
          place.longitude > -180 && place.longitude < 180
        )
        setApiPlaces(validPlaces)
      } catch (error) {
        console.error('Error cargando lugares:', error)
      }
    }

    loadPlaces()
  }, [])

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
  const routeDestination = selectedPlace && selectedPlace.lat && selectedPlace.lng
    ? [selectedPlace.lat, selectedPlace.lng]
    : null

  return (
    <div className="map-wrapper">
      <MapContainer
        center={routeDestination || userPosition || defaultCenter}
        zoom={13}
        style={{ height: '540px', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <RecenterMap position={routeDestination || userPosition} />

        {userPosition && (
          <Marker position={userPosition} icon={userLocationIcon}>
            <Popup>Tu ubicación actual</Popup>
          </Marker>
        )}

        {apiPlaces.map((place) => (
          <Marker 
            key={place.id} 
            position={[place.latitude, place.longitude]}
            icon={
              selectedPlace?.id === place.id ? selectedPlaceIcon : placeIcon
            }
          >
            <Popup>
              <strong>{place.name}</strong>
              <br />
              {place.category}
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