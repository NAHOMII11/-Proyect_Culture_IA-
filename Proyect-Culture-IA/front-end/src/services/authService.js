// src/services/authService.js
import axios from 'axios'
import { API } from '../config/api'

const AUTH_API = API.auth

export const registerUser = async (payload) => {
  const response = await axios.post(`${AUTH_API}/register`, payload)
  return response.data
}

export const loginUser = async (payload) => {
  const response = await axios.post(`${AUTH_API}/login`, payload)
  return response.data
}