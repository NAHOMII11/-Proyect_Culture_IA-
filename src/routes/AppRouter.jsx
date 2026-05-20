import { Routes, Route, Navigate } from 'react-router-dom'
import FinalInterface from '../pages/FinalInterface'
import AuthPage from '../pages/AuthPage'
import UploadCsvPage from '../pages/UploadCsvPage'
import NearbyPage from '../pages/NearbyPage'
import RankZonePage from '../pages/rankzone'
import ProtectedRoute from '../components/ProtectedRoute'

function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<FinalInterface />} />
      <Route path="/auth" element={<AuthPage />} />
      <Route path="/nearby" element={<NearbyPage />} />
      <Route path="/rankzone" element={<RankZonePage />} />
      <Route path="/app" element={<FinalInterface />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/upload-csv" element={<UploadCsvPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default AppRouter
