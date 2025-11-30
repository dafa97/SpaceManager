// Avoid TS complaints when Node types aren't available in Vitest/Next env
declare const process: any;
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { CreateSpaceRequest, Space, UpdateSpaceRequest } from '@/types/space';
import { 
    LoginRequest, 
    RegisterRequest, 
    TokenResponse, 
    User, 
    OrganizationMembership 
} from '@/types/auth';
import {
    Reservation,
    CreateReservationRequest,
    UpdateReservationRequest
} from '@/types/reservation';

// API configuration
// Prefer explicit base URL from env; fall back to localhost backend
// Ensure absolute URL for MSW compatibility in tests
// Safe env accessor across Next/Vite/Vitest without Node types
const getEnv = (key: string): string | undefined => {
    const nodeEnv = (typeof process !== 'undefined' && (process as any).env) ? (process as any).env[key] : undefined;
    const viteEnv = (typeof import.meta !== 'undefined' && (import.meta as any).env) ? (import.meta as any).env[key] : undefined;
    return nodeEnv ?? viteEnv;
};

const nodeEnv = getEnv('NODE_ENV');
const apiOrigin = (getEnv('NEXT_PUBLIC_API_URL')?.replace(/\/$/, '') || 'http://localhost:8000');
// In tests, stick to localhost:3000/api which MSW handlers expect
const baseURL = nodeEnv === 'test' ? 'http://localhost:3000/api' : `${apiOrigin}/api`;

export const api = axios.create({
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
        if (error.response?.status === 401 && !originalRequest._retry && originalRequest) {
            originalRequest._retry = true;

            const refreshToken = localStorage.getItem('refresh_token');
            
            // If no refresh token, clear everything and redirect
            if (!refreshToken) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                // Avoid relative redirects causing URL parse issues in test env
                const nodeEnv = getEnv('NODE_ENV');
                if (typeof window !== 'undefined' && nodeEnv !== 'test') {
                    const loginUrl = new URL('/login', window.location.origin).toString();
                    window.location.href = loginUrl;
                }
                return Promise.reject(error);
            }

            try {
                // Call refresh endpoint using configured baseURL
                const refreshUrl = `${baseURL}/auth/refresh`;
                
                const response = await axios.post(
                    refreshUrl,
                    { refresh_token: refreshToken }
                );

                const { access_token, refresh_token: new_refresh_token } = response.data;

                // Store new tokens
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', new_refresh_token);

                // Retry original request with new token
                if (originalRequest.headers) {
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                }
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh failed, clear tokens and redirect to login
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                const nodeEnv = getEnv('NODE_ENV');
                if (typeof window !== 'undefined' && nodeEnv !== 'test') {
                    const loginUrl = new URL('/login', window.location.origin).toString();
                    window.location.href = loginUrl;
                }
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

// ============================================================================
// AUTH API
// ============================================================================
export const authApi = {
    register: async (data: RegisterRequest): Promise<TokenResponse> => {
        const response = await api.post<TokenResponse>('auth/register', data);
        return response.data;
    },

    login: async (data: LoginRequest): Promise<TokenResponse> => {
        const response = await api.post<TokenResponse>('auth/login', data);
        return response.data;
    },

    refresh: async (refreshToken: string): Promise<TokenResponse> => {
        const response = await api.post<TokenResponse>('auth/refresh', {
            refresh_token: refreshToken
        });
        return response.data;
    },

    me: async (): Promise<User> => {
        const response = await api.get<User>('auth/me');
        return response.data;
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }
};

// ============================================================================
// ORGANIZATIONS API
// ============================================================================
export const orgsApi = {
    list: async (): Promise<OrganizationMembership[]> => {
        const response = await api.get<OrganizationMembership[]>('orgs');
        return response.data;
    },

    create: async (data: { name: string; slug: string }): Promise<OrganizationMembership> => {
        const response = await api.post<OrganizationMembership>('orgs', data);
        return response.data;
    },

    getBySlug: async (slug: string) => {
        const response = await api.get(`orgs/${slug}`);
        return response.data;
    },

    invite: async (orgId: number, data: { email: string; role: string }) => {
        const response = await api.post(`orgs/${orgId}/invite`, data);
        return response.data;
    }
};

// ============================================================================
// SPACES API
// ============================================================================
export const spacesApi = {
    list: async (skip: number = 0, limit: number = 100): Promise<Space[]> => {
        const response = await api.get<Space[]>('spaces', {
            params: { skip, limit }
        });
        return response.data;
    },

    create: async (data: CreateSpaceRequest): Promise<Space> => {
        const response = await api.post<Space>('spaces', data);
        return response.data;
    },

    get: async (id: number): Promise<Space> => {
        const response = await api.get<Space>(`spaces/${id}`);
        return response.data;
    },

    update: async (id: number, data: UpdateSpaceRequest): Promise<Space> => {
        const response = await api.put<Space>(`spaces/${id}`, data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`spaces/${id}`);
    }
};

// ============================================================================
// RESERVATIONS API
// ============================================================================
export const reservationsApi = {
    list: async (skip: number = 0, limit: number = 100): Promise<Reservation[]> => {
        const response = await api.get<Reservation[]>('reservations', {
            params: { skip, limit }
        });
        return response.data;
    },

    create: async (data: CreateReservationRequest): Promise<Reservation> => {
        const response = await api.post<Reservation>('reservations', data);
        return response.data;
    },

    get: async (id: number): Promise<Reservation> => {
        const response = await api.get<Reservation>(`reservations/${id}`);
        return response.data;
    },

    update: async (id: number, data: UpdateReservationRequest): Promise<Reservation> => {
        const response = await api.put<Reservation>(`reservations/${id}`, data);
        return response.data;
    },

    cancel: async (id: number): Promise<void> => {
        await api.delete(`reservations/${id}`);
    }
};

export default api;
