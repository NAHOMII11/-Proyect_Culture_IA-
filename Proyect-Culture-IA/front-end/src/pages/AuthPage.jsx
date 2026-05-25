import Header from '../components/layout/Header'
import LoginForm from '../components/auth/LoginForm'

function AuthPage() {
  return (
    <>
      <Header />

      <main className="auth-page">
        <div className="auth-panel">
          <div className="auth-info">
            <p className="eyebrow">Acceso</p>
            <h1>Gestiona el ingreso a la plataforma turística</h1>
            <p>
              Desde aquí puedes iniciar sesión para cargar el archivo CSV con la
              información de los lugares turísticos.
            </p>
          </div>

          <div className="auth-card">
            <LoginForm />
          </div>
        </div>
      </main>
    </>
  )
}

export default AuthPage