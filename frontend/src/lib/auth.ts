import api from './api';
import { LoginRequest, RegisterRequest, TokenResponse, User } from '@/types/auth';

export const authApi = {
    login: async (credentials: LoginRequest): Promise<TokenResponse> => {
        const response = await api.post<TokenResponse>('/auth/login', credentials);
        return response.data;
    },

    register: async (data: RegisterRequest): Promise<TokenResponse> => {
        const response = await api.post<TokenResponse>('/auth/register', data);
        return response.data;
    },

    getCurrentUser: async (): Promise<User> => {
        const response = await api.get<User>('/auth/me');
        return response.data;
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
};
