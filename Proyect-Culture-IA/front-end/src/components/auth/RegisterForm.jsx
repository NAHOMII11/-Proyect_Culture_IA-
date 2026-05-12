import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { registerUser } from '../../services/authService'

function RegisterForm() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    full_name: '',
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
      await registerUser({
        full_name: form.full_name,
        email: form.email,
        password: form.password
      })

      navigate('/upload-csv')
    } catch (err) {
      setError(err?.response?.data?.message || 'No fue posible registrarte')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h3>Crear cuenta</h3>
      <input name="full_name" type="text" placeholder="Nombre completo" onChange={handleChange} required />
      <input name="email" type="email" placeholder="Correo electrónico" onChange={handleChange} required />
      <input name="password" type="password" placeholder="Contraseña" onChange={handleChange} required />
      {error && <p className="error-text">{error}</p>}
      <button className="btn btn-primary" type="submit" disabled={loading}>
        {loading ? 'Registrando...' : 'Registrarme'}
      </button>
    </form>
  )
}

export default RegisterForm