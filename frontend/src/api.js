import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const generateReport = async (formData) => {
    const response = await axios.post(`${API_URL}/api/generate`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getJobStatus = async (jobId) => {
    const response = await axios.get(`${API_URL}/api/job/${jobId}`);
    return response.data;
};

export const getDownloadUrl = (jobId) => {
    return `${API_URL}/api/download/${jobId}`;
};
