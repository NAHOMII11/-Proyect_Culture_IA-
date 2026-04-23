import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import Header from '../components/layout/Header'
import LoginForm from '../components/auth/LoginForm'
import RegisterForm from '../components/auth/RegisterForm'

function AuthPage() {
  const [searchParams] = useSearchParams()
  const [tab, setTab] = useState('login')

  useEffect(() => {
    const mode = searchParams.get('mode')
    if (mode === 'register') {
      setTab('register')
    } else {
      setTab('login')
    }
  }, [searchParams])

  return (
    <>
      <Header />

      <main className="auth-page">
        <div className="auth-panel">
          <div className="auth-info">
            <p className="eyebrow">Acceso</p>
            <h1>Gestiona el ingreso a la plataforma turística</h1>
            <p>
              Desde aquí puedes iniciar sesión o registrarte para cargar el archivo CSV
              con la información de los lugares turísticos.
            </p>
          </div>

          <div className="auth-card">
            <div className="auth-tabs">
              <button
                type="button"
                className={tab === 'login' ? 'tab active' : 'tab'}
                onClick={() => setTab('login')}
              >
                Login
              </button>

              <button
                type="button"
                className={tab === 'register' ? 'tab active' : 'tab'}
                onClick={() => setTab('register')}
              >
                Register
              </button>
            </div>

            {tab === 'login' ? <LoginForm /> : <RegisterForm />}
          </div>
        </div>
      </main>
    </>
  )
}

export default AuthPage