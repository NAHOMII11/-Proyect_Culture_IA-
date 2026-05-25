// src/components/layout/Header.jsx
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { logout } from '../../utils/auth'

function Header() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const token = localStorage.getItem('token')
  const isLoggedIn = Boolean(token)


  const handleLogout = () => {
    logout()
    navigate('/auth', { replace: true })
  }

  return (
    <header className="header">
      <Link to="/" className="brand">
        <span className="brand-mark">T</span>
        <div>
          <strong>Turismo Norte</strong>
          <small>Catálogo de lugares</small>
        </div>
      </Link>

      <nav className="nav">
        <Link className={pathname === '/' ? 'nav-link active' : 'nav-link'} to="/">
          Inicio
        </Link>

        <Link className={pathname === '/nearby' ? 'nav-link active' : 'nav-link'} to="/nearby">
          Lugares cercanos
        </Link>

        <Link className={pathname === '/rankzone' ? 'nav-link active' : 'nav-link'} to="/rankzone">
          Ranking
        </Link>

        <Link className={pathname === '/auditoria' ? 'nav-link active' : 'nav-link'} to="/auditoria">
          Auditoría
        </Link>

        <Link className={pathname === '/routes' ? 'nav-link active' : 'nav-link'} to="/routes">
          Rutas
        </Link>

        <div className="user-menu">
          <button type="button" className="user-trigger" aria-label="Abrir menú de acceso">
            <span className="user-avatar">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
                width="20"
                height="20"
              >
                <path d="M20 21a8 8 0 0 0-16 0" />
                <circle cx="12" cy="8" r="4" />
              </svg>
            </span>
          </button>

          <div className="user-dropdown">
            <Link className="dropdown-link" to="/auth?mode=login">
              Iniciar sesión
            </Link>

            {isLoggedIn && (
              <>
                <Link className="dropdown-link dropdown-link-primary" to="/upload-csv">
                  Registro
                </Link>
                <button
                  type="button"
                  className="dropdown-link dropdown-logout"
                  onClick={handleLogout}
                >
                  Cerrar sesión
                </button>
              </>
            )}
          </div>
        </div>
      </nav>
    </header>
  )
}

export default Header