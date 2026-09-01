// src/services/employees.js
import api from './api'

export function listEmployees() {
  return api.get('/employees/').then(r => r.data)
}

export function createEmployee({ nome, email, reparto = '' }) {
  return api.post('/employees/', { nome, email, reparto }).then(r => r.data)
}

export function deleteEmployee(id) {
  return api.delete(`/employees/${id}/`).then(r => r.data)
}

export function nominateCandidate(jobCode, employeeId) {
  return api.post(`/jobs/${jobCode}/nominate/`, { employee_id: employeeId }).then(r => r.data)
}
