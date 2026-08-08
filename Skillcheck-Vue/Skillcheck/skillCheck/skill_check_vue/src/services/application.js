// src/services/application.js
// Flusso candidato pubblico: candidatura -> domande -> test di personalità
import api from './api'

export function applyForJob(jobCode, { name, email, file }) {
  const formData = new FormData()
  formData.append('name', name)
  formData.append('email', email)
  formData.append('pdf_file_upload', file)
  // Content-Type: undefined -> lascia che sia il browser a impostare
  // multipart/form-data con il boundary corretto (altrimenti resta
  // application/json dal default dell'istanza api e Django non legge i campi)
  return api
    .post(`/apply/${jobCode}/`, formData, { headers: { 'Content-Type': undefined } })
    .then(r => r.data)
}

export function getMostraDomande(resumeId, jobCode) {
  return api.get(`/mostra_domande/${resumeId}/${jobCode}/`).then(r => r.data)
}

export function postMostraDomande(resumeId, jobCode, payload) {
  return api.post(`/mostra_domande/${resumeId}/${jobCode}/`, payload).then(r => r.data)
}

export function getPersonalityQuestions(resumeId) {
  return api.get(`/personality_test/${resumeId}/`).then(r => r.data)
}

export function postPersonalityAnswers(resumeId, payload) {
  return api.post(`/personality_test/${resumeId}/`, payload).then(r => r.data)
}
