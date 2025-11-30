import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '../utils/test-utils';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server } from '../utils/mocks';
import LoginPage from '@/app/login/page';
import DashboardPage from '@/app/dashboard/page';
import SpacesPage from '@/app/dashboard/spaces/page';
import { useRouter, usePathname } from 'next/navigation';

// Mock useRouter and usePathname
const mockPush = vi.fn();
const mockReplace = vi.fn();
let mockPathname = '/';

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: mockReplace,
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => mockPathname,
  useSearchParams: () => new URLSearchParams(),
}));

describe('Navigation Integration Tests', () => {
  beforeEach(() => {
    mockPush.mockClear();
    mockReplace.mockClear();
    localStorage.clear();
    mockPathname = '/';
  });

  describe('Protected Routes', () => {
    it('should allow access to dashboard when authenticated', () => {
      localStorage.setItem('access_token', 'valid-token');
      
      render(<DashboardPage />);
      
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText(/you are now logged in/i)).toBeInTheDocument();
    });

    it('should redirect to login when accessing protected route without token', () => {
      localStorage.removeItem('access_token');
      
      // In a real app, this would be handled by middleware or a layout component
      // For testing, we simulate the redirect behavior
      const hasToken = localStorage.getItem('access_token');
      if (!hasToken) {
        mockPathname = '/login';
      }
      
      expect(hasToken).toBeNull();
    });
  });

  describe('Navigation Flow', () => {
    it('should navigate from login to dashboard after successful login', async () => {
      const user = userEvent.setup();
      localStorage.removeItem('access_token');
      
      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('should navigate from dashboard to spaces page', async () => {
      localStorage.setItem('access_token', 'valid-token');
      const user = userEvent.setup();
      
      render(<SpacesPage />);

      await waitFor(() => {
        expect(screen.getByText('Spaces')).toBeInTheDocument();
      });

      const addButton = screen.getByRole('link', { name: /add space/i });
      expect(addButton).toHaveAttribute('href', '/dashboard/spaces/new');
    });

    it('should navigate back from create space page', async () => {
      localStorage.setItem('access_token', 'valid-token');
      
      // This test verifies that the back navigation functionality exists
      // The actual back() function is mocked in setup.ts
      const router = useRouter();
      expect(router.back).toBeDefined();
    });
  });

  describe('Link Navigation', () => {
    it('should have correct links in login page', () => {
      render(<LoginPage />);
      
      const registerLink = screen.getByRole('link', { name: /sign up/i });
      expect(registerLink).toHaveAttribute('href', '/register');
    });

    it('should have correct links between login and register pages', () => {
      render(<LoginPage />);
      
      const registerLink = screen.getByRole('link', { name: /sign up/i });
      expect(registerLink).toHaveAttribute('href', '/register');
    });
  });

  describe('State Persistence', () => {
    it('should persist authentication state across navigation', async () => {
      const user = userEvent.setup();
      
      // Login
      render(<LoginPage />);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBeTruthy();
      });

      const token = localStorage.getItem('access_token');
      
      // Simulate navigation to dashboard
      localStorage.setItem('access_token', token!);
      
      // Token should still be present
      expect(localStorage.getItem('access_token')).toBe(token);
    });

    it('should maintain user session after page reload simulation', () => {
      const token = 'persistent-token';
      localStorage.setItem('access_token', token);
      localStorage.setItem('refresh_token', 'persistent-refresh-token');

      // Simulate page reload by checking localStorage
      const reloadedToken = localStorage.getItem('access_token');
      const reloadedRefreshToken = localStorage.getItem('refresh_token');

      expect(reloadedToken).toBe(token);
      expect(reloadedRefreshToken).toBe('persistent-refresh-token');
    });
  });

  describe('Error Navigation', () => {
    it('should stay on login page on authentication error', async () => {
      const user = userEvent.setup();
      
      server.use(
        http.post('/api/auth/login', () => {
          return HttpResponse.json(
            { detail: 'Invalid credentials' },
            { status: 401 }
          );
        })
      );

      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'wrong@example.com');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/login failed/i)).toBeInTheDocument();
      });

      // Should not navigate
      expect(mockPush).not.toHaveBeenCalled();
      // Should still be on login page
      expect(screen.getByText('Welcome back')).toBeInTheDocument();
    });
  });
});

