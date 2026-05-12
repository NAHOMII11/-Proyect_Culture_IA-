import { Routes, Route } from 'react-router-dom'
import HomePage from '../pages/HomePage'
import AuthPage from '../pages/AuthPage'
import UploadCsvPage from '../pages/UploadCsvPage'
import NearbyPage from '../pages/NearbyPage'
import RankZonePage from '../pages/rankzone'
import ProtectedRoute from '../components/ProtectedRoute'

function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/auth" element={<AuthPage />} />
      <Route path="/nearby" element={<NearbyPage />} />
      <Route path="/rankzone" element={<RankZonePage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/upload-csv" element={<UploadCsvPage />} />
      </Route>
    </Routes>
  )
}

export default AppRouter