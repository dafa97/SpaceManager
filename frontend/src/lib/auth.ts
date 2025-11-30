import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { LoginRequest, RegisterRequest, TokenResponse, User } from '@/types/auth';

// Env helper compatible with Next/Vite/Vitest
declare const process: any;
const getEnv = (key: string): string | undefined => {
    const nodeEnv = (typeof process !== 'undefined' && (process as any).env) ? (process as any).env[key] : undefined;
    const viteEnv = (typeof import.meta !== 'undefined' && (import.meta as any).env) ? (import.meta as any).env[key] : undefined;
    return nodeEnv ?? viteEnv;
};

const nodeEnv = getEnv('NODE_ENV');
const apiOrigin = (getEnv('NEXT_PUBLIC_API_URL')?.replace(/\/$/, '') || 'http://localhost:8000');
// In tests, align with MSW mocks
const baseURL = nodeEnv === 'test' ? 'http://localhost:3000/api' : `${apiOrigin}/api`;

const api = axios.create({
    baseURL,
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
    (error: any) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
    (response: any) => response,
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

                // Call refresh endpoint using configured baseURL
                const response = await axios.post(
                    `${baseURL}/auth/refresh`,
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
                                const envNode = getEnv('NODE_ENV');
                                if (typeof window !== 'undefined' && envNode !== 'test') {
                                    const loginUrl = new URL('/login', window.location.origin).toString();
                                    window.location.href = loginUrl;
                                }
                                return Promise.reject(refreshError);
                        }
        }

        return Promise.reject(error);
    }
);

export const authApi = {
    login: async (credentials: LoginRequest): Promise<TokenResponse> => {
        const response = await api.post<TokenResponse>('auth/login', credentials);
        return response.data;
    },

    register: async (data: RegisterRequest): Promise<TokenResponse> => {
        const response = await api.post<TokenResponse>('auth/register', data);
        return response.data;
    },

    getCurrentUser: async (): Promise<User> => {
        const response = await api.get<User>('auth/me');
        return response.data;
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
};
