import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

const auditBase = '/api/v1_audit'

export const getAuditEvents = async (filters = {}) => {
  const { data } = await api.get(`${auditBase}/audit/events`, { params: filters })
  return data
}

export const getAuditSummary = async (filters = {}) => {
  const { data } = await api.get(`${auditBase}/audit/events/summary`, { params: filters })
  return data
}

export const getAuditEventById = async (eventId) => {
  const { data } = await api.get(`${auditBase}/audit/events/${eventId}`)
  return data
}

export const createAuditEvent = async (payload) => {
  const { data } = await api.post(`${auditBase}/audit/events`, payload)
  return data
}

export const getAuditEventTypes = async () => {
  const { data } = await api.get(`${auditBase}/audit/event-types`)
  return data
}
