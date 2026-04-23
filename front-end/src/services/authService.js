// src/services/authService.js
import axios from 'axios'

const API = 'http://localhost:8000/api/v1_auth/auth'

export const registerUser = async (payload) => {
  const response = await axios.post(`${API}/register`, payload)
  return response.data
}

export const loginUser = async (payload) => {
  const response = await axios.post(`${API}/login`, payload)
  return response.data
}