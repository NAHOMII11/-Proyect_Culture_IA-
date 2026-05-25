import axios from 'axios'
import { API } from '../config/api'
import { getToken } from '../utils/auth'

export const uploadCsvFile = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const token = getToken()

  const response = await axios.post(`${API.quality}/imports`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  })

  return response.data
}