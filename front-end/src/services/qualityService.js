import axios from 'axios'

const API = 'http://localhost:8000/api/v1_quality'

export const uploadCsvFile = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const token = localStorage.getItem('token')

  const response = await axios.post(`${API}/imports`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  })

  return response.data
}