// AdminPage.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import AdminPage from '../src/app/admin/[id]/page.js';
import { useParams, useRouter } from 'next/navigation';

// Mock the Next.js modules
jest.mock('next/font/google', () => ({
  Rubik: () => ({
    className: 'mocked-font-class',
    style: { fontFamily: 'mocked-rubik' },
    subsets: jest.fn(),
    weight: jest.fn(),
  }),
}));

jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
  useRouter: jest.fn(),
}));

// Mock the CSS modules
jest.mock('../styles/Chat_Bot.module.css', () => ({
  block: 'mock-block',
}));

jest.mock('../styles/Admin.module.css', () => ({
  container: 'mock-container',
  searchContainer: 'mock-search-container',
  searchField: 'mock-search-field',
  searchButton: 'mock-search-button',
  table: 'mock-table',
  tableHeader: 'mock-table-header',
  tableHeaderCell: 'mock-table-header-cell',
  tableCell: 'mock-table-cell',
}));

describe('AdminPage Component', () => {
  const mockParams = { id: '123' };
  const mockPush = jest.fn();
  let originalFetch;
  
  beforeEach(() => {
    originalFetch = global.fetch;
    
    useParams.mockReturnValue(mockParams);
    useRouter.mockReturnValue({
      push: mockPush,
    });
    
    global.fetch = jest.fn();
    
    const mockUserData = {
      id: '123',
      username: 'testuser',
      email: 'test@example.com',
      is_admin: true,
      permissions: [
        { id: 1, permission_name: 'DATABASE' },
        { id: 2, permission_name: 'WEBHOOK' }
      ]
    };
    
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockUserData
    });
    
    jest.clearAllMocks();
  });
  
  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });
  
  // Testing the main component rendering
  test('renders AdminPage component correctly', async () => {
    await act(async () => {
      render(<AdminPage />);
    });
    
    // Checking that main elements are rendered
    expect(screen.getByText('DocGenie')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter User ID')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument();
    
    // Wait for data to load onto the page and check user data is displayed
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      expect(screen.getByText('testuser')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
      expect(screen.getByText('true')).toBeInTheDocument();
      expect(screen.getByText('DATABASE')).toBeInTheDocument();
      expect(screen.getByText('WEBHOOK')).toBeInTheDocument();
    });
  });
  
  // Test loading state
  test('displays loading state while fetching data', async () => {
    // Delay the fetch resolution to ensure we can check the loading state
    global.fetch.mockImplementationOnce(() => 
      new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: true,
            json: async () => ({ id: '123', username: 'testuser', email: 'test@example.com', is_admin: true, permissions: [] })
          });
        }, 100);
      })
    );
    
    render(<AdminPage />);
    
    // Loading state should be visible
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
  });
  
  // Test fetch user data
  test('fetches user data on initial load', async () => {
    await act(async () => {
      render(<AdminPage />);
    });
    
    // Verify fetch was called with the correct URL
    expect(global.fetch).toHaveBeenCalledWith(`http://127.0.0.1:8888/user/${mockParams.id}`);
    
    // Wait for data to load and check user data
    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument();
    });
  });
  
  // Test handling of API failure
  test('handles API failure gracefully', async () => {
    // Mock an API failure
    global.fetch.mockResolvedValueOnce({
      ok: false
    });
    
    await act(async () => {
      render(<AdminPage />);
    });
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    
    // No user data should be displayed
    expect(screen.queryByText('ID')).not.toBeInTheDocument();
    expect(screen.queryByText('Username')).not.toBeInTheDocument();
  });
  
  // Test search functionality
  test('allows searching for a different user', async () => {
    await act(async () => {
      render(<AdminPage />);
    });
    
    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument();
    });
    
    const input = screen.getByPlaceholderText('Enter User ID');
    fireEvent.change(input, { target: { value: '456' } });
    
    // Click the search button
    const searchButton = screen.getByRole('button', { name: 'Search' });
    await act(async () => {
      fireEvent.click(searchButton);
    });
    
    // Verify router.push was called with the new user ID
    expect(mockPush).toHaveBeenCalledWith('/admin/456');
    
    // Verify fetch was called with the updated URL
    expect(global.fetch).toHaveBeenCalledWith(`http://127.0.0.1:8888/user/${mockParams.id}`);
  });
  
  // Test user ID input
  test('updates userId state when input changes', async () => {
    await act(async () => {
      render(<AdminPage />);
    });
    
    const input = screen.getByPlaceholderText('Enter User ID');
    
    // Update the input value
    fireEvent.change(input, { target: { value: '789' } });
    
    // Check that the input value was updated
    expect(input.value).toBe('789');
  });
  
  // Test rendering of the permissions list
  test('renders permissions list correctly', async () => {
    await act(async () => {
      render(<AdminPage />);
    });
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Permissions')).toBeInTheDocument();
    });
    
    // Check that permissions are rendered as list items
    const permissionItems = screen.getAllByRole('listitem');
    expect(permissionItems).toHaveLength(2);
    expect(permissionItems[0]).toHaveTextContent('DATABASE');
    expect(permissionItems[1]).toHaveTextContent('WEBHOOK');
  });
  
  // Testing with user having no permissions
  test('renders empty permissions list when user has no permissions', async () => {
    // Mocking a user with no permissions
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: '123',
        username: 'testuser',
        email: 'test@example.com',
        is_admin: false,
        permissions: []
      })
    });
    
    await act(async () => {
      render(<AdminPage />);
    });
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Permissions')).toBeInTheDocument();
    });
    
    // There should be no list items for permissions
    expect(screen.queryAllByRole('listitem')).toHaveLength(0);
  });
});