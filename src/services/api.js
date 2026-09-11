import axios from 'axios';

const API_BASE_URL = 'http://localhost:5002/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  register: async (email, password) => {
    const response = await api.post('/auth/register', { email, password });
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
};

export const reportService = {
  uploadReport: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('pdf', file);

    const response = await api.post('/reports/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  },

  getReportHistory: async () => {
    const response = await api.get('/reports/history');
    return response.data.reports;
  },

  downloadReport: async (reportId) => {
    try {
      console.log('Starting download for report:', reportId);
      
      if (!reportId) {
        alert('Report ID is missing');
        return;
      }

      const token = localStorage.getItem('token');
      console.log('Token exists:', !!token);
      console.log('Full request URL:', `${API_BASE_URL}/reports/download/${reportId}`);

      const response = await api.get(`/reports/download/${reportId}`, {
        responseType: 'blob',
      });
      
      console.log('Download successful, blob size:', response.data.size);
      
      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `AI_Report_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('Download triggered successfully');
    } catch (error) {
      console.error('Download error full details:', error);
      console.error('Error status:', error.response?.status);
      console.error('Error data:', error.response?.data);
      alert('Failed to download report: ' + (error.response?.data?.message || error.message));
    }
  },
};

export default api;
