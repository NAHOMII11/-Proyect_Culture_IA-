import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet-routing-machine'

function RoutingControl({ from, to }) {
  const map = useMap()

  useEffect(() => {
    if (!from || !to) return

    const routingControl = L.Routing.control({
      waypoints: [
        L.latLng(from.lat, from.lng),
        L.latLng(to.lat, to.lng),
      ],
      routeWhileDragging: true,
      showAlternatives: true,
      addWaypoints: false,
      draggableWaypoints: true,
      fitSelectedRoutes: true,
      lineOptions: {
        styles: [{ color: '#2563eb', weight: 5 }]
      }
    }).addTo(map)

    return () => {
      map.removeControl(routingControl)
    }
  }, [map, from, to])

  return null
}

export default RoutingControl