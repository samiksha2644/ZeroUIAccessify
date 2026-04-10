import axios from 'axios';

// Initialize the Axios instance with a base URL
// Using EXPO_PUBLIC_ prefix makes it available in Expo apps automatically
const getBaseUrl = () => {
  // If no env is set, fallback to localhost
  return process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
};

const api = axios.create({
  baseURL: getBaseUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request Interceptor
api.interceptors.request.use(
  (config) => {
    // You can also add authorization tokens here later
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response Interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Log the error centrally
    if (error.response) {
      // Server responded with a status other than 2xx
      console.error(
        '[API Response Error]',
        `Status: ${error.response.status}`,
        `Data:`, error.response.data
      );
    } else if (error.request) {
      // The request was made but no response was received
      console.error('[API Response Error] No response received', error.request);
    } else {
      // Something happened in setting up the request
      console.error('[API Response Error]', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;
