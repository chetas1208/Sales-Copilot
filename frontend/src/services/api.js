import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// API endpoints
export const apiService = {
  // Health check
  health: () => api.get('/health'),

  // User profile
  saveProfile: (profileData) => api.post('/api/profile', profileData),
  getProfile: (userId) => api.get(`/api/profile/${userId}`),

  // Meeting preparation
  saveMeetingPrep: (meetingData) => api.post('/api/meeting-prep', meetingData),
  getMeetingPrep: (meetingId) => api.get(`/api/meeting-prep/${meetingId}`),

  // Research
  startResearch: (companyUrl, competitorUrls) =>
    api.post('/api/research', { company_url: companyUrl, competitor_urls: competitorUrls }),

  // LinkedIn via Apify
  fetchLinkedInProfile: (linkedinUrl) =>
    api.post('/api/linkedin/profile', { linkedin_url: linkedinUrl }),

  fetchLinkedInCompany: (linkedinUrl) =>
    api.post('/api/linkedin/company', { linkedin_url: linkedinUrl }),

  // Past meetings
  getPastMeetings: (userId) => api.get(`/api/meetings/${userId}`),
  getMeetingInsights: (meetingId) => api.get(`/api/meetings/${meetingId}/insights`),
}

export default api
