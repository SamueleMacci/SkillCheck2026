// src/services/employees.js
import api from './api'

export function listEmployees() {
  return api.get('/employees/').then(r => r.data)
}

export function createEmployee({ nome, email, reparto = '', cvFile = null }) {
  const formData = new FormData()
  formData.append('nome', nome)
  formData.append('email', email)
  formData.append('reparto', reparto)
  if (cvFile) formData.append('cv_file', cvFile)
  // Content-Type: undefined -> lascia che sia il browser a impostare
  // multipart/form-data con il boundary corretto (vedi ApplyForJob.vue)
  return api
    .post('/employees/', formData, { headers: { 'Content-Type': undefined } })
    .then(r => r.data)
}

export function deleteEmployee(id) {
  return api.delete(`/employees/${id}/`).then(r => r.data)
}

export function nominateCandidate(jobCode, employeeId) {
  return api.post(`/jobs/${jobCode}/nominate/`, { employee_id: employeeId }).then(r => r.data)
}

export function getEmployeeJobScores(jobCode) {
  return api.get(`/jobs/${jobCode}/employee_scores/`).then(r => r.data)
}
