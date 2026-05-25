import { Routes, Route } from 'react-router-dom'
import HomePage from '../pages/HomePage'
import AuthPage from '../pages/AuthPage'
import UploadCsvPage from '../pages/UploadCsvPage'
import NearbyPage from '../pages/NearbyPage'
import RankZonePage from '../pages/rankzone'
import AuditPage from '../pages/AuditPage'
import ProtectedRoute from '../components/ProtectedRoute'
import AIChatBot from '../components/AIChatBot'
import RoutePage from '../pages/RoutePage'
import { MapPlacesProvider } from '../context/MapPlacesContext'

function AppRouter() {
  return (
    <MapPlacesProvider>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/nearby" element={<NearbyPage />} />
        <Route path="/rankzone" element={<RankZonePage />} />
        <Route path="/auditoria" element={<AuditPage />} />
        <Route path="/routes" element={<RoutePage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/upload-csv" element={<UploadCsvPage />} />
        </Route>
      </Routes>
      <AIChatBot />
    </MapPlacesProvider>
  )
}

export default AppRouter