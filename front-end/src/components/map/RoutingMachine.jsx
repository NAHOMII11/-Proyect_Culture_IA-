import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet-routing-machine'

function RoutingMachine({ origin, destination }) {
  const map = useMap()

  useEffect(() => {
    if (!origin || !destination) return

    const routingControl = L.Routing.control({
      waypoints: [
        L.latLng(origin.lat, origin.lng),
        L.latLng(destination.lat, destination.lng)
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

export default RoutingMachine