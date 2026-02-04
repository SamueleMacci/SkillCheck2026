// src/services/jobs.js
import api from './api'

// JOBS
export function listJobs() {
  return api.get('/jobs/').then(r => r.data)
}

export function getJob(code) {
  // usa il codice della JD (stringa) come chiave
  return api.get(`/jobs/${code}/`).then(r => r.data)
}

export function createJob({ name, content, deadline = null }) {
  return api.post('/jobs/', { name, content, deadline }).then(r => r.data)
}

// CANDIDATI di una JD
export function listCandidates(jobCode) {
  return api.get(`/jobs/${jobCode}/candidates/`).then(r => r.data)
}

// Decisione su un candidato
export function decideCandidate(candidateId, decision /* 'ok' | 'rejected' | 'pending' | 'contact' */) {
  return api.post(`/candidates/${candidateId}/decision/`, { decision }).then(r => r.data)
}
