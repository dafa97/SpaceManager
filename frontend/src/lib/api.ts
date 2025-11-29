import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { CreateSpaceRequest, Space, UpdateSpaceRequest } from '@/types/space';

// Always use relative URLs - Next.js proxy handles routing to backend
export const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('access_token');
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // If 401 and not already retried, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (!refreshToken) {
                    throw new Error('No refresh token');
                }

                // Call refresh endpoint using relative URL (goes through proxy)
                const response = await axios.post(
                    '/api/auth/refresh',
                    { refresh_token: refreshToken }
                );

                const { access_token, refresh_token } = response.data;

                // Store new tokens
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', refresh_token);

                // Retry original request with new token
                if (originalRequest.headers) {
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                }
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh failed, clear tokens and redirect to login
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export const spacesApi = {
    list: async () => {
        const response = await api.get<Space[]>('/spaces');
        return response.data;
    },
    create: async (data: CreateSpaceRequest) => {
        const response = await api.post<Space>('/spaces', data);
        return response.data;
    },
    get: async (id: string) => {
        const response = await api.get<Space>(`/spaces/${id}`);
        return response.data;
    },
    update: async (id: string, data: UpdateSpaceRequest) => {
        const response = await api.put<Space>(`/spaces/${id}`, data);
        return response.data;
    },
    delete: async (id: string) => {
        await api.delete(`/spaces/${id}`);
    }
};

export default api;
