import { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-routing-machine'
import { getAllPlaces } from '../../services/placesService'
import { BOGOTA_CENTER, filterPlacesInColombia, isInColombia } from '../../utils/colombia'
import PlaceMapPopup from './PlaceMapPopup'

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
    ">
      ⭐
    </div>
  `,
  className: 'selected-place-icon',
  iconSize: [44, 44],
  popupAnchor: [0, -22]
})

const chatPlaceIcon = L.divIcon({
  html: `
    <div style="
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
      border: 3px solid white;
      border-radius: 50%;
      box-shadow: 0 4px 14px rgba(124, 58, 237, 0.45);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      transform: translate(-20px, -20px);
    ">
      🤖
    </div>
  `,
  className: 'chat-place-icon',
  iconSize: [40, 40],
  popupAnchor: [0, -20]
})

function RecenterMap({ position }) {
  const map = useMap()

  useEffect(() => {
    if (position) {
      map.setView(position, 14, { animate: true, duration: 1 })
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

function TouristMap({ selectedPlace, places = [], highlightPlaces = [] }) {
  const [userPosition, setUserPosition] = useState(null)
  const [apiPlaces, setApiPlaces] = useState([])
  const defaultCenter = [BOGOTA_CENTER.lat, BOGOTA_CENTER.lng]

  useEffect(() => {
    const loadPlaces = async () => {
      try {
        const hasCoords = places.some(
          (place) =>
            typeof (place.latitude ?? place.lat) === 'number' &&
            typeof (place.longitude ?? place.lng) === 'number'
        )
        const source = hasCoords ? places : await getAllPlaces()
        const validPlaces = filterPlacesInColombia(source).filter(
          (place) =>
            typeof place.latitude === 'number' &&
            typeof place.longitude === 'number'
        )
        setApiPlaces(validPlaces)
      } catch (error) {
        console.error('Error cargando lugares:', error)
      }
    }

    loadPlaces()
  }, [places])

  useEffect(() => {
    if (!navigator.geolocation) return

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords = [position.coords.latitude, position.coords.longitude]
        if (isInColombia(coords[0], coords[1])) {
          setUserPosition(coords)
        } else {
          setUserPosition(defaultCenter)
        }
      },
      () => {
        setUserPosition(defaultCenter)
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    )
  }, [])

  const chatMarkers = useMemo(() => {
    return filterPlacesInColombia(
      highlightPlaces.map((place) => ({
        ...place,
        id: place.id || place.place_id,
        latitude: place.latitude ?? place.lat,
        longitude: place.longitude ?? place.lng,
      }))
    )
  }, [highlightPlaces])

  const chatIds = useMemo(
    () => new Set(chatMarkers.map((place) => String(place.id || place.place_id))),
    [chatMarkers]
  )

  const recenterTarget = useMemo(() => {
    if (chatMarkers.length > 0) {
      const first = chatMarkers[0]
      return [first.latitude, first.longitude]
    }
    if (selectedPlace?.lat && selectedPlace?.lng) {
      return [selectedPlace.lat, selectedPlace.lng]
    }
    return userPosition
  }, [chatMarkers, selectedPlace, userPosition])

  const routeOrigin = userPosition || defaultCenter
  const routeDestination = selectedPlace && selectedPlace.lat && selectedPlace.lng
    ? [selectedPlace.lat, selectedPlace.lng]
    : null

  return (
    <div className="map-wrapper">
      <MapContainer
        center={recenterTarget || defaultCenter}
        zoom={13}
        style={{ height: '540px', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <RecenterMap position={recenterTarget} />

        {userPosition && (
          <Marker position={userPosition} icon={userLocationIcon}>
            <Popup>Tu ubicación actual</Popup>
          </Marker>
        )}

        {apiPlaces
          .filter((place) => !chatIds.has(String(place.id)))
          .map((place) => (
            <Marker
              key={place.id}
              position={[place.latitude, place.longitude]}
              icon={selectedPlace?.id === place.id ? selectedPlaceIcon : placeIcon}
            >
              <PlaceMapPopup
                placeId={place.id}
                fallbackName={place.name}
                fallbackCategory={place.category}
              />
            </Marker>
          ))}

        {chatMarkers.map((place) => (
          <Marker
            key={`chat-${place.id || place.place_id}`}
            position={[place.latitude, place.longitude]}
            icon={chatPlaceIcon}
          >
            <PlaceMapPopup
              placeId={place.id || place.place_id}
              fallbackName={place.name}
              fallbackCategory={place.category}
            />
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
