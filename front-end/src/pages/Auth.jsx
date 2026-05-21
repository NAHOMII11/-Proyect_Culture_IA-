import { useState } from 'react'
import LoginForm from '../components/auth/LoginForm'
import RegisterForm from '../components/auth/RegisterForm'

function Auth() {
  const [mode, setMode] = useState('login')

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-tabs">
          <button onClick={() => setMode('login')}>Login</button>
          <button onClick={() => setMode('register')}>Register</button>
        </div>

        {mode === 'login' ? <LoginForm /> : <RegisterForm />}
      </div>
    </div>
  )
}

export default Auth