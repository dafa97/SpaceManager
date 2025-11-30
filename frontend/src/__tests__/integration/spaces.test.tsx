import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '../utils/test-utils';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { server, mockSpace } from '../utils/mocks';
import SpacesPage from '@/app/dashboard/spaces/page';
import CreateSpacePage from '@/app/dashboard/spaces/new/page';
import { useRouter } from 'next/navigation';

// Mock useRouter
const mockPush = vi.fn();
const mockBack = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    back: mockBack,
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => '/dashboard/spaces',
  useSearchParams: () => new URLSearchParams(),
}));

describe('Spaces Integration Tests', () => {
  beforeEach(() => {
    mockPush.mockClear();
    mockBack.mockClear();
    // Set up auth token for protected routes
    localStorage.setItem('access_token', 'mock-token');
  });

  describe('List Spaces', () => {
    it('should render spaces list page', () => {
      render(<SpacesPage />);
      
      expect(screen.getByText('Spaces')).toBeInTheDocument();
      expect(screen.getByText('All Spaces')).toBeInTheDocument();
    });

    it('should display loading state initially', () => {
      render(<SpacesPage />);
      
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should fetch and display spaces', async () => {
      render(<SpacesPage />);

      await waitFor(() => {
        expect(screen.getByText('Conference Room A')).toBeInTheDocument();
      });

      expect(screen.getByText(/capacity: 10/i)).toBeInTheDocument();
      // Note: The actual display might use price_per_hour but type uses price_per_unit
      // This test verifies the space is displayed correctly
    });

    it('should display empty state when no spaces', async () => {
      server.use(
        http.get('/api/spaces', () => {
          return HttpResponse.json([]);
        })
      );

      render(<SpacesPage />);

      await waitFor(() => {
        expect(screen.getByText(/no spaces found/i)).toBeInTheDocument();
      });
    });

    it('should handle API error when fetching spaces', async () => {
      server.use(
        http.get('/api/spaces', () => {
          return HttpResponse.json(
            { detail: 'Failed to fetch spaces' },
            { status: 500 }
          );
        })
      );

      render(<SpacesPage />);

      await waitFor(() => {
        // Should not crash, just show empty state or error
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });
    });

    it('should navigate to create space page', async () => {
      const user = userEvent.setup();
      render(<SpacesPage />);

      await waitFor(() => {
        expect(screen.getByText('Conference Room A')).toBeInTheDocument();
      });

      const addButton = screen.getByRole('link', { name: /add space/i });
      await user.click(addButton);

      // Note: In a real test, we'd check navigation, but since we're mocking
      // the router, we can verify the link href
      expect(addButton).toHaveAttribute('href', '/dashboard/spaces/new');
    });
  });

  describe('Create Space', () => {
    it('should render create space form', () => {
      render(<CreateSpacePage />);
      
      expect(screen.getByRole('heading', { name: 'Create Space' })).toBeInTheDocument();
      expect(screen.getByText('Space Details')).toBeInTheDocument();
      expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/capacity/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/price per hour/i)).toBeInTheDocument();
    });

    it('should successfully create space and redirect', async () => {
      const user = userEvent.setup();
      render(<CreateSpacePage />);

      const nameInput = screen.getByLabelText(/name/i);
      const descriptionInput = screen.getByLabelText(/description/i);
      const capacityInput = screen.getByLabelText(/capacity/i);
      const priceInput = screen.getByLabelText(/price per hour/i);
      const submitButton = screen.getByRole('button', { name: /create space/i });

      await user.type(nameInput, 'New Conference Room');
      await user.type(descriptionInput, 'A new room');
      await user.type(capacityInput, '20');
      await user.type(priceInput, '75.50');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard/spaces');
      });
    });

    it('should display error message on creation failure', async () => {
      const user = userEvent.setup();
      
      server.use(
        http.post('/api/spaces', () => {
          return HttpResponse.json(
            { detail: 'Failed to create space' },
            { status: 400 }
          );
        })
      );

      render(<CreateSpacePage />);

      const nameInput = screen.getByLabelText(/name/i);
      const capacityInput = screen.getByLabelText(/capacity/i);
      const priceInput = screen.getByLabelText(/price per hour/i);
      const submitButton = screen.getByRole('button', { name: /create space/i });

      await user.type(nameInput, 'New Room');
      await user.type(capacityInput, '10');
      await user.type(priceInput, '50');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to create space/i)).toBeInTheDocument();
      });

      expect(mockPush).not.toHaveBeenCalled();
    });

    it('should validate required fields', async () => {
      const user = userEvent.setup();
      render(<CreateSpacePage />);

      const submitButton = screen.getByRole('button', { name: /create space/i });
      await user.click(submitButton);

      // HTML5 validation should prevent submission
      const nameInput = screen.getByLabelText(/name/i) as HTMLInputElement;
      expect(nameInput.validity.valid).toBe(false);
    });

    it('should cancel and go back', async () => {
      const user = userEvent.setup();
      render(<CreateSpacePage />);

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      expect(mockBack).toHaveBeenCalled();
    });

    it('should disable form during submission', async () => {
      const user = userEvent.setup();
      render(<CreateSpacePage />);

      const nameInput = screen.getByLabelText(/name/i);
      const capacityInput = screen.getByLabelText(/capacity/i);
      const priceInput = screen.getByLabelText(/price per hour/i);
      const submitButton = screen.getByRole('button', { name: /create space/i });

      await user.type(nameInput, 'New Room');
      await user.type(capacityInput, '10');
      await user.type(priceInput, '50');
      await user.click(submitButton);

      expect(submitButton).toBeDisabled();
    });
  });
});

