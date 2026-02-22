import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export const dataflowAPI = {
  getAll: (page = 1, pageSize = 10) => api.get(`/dataflows?page=${page}&page_size=${pageSize}`),
  getCount: () => api.get('/dataflows/count'),
  get: (id) => api.get(`/dataflows/${id}`),
  create: (data) => api.post('/dataflows', data),
  update: (id, data) => api.put(`/dataflows/${id}`, data),
  delete: (id) => api.delete(`/dataflows/${id}`),
  testConnection: (id) => api.post(`/dataflows/${id}/test`),
  getFields: (id) => api.get(`/dataflows/${id}/fields`),
  saveFields: (id, data) => api.post(`/dataflows/${id}/fields`, data),
  importFields: (id, formData) => api.post(`/dataflows/${id}/import-fields`, formData),
}

export const dataAPI = {
  getFields: (dataflowId) => api.get(`/data/${dataflowId}/fields`),
  getEnabledFields: (dataflowId) => api.get(`/data/${dataflowId}/enabled-fields`),
  queryData: (data) => api.post('/data/query', data),
  getAllSnapshots: (page = 1, pageSize = 10) => api.get(`/data/snapshots?page=${page}&page_size=${pageSize}`),
  getSnapshotsCount: () => api.get('/data/snapshots/count'),
  getSnapshots: (dataflowId, page = 1, pageSize = 10) => api.get(`/data/${dataflowId}/snapshots?page=${page}&page_size=${pageSize}`),
  createSnapshot: (data) => api.post('/data/snapshots', data),
  getSnapshot: (snapshotId) => api.get(`/data/snapshots/${snapshotId}`),
  deleteSnapshot: (snapshotId) => api.delete(`/data/snapshots/${snapshotId}`),
  importLocalFile: (formData) => api.post('/data/import/local', formData),
}

export const dashboardAPI = {
  getAll: (page = 1, pageSize = 100) => api.get(`/dashboards?page=${page}&page_size=${pageSize}`),
  getCount: () => api.get('/dashboards/count'),
  get: (id) => api.get(`/dashboards/${id}`),
  create: (data) => api.post('/dashboards', data),
  update: (id, data) => api.put(`/dashboards/${id}`, data),
  delete: (id) => api.delete(`/dashboards/${id}`),
}

export const analysisAPI = {
  aggregate: (data) => api.post('/analysis/aggregate', data),
  transform: (data) => api.post('/analysis/transform', data),
  custom: (data) => api.post('/analysis/custom', data),
  getSnapshot: (snapshotId) => api.get(`/data/snapshots/${snapshotId}`),
  statisticalAnalysis: (data) => api.post('/analysis/statistical', data),
  distributionAnalysis: (data) => api.post('/analysis/distribution', data),
  regressionAnalysis: (data) => api.post('/analysis/regression', data),
  correlationAnalysis: (data) => api.post('/analysis/correlation', data),
  monteCarloAnalysis: (data) => api.post('/analysis/montecarlo', data),
  multiCorrelationAnalysis: (data) => api.post('/analysis/multi-correlation', data),
  correlationExplore: (data) => api.post('/analysis/correlation-explore', data),
  monteCarloPi: (data) => api.post('/analysis/montecarlo/pi', data),
  monteCarloIntegral: (data) => api.post('/analysis/montecarlo/integral', data),
  monteCarloQueue: (data) => api.post('/analysis/montecarlo/queue', data),
}

export default api
