import React from 'react';
import { act, render, fireEvent } from '@testing-library/react';
import Login from '../src/app/page.js';
import { useRouter } from 'next/navigation';

jest.mock('next/font/google', () => ({
  Rubik: () => ({
    className: 'mocked-font-class',
    style: { fontFamily: 'mocked-rubik' },
    subsets: jest.fn(),
    weight: jest.fn(),
  }),
}));

// Mock Routing
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock CSS Module
jest.mock('../styles/Login.module.css', () => ({
  container: 'mock-container',
  loginForm: 'mock-login-form',
  loginTitle: 'mock-login-title',
  formGroup: 'mock-form-group',
  error: 'mock-error',
  success: 'mock-success',
  submitBtn: 'mock-submit-btn',
}));

// Test Environment
describe('Login Component Functions', () => {
  const mockPush = jest.fn();
  let originalFetch;
  
  beforeEach(() => {
    originalFetch = global.fetch;
    
    // Mock router
    useRouter.mockImplementation(() => ({
      push: mockPush,
    }));
    
    // Mock fetch
    global.fetch = jest.fn();
    
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  // Unit test for handleSubmit function with empty email
  // Message displayed if unit test has passed
  test('handleSubmit should show error when email is empty', async () => {

    // Create a spy to track state changes
    const setErrorMock = jest.fn();
    const useStateSpy = jest.spyOn(React, 'useState');
    
    // Mock useState for email, password, error, and success (always the same order as in the original file)
    useStateSpy.mockImplementationOnce(() => ["", jest.fn()]); // email
    useStateSpy.mockImplementationOnce(() => ["password123", jest.fn()]); // password 
    useStateSpy.mockImplementationOnce(() => ["", setErrorMock]); // error
    useStateSpy.mockImplementationOnce(() => [false, jest.fn()]); // success
    
    const { getByRole } = render(<Login />);
    
    // Get the submit button and use fireEvent to trigger submission
    const submitButton = getByRole('button', { name: /login/i });
    
    // Simulate form submission
    await act(async () => {
      fireEvent.click(submitButton);
    });
    
    // Carry out checks
    expect(setErrorMock).toHaveBeenCalledWith("Email is missing");
    expect(global.fetch).not.toHaveBeenCalled();
  });

  // Unit test for handleSubmit function with empty password
  test('handleSubmit should show error when password is empty', async () => {
    const setErrorMock = jest.fn();
    const setEmailMock = jest.fn();
    const useStateSpy = jest.spyOn(React, 'useState');
    
    useStateSpy.mockImplementationOnce(() => ["test@example.com", setEmailMock]);
    useStateSpy.mockImplementationOnce(() => ["", jest.fn()]);
    useStateSpy.mockImplementationOnce(() => ["", setErrorMock]);
    useStateSpy.mockImplementationOnce(() => [false, jest.fn()]);
    
    const { getByRole } = render(<Login />);
    
    // Get the submit button
    const submitButton = getByRole('button', { name: /login/i });
    
    await act(async () => {
      fireEvent.click(submitButton);
    });
    
    expect(setErrorMock).toHaveBeenCalledWith("Password is missing");
    expect(global.fetch).not.toHaveBeenCalled();
  });

  // Unit test for handleSubmit function with successful login
  test('handleSubmit should make API call and redirect on successful login', async () => {

    // Mock successful API response
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: '123' }),
    });
    
    const setErrorMock = jest.fn();
    const setSuccessMock = jest.fn();
    const useStateSpy = jest.spyOn(React, 'useState');
    
    useStateSpy.mockImplementationOnce(() => ["test@example.com", jest.fn()]);
    useStateSpy.mockImplementationOnce(() => ["password123", jest.fn()]);
    useStateSpy.mockImplementationOnce(() => ["", setErrorMock]);
    useStateSpy.mockImplementationOnce(() => [false, setSuccessMock]);
    
    const { getByRole } = render(<Login />);
    
    // Retrieve the submit button
    const submitButton = getByRole('button', { name: /login/i });
    
    await act(async () => {
      fireEvent.click(submitButton);
    });
    
    expect(setErrorMock).toHaveBeenCalledWith("");
    expect(setSuccessMock).toHaveBeenCalledWith(false);
    
    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8888/user/login',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123',
        }),
      }
    );
    
    expect(setSuccessMock).toHaveBeenCalledWith(true);
    expect(mockPush).toHaveBeenCalledWith('/chat_bot/123');
  });

  // Unit test for handleSubmit function with failed login
  test('handleSubmit should not redirect on failed login', async () => {

    // Mock failed API response
    global.fetch.mockResolvedValueOnce({
      ok: false,
    });
    
    const setErrorMock = jest.fn();
    const setSuccessMock = jest.fn();
    const useStateSpy = jest.spyOn(React, 'useState');
    
    useStateSpy.mockImplementationOnce(() => ["test@example.com", jest.fn()]);
    useStateSpy.mockImplementationOnce(() => ["password123", jest.fn()]);
    useStateSpy.mockImplementationOnce(() => ["", setErrorMock]);
    useStateSpy.mockImplementationOnce(() => [false, setSuccessMock]);
    
    const { getByRole } = render(<Login />);
    
    const submitButton = getByRole('button', { name: /login/i });
    
    await act(async () => {
      fireEvent.click(submitButton);
    });
    
    expect(global.fetch).toHaveBeenCalled();
    expect(setSuccessMock).not.toHaveBeenCalledWith(true);
    expect(mockPush).not.toHaveBeenCalled();
  });

  // Unit test for email input change handler
  test('setEmail should be called when email input changes', () => {
    const setEmailMock = jest.fn();
    const useStateSpy = jest.spyOn(React, 'useState');
    
    useStateSpy.mockImplementationOnce(() => ["", setEmailMock]); 
    useStateSpy.mockImplementationOnce(() => ["", jest.fn()]); 
    useStateSpy.mockImplementationOnce(() => ["", jest.fn()]); 
    useStateSpy.mockImplementationOnce(() => [false, jest.fn()]);
    
    const { getByLabelText } = render(<Login />);
    
    // Find the email input
    const emailInput = getByLabelText(/email/i);
    
    // Simulate onChange event using fireEvent
    fireEvent.change(emailInput, { target: { value: 'new@example.com' } });
    
    // Check if setEmail was called with the new value
    expect(setEmailMock).toHaveBeenCalledWith('new@example.com');
  });

  // Unit test for password input change handler
  test('setPassword should be called when password input changes', () => {
    const setPasswordMock = jest.fn();
    const useStateSpy = jest.spyOn(React, 'useState');
    
    useStateSpy.mockImplementationOnce(() => ["", jest.fn()]); 
    useStateSpy.mockImplementationOnce(() => ["", setPasswordMock]); 
    useStateSpy.mockImplementationOnce(() => ["", jest.fn()]); 
    useStateSpy.mockImplementationOnce(() => [false, jest.fn()]);
    
    const { getByLabelText } = render(<Login />);
    
    const passwordInput = getByLabelText(/password/i);
    
    fireEvent.change(passwordInput, { target: { value: 'newpassword' } });
    
    expect(setPasswordMock).toHaveBeenCalledWith('newpassword');
  });

  // Testing email validation with whitespace
  test('handleSubmit should trim email before validation', async () => {
    const setErrorMock = jest.fn();
    const useStateSpy = jest.spyOn(React, 'useState');
    
    useStateSpy.mockImplementationOnce(() => ["  ", jest.fn()]); // email with only spaces
    useStateSpy.mockImplementationOnce(() => ["password123", jest.fn()]); // password
    useStateSpy.mockImplementationOnce(() => ["", setErrorMock]); // error
    useStateSpy.mockImplementationOnce(() => [false, jest.fn()]); // success
    
    const { getByRole } = render(<Login />);
    
    const submitButton = getByRole('button', { name: /login/i });
    
    await act(async () => {
      fireEvent.click(submitButton);
    });
    
    expect(setErrorMock).toHaveBeenCalledWith("Email is missing");
    expect(global.fetch).not.toHaveBeenCalled();
  });
});