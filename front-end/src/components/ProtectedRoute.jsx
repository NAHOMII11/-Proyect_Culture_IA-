// src/components/ProtectedRoute.jsx
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { isAuthenticated } from '../utils/auth'

function ProtectedRoute() {
  const location = useLocation()

  if (!isAuthenticated()) {
    return <Navigate to="/auth" replace state={{ from: location }} />
  }

  return <Outlet />
}

export default ProtectedRoute