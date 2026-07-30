import api from './api';

// lista candidati per una JD (passa il code della JD)
export function listCandidates(jobCode) {
  return api.get(`/jobs/${encodeURIComponent(jobCode)}/candidates/`)
            .then(r => r.data);
}

// aggiorna lo stato (globale) del candidato
export function updateCandidateStatus(id, status) {
  return api.patch(`/candidates/${id}/`, { status }).then(r => r.data);
}

// aggiorna le 3 fasi (cv/hr/tech) del candidato
export function updateCandidateStage(id, payload /* {status_cv?, status_hr?, status_tech?} */) {
  return api.patch(`/candidates/${id}/state/`, payload).then(r => r.data);
}

// aggiorna il commento (persistito su DB) del candidato
export function updateCandidateComment(id, comment) {
  return api.patch(`/candidates/${id}/`, { comment }).then(r => r.data);
}
