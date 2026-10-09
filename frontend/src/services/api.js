import axios from 'axios';

const API_BASE_URL = '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health
  checkHealth: async () => {
    const res = await apiClient.get('/health');
    return res.data;
  },

  // Chat & RAG
  askQuestion: async (question, history = []) => {
    const res = await apiClient.post('/chat', { question, history });
    return res.data;
  },

  // Banking Glossary
  getGlossary: async (search = '', category = '') => {
    const params = {};
    if (search) params.search = search;
    if (category) params.category = category;
    const res = await apiClient.get('/glossary', { params });
    return res.data;
  },

  getGlossaryDetail: async (itemId) => {
    const res = await apiClient.get(`/glossary/${itemId}`);
    return res.data;
  },

  // Document Checklist
  getChecklist: async (task, bank = null) => {
    const res = await apiClient.post('/checklist', { task, bank });
    return res.data;
  },

  downloadChecklistPdf: async (task, bank = null) => {
    const res = await apiClient.post(
      '/checklist/pdf',
      { task, bank },
      { responseType: 'blob' }
    );
    // Create download link
    const blob = new Blob([res.data], { type: 'application/pdf' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `FinGuide_Checklist_${task}_${bank || 'General'}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  },

  // Scam Awareness
  getScamSamples: async () => {
    const res = await apiClient.get('/scam/samples');
    return res.data;
  },

  analyzeScam: async (messageText, scenarioType = null) => {
    const res = await apiClient.post('/scam/analyze', {
      message_text: messageText,
      scenario_type: scenarioType,
    });
    return res.data;
  },

  // Neutral Comparisons
  getComparisons: async () => {
    const res = await apiClient.get('/comparisons');
    return res.data;
  },

  getComparisonTopic: async (topic) => {
    const res = await apiClient.get(`/comparisons/${topic}`);
    return res.data;
  },

  // Sources & Documents
  getSources: async () => {
    const res = await apiClient.get('/sources');
    return res.data;
  },

  reindexSources: async () => {
    const res = await apiClient.post('/sources/reindex');
    return res.data;
  },
};

export default api;
