import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { TokenResponse, User, OrganizationMembership } from '@/types/auth';
import { Space } from '@/types/space';
import { Reservation } from '@/types/reservation';

// Mock data
export const mockUser: User = {
  id: 1,
  email: 'test@example.com',
  full_name: 'Test User',
  is_active: true,
  is_superuser: false,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export const mockOrganization: OrganizationMembership = {
  organization: {
    id: 1,
    name: 'Test Org',
    slug: 'test-org',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
  },
  role: 'admin',
  status: 'active',
  created_at: '2024-01-01T00:00:00Z',
};

export const mockTokenResponse: TokenResponse = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  token_type: 'bearer',
};

export const mockSpace: Space = {
  id: 1,
  name: 'Conference Room A',
  description: 'A spacious conference room',
  space_type: 'hourly',
  capacity: 10,
  price_per_unit: 50.0,
  is_available: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

export const mockReservation: Reservation = {
  id: 1,
  space_id: 1,
  user_id: 1,
  start_time: '2024-01-01T10:00:00Z',
  end_time: '2024-01-01T12:00:00Z',
  total_price: 100.0,
  status: 'CONFIRMED',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

// Base URL for all API requests (must match api.ts baseURL)
const API_BASE_URL = 'http://localhost:3000/api';

// MSW handlers
export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE_URL}/auth/login`, () => {
    return HttpResponse.json(mockTokenResponse);
  }),

  http.post(`${API_BASE_URL}/auth/register`, () => {
    return HttpResponse.json(mockTokenResponse);
  }),

  http.post(`${API_BASE_URL}/auth/refresh`, () => {
    return HttpResponse.json({
      access_token: 'new-access-token',
      refresh_token: 'new-refresh-token',
      token_type: 'bearer',
    });
  }),

  http.get(`${API_BASE_URL}/auth/me`, () => {
    return HttpResponse.json(mockUser);
  }),

  // Organizations endpoints
  http.get(`${API_BASE_URL}/orgs`, () => {
    return HttpResponse.json([mockOrganization]);
  }),

  http.post(`${API_BASE_URL}/orgs`, () => {
    return HttpResponse.json(mockOrganization);
  }),

  // Spaces endpoints
  http.get(`${API_BASE_URL}/spaces`, () => {
    return HttpResponse.json([mockSpace]);
  }),

  http.post(`${API_BASE_URL}/spaces`, () => {
    return HttpResponse.json(mockSpace);
  }),

  http.get(`${API_BASE_URL}/spaces/:id`, () => {
    return HttpResponse.json(mockSpace);
  }),

  http.put(`${API_BASE_URL}/spaces/:id`, () => {
    return HttpResponse.json(mockSpace);
  }),

  http.delete(`${API_BASE_URL}/spaces/:id`, () => {
    return HttpResponse.json({});
  }),

  // Reservations endpoints
  http.get(`${API_BASE_URL}/reservations`, () => {
    return HttpResponse.json([mockReservation]);
  }),

  http.post(`${API_BASE_URL}/reservations`, () => {
    return HttpResponse.json(mockReservation);
  }),

  http.get(`${API_BASE_URL}/reservations/:id`, () => {
    return HttpResponse.json(mockReservation);
  }),

  http.put(`${API_BASE_URL}/reservations/:id`, () => {
    return HttpResponse.json(mockReservation);
  }),

  http.delete(`${API_BASE_URL}/reservations/:id`, () => {
    return HttpResponse.json({});
  }),
];

// Setup MSW server
export const server = setupServer(...handlers);

// Helper to reset handlers
export const resetHandlers = () => {
  server.resetHandlers();
};

// Helper to add custom handlers
export const addHandlers = (...newHandlers: typeof handlers) => {
  server.use(...newHandlers);
};

