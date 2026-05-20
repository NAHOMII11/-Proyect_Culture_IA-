import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { loginUser } from '../../services/authService'

function LoginForm() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    email: '',
    password: ''
  })

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await loginUser(form)
      const token = response?.access_token

      if (!token) throw new Error('Token no recibido')

      localStorage.setItem('token', token)
      navigate('/upload-csv', { replace: true })
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'No fue posible iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h3>Iniciar sesión</h3>
      <input name="email" type="email" placeholder="Correo electrónico" onChange={handleChange} required />
      <input name="password" type="password" placeholder="Contraseña" onChange={handleChange} required />
      {error && <p className="error-text">{error}</p>}
      <button className="btn btn-primary" type="submit" disabled={loading}>
        {loading ? 'Ingresando...' : 'Entrar'}
      </button>
    </form>
  )
}

export default LoginForm