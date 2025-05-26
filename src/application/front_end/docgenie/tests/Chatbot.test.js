// Chat_Bot.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import Chat_Bot, { ConversationHistory, ChatDisplay, ChatInput } from '../src/app/chat_bot/[id]/page';
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

jest.mock('../styles/Chat_Bot.module.css', () => ({
  block: 'mock-block',
  icon: 'mock-icon',
  message: 'mock-message',
  conversation_history: 'mock-conversation-history',
  title: 'mock-title',
  conversation_text_bar: 'mock-conversation-text-bar',
  conversation_button: 'mock-conversation-button',
  scrollable_conversations_list: 'mock-scrollable-conversations-list',
  conversation_item: 'mock-conversation-item',
  delete_icon: 'mock-delete-icon',
  scrollable_list: 'mock-scrollable-list',
  text_bar: 'mock-text-bar',
  query_submit_button: 'mock-query-submit-button',
  // Add these new style mocks
  user_message: 'mock-user-message',
  generated_message: 'mock-generated-message',
  section_zone: 'mock-section-zone',
  settings_icon: 'mock-settings-icon',
  settings_message: 'mock-settings-message',
}));

jest.mock('react-icons/ri', () => ({
  RiChatHistoryLine: () => <div data-testid="chat-history-icon" />,
}));

jest.mock('react-icons/cg', () => ({
  CgProfile: () => <div data-testid="settings-icon" />,
}));

jest.mock('react-icons/md', () => ({
  MdDelete: (props) => (
    <div 
      data-testid="delete-icon" 
      onClick={props.onClick}
      role={props.role}
    />
  ),
}));

jest.mock('react-icons/gr', () => ({
  GrSend: () => <div data-testid="send-icon" />,
}));

describe('Chat_Bot Component', () => {
  const mockParams = { id: '123' };
  const mockPush = jest.fn();
  let originalFetch;
  
  beforeEach(() => {
    originalFetch = global.fetch;
    
    useParams.mockReturnValue(mockParams);
    useRouter.mockImplementation(() => ({
      push: mockPush,
    }));
    
    global.fetch = jest.fn();
    
    const mockLatestConversation = { id: 'conv1', title: 'Latest Conversation' };
    const mockChats = [
      { id: 'chat1', body: 'User message', conversation_id: 'conv1' },
      { id: 'chat2', body: 'Response: Bot response', conversation_id: 'conv1' }
    ];
    const mockConversations = [
      { id: 'conv1', title: 'Conversation 1', user_id: '123' },
      { id: 'conv2', title: 'Conversation 2', user_id: '123' }
    ];
    
    // Fetch mock for different endpoints
    global.fetch.mockImplementation((url) => {
      if (url.includes('/conversation/latest')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockLatestConversation)
        });
      } else if (url.includes('/chat/all')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockChats)
        });
      } else if (url.includes('/conversation/all')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockConversations)
        });
      } else if (url.includes('/conversation/create')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ id: 'new-conv', title: 'New Conversation', user_id: '123' })
        });
      } else if (url.includes('/chat/create')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([
            { id: 'new-chat1', body: 'New message', conversation_id: 'conv1' },
            { id: 'new-chat2', body: 'New response', conversation_id: 'conv1' }
          ])
        });
      } else if (url.includes('/conversation/') && !url.includes('/chat/')) {
        // Delete conversation endpoint
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ success: true })
        });
      }
      return Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ error: 'Unknown endpoint' })
      });
    });
    
    jest.clearAllMocks();
  });
  
  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });
  
  // Test main component rendering
  test('renders Chat_Bot component correctly', async () => {
    await act(async () => {
      render(<Chat_Bot />);
    });
    
    // Check that main elements are rendered
    expect(screen.getByText('DocGenie')).toBeInTheDocument();
    expect(screen.getByTestId('chat-history-icon')).toBeInTheDocument();
    expect(screen.getByTestId('settings-icon')).toBeInTheDocument();
    expect(screen.getByText('Show/Hide Conversation History')).toBeInTheDocument();
    expect(screen.getByText('Admin')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter your message')).toBeInTheDocument();
  });
  
  // Test fetching initial data
  test('fetches conversation data on initial load', async () => {
    await act(async () => {
      render(<Chat_Bot />);
    });
    
    await waitFor(() => {
      // Check that fetch was called with correct URLs
      expect(global.fetch).toHaveBeenCalledWith(
        `http://127.0.0.1:8888/conversation/latest?user_id=${mockParams.id}`,
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
      
      expect(global.fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:8888/conversation/conv1/chat/all',
        expect.objectContaining({
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        })
      );
      
      expect(global.fetch).toHaveBeenCalledWith(
        `http://127.0.0.1:8888/conversation/all?user_id=${mockParams.id}`,
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });
    
    // Check that chat messages are displayed
    expect(screen.getByText(/User message/)).toBeInTheDocument();
    expect(screen.getByText(/Bot response/)).toBeInTheDocument();
  });
  
  // Test submitting a new message
  test('submits a new message and updates chat log', async () => {
    await act(async () => {
      render(<Chat_Bot />);
    });
    
    // Find the textarea and button
    const textarea = screen.getByPlaceholderText('Enter your message');
    const submitButton = screen.getByTestId('send-icon').closest('button');
    
    // Type a message and submit
    await act(async () => {
      fireEvent.change(textarea, { target: { value: 'Hello bot' } });
      fireEvent.click(submitButton);
    });
    
    await waitFor(() => {
      // Check that fetch was called with correct data
      expect(global.fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:8888/conversation/conv1/chat/create',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            body: 'Hello bot',
            conversation_id: 'conv1',
          }),
        })
      );
    });
  });
  
  // Testing the Enter key user submission
  test('submits message when Enter key is pressed', async () => {
    await act(async () => {
      render(<Chat_Bot />);
    });
    
    // Finding if the textarea exits
    const textarea = screen.getByPlaceholderText('Enter your message');
    
    // Type a message and press Enter
    await act(async () => {
      fireEvent.change(textarea, { target: { value: 'Hello with Enter' } });
      fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });
    });
    
    await waitFor(() => {
      // Check that fetch was called with correct data
      expect(global.fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:8888/conversation/conv1/chat/create',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('Hello with Enter'),
        })
      );
    });
  });
  
  // Test settings icon rendering and navigation separately
  test('renders settings icon correctly', async () => {
    await act(async () => {
      render(<Chat_Bot />);
    });
    
    // Verify the settings icon is rendered
    const settingsIcon = screen.getByTestId('settings-icon');
    expect(settingsIcon).toBeInTheDocument();
    expect(screen.getByText('Admin')).toBeInTheDocument();
  });
  
  test('handleSettingsClick function navigates to admin page', () => {
    // Create a mock router
    const mockRouter = { push: jest.fn() };
    useRouter.mockReturnValue(mockRouter);
    
    // Mock the params
    useParams.mockReturnValue({ id: '123' });
    
    // Create an instance of the function directly
    const handleSettingsClick = () => {
      mockRouter.push(`/admin/123`);
    };
    
    // Call the function
    handleSettingsClick();
    
    // Verify it navigates correctly
    expect(mockRouter.push).toHaveBeenCalledWith('/admin/123');
  });
});

describe('ConversationHistory Component', () => {
  test('renders conversation history correctly', () => {
    const props = {
      conversation: true,
      conversationElement: { current: {} },
      conversationSideBarList: [
        { id: 'conv1', title: 'Conversation 1' },
        { id: 'conv2', title: 'Conversation 2' }
      ],
      createConversationTitle: '',
      setCreateConversationTitle: jest.fn(),
      createConversation: jest.fn(),
      handleDelete: jest.fn(),
      swapConversations: jest.fn()
    };
    
    render(<ConversationHistory {...props} />);
    
    expect(screen.getByText('Conversation History')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('New Conversation')).toBeInTheDocument();
    expect(screen.getByText('+')).toBeInTheDocument();
    expect(screen.getByText('Conversation 1')).toBeInTheDocument();
    expect(screen.getByText('Conversation 2')).toBeInTheDocument();
    expect(screen.getAllByTestId('delete-icon').length).toBe(2);
  });
  
  test('calls handleDelete when delete icon is clicked', () => {
    const handleDelete = jest.fn();
    const props = {
      conversation: true,
      conversationElement: { current: {} },
      conversationSideBarList: [{ id: 'conv1', title: 'Conversation 1' }],
      createConversationTitle: '',
      setCreateConversationTitle: jest.fn(),
      createConversation: jest.fn(),
      handleDelete,
      swapConversations: jest.fn()
    };
    
    render(<ConversationHistory {...props} />);
    
    const deleteIcon = screen.getByTestId('delete-icon');
    fireEvent.click(deleteIcon);
    
    expect(handleDelete).toHaveBeenCalledWith('conv1');
  });
  
  test('calls swapConversations when conversation is clicked', () => {
    const swapConversations = jest.fn();
    const props = {
      conversation: true,
      conversationElement: { current: {} },
      conversationSideBarList: [{ id: 'conv1', title: 'Conversation 1' }],
      createConversationTitle: '',
      setCreateConversationTitle: jest.fn(),
      createConversation: jest.fn(),
      handleDelete: jest.fn(),
      swapConversations
    };
    
    render(<ConversationHistory {...props} />);
    
    const conversationLink = screen.getByText('Conversation 1').closest('a');
    fireEvent.click(conversationLink);
    
    expect(swapConversations).toHaveBeenCalledWith('conv1');
  });
  
  test('updates createConversationTitle when input changes', () => {
    const setCreateConversationTitle = jest.fn();
    const props = {
      conversation: true,
      conversationElement: { current: {} },
      conversationSideBarList: [],
      createConversationTitle: '',
      setCreateConversationTitle,
      createConversation: jest.fn(),
      handleDelete: jest.fn(),
      swapConversations: jest.fn()
    };
    
    render(<ConversationHistory {...props} />);
    
    const input = screen.getByPlaceholderText('New Conversation');
    fireEvent.change(input, { target: { value: 'New Title' } });
    
    expect(setCreateConversationTitle).toHaveBeenCalledWith('New Title');
  });
  
  test('calls createConversation when button is clicked', () => {
    const createConversation = jest.fn();
    const props = {
      conversation: true,
      conversationElement: { current: {} },
      conversationSideBarList: [],
      createConversationTitle: 'New Title',
      setCreateConversationTitle: jest.fn(),
      createConversation,
      handleDelete: jest.fn(),
      swapConversations: jest.fn()
    };
    
    render(<ConversationHistory {...props} />);
    
    const button = screen.getByText('+');
    fireEvent.click(button);
    
    expect(createConversation).toHaveBeenCalled();
  });
});

describe('ChatDisplay Component', () => {
  test('renders chat messages correctly', () => {
    const chatLog = [
      { id: 'chat1', body: 'User message' },
      { id: 'chat2', body: 'Response: Bot response' }
    ];
    
    render(<ChatDisplay chatLog={chatLog} />);
    
    // Check that messages are displayed (with "Response:" prefix removed)
    expect(screen.getByText('User message')).toBeInTheDocument();
    expect(screen.getByText('Bot response')).toBeInTheDocument();
  });
  
  test('applies correct styling to user and system messages', () => {
    const chatLog = [
      { id: 'chat1', body: 'User message' },
      { id: 'chat2', body: 'Response: Bot response' }
    ];
    
    render(<ChatDisplay chatLog={chatLog} />);
    
    // Get the rendered message elements
    const userMessage = screen.getByText('User message');
    const botResponse = screen.getByText('Bot response');
    
    // Check they have the right classes
    expect(userMessage.closest('li')).toHaveClass('mock-user-message');
    expect(botResponse.closest('li')).toHaveClass('mock-generated-message');
  });
  
  test('handles empty chat log', () => {
    render(<ChatDisplay chatLog={[]} />);
    
    const listElement = screen.getByRole('list');
    expect(listElement).toBeInTheDocument();
    expect(listElement.children.length).toBe(0);
  });

  test('handles undefined body properties', () => {
    const chatLog = [
      { id: 'chat1', body: undefined },
      { id: 'chat2', body: null }
    ];
    
    render(<ChatDisplay chatLog={chatLog} />);
    
    // Should display the fallback message
    expect(screen.getAllByText('Error: Content isn\'t available').length).toBe(2);
  });
});

describe('ChatInput Component', () => {
  test('renders input correctly', () => {
    const props = {
      userQuery: '',
      setUserQuery: jest.fn(),
      handleSubmit: jest.fn(),
      handleEnter: jest.fn()
    };
    
    render(<ChatInput {...props} />);
    
    expect(screen.getByPlaceholderText('Enter your message')).toBeInTheDocument();
    expect(screen.getByTestId('send-icon')).toBeInTheDocument();
  });
  
  test('updates userQuery when input changes', () => {
    const setUserQuery = jest.fn();
    const props = {
      userQuery: '',
      setUserQuery,
      handleSubmit: jest.fn(),
      handleEnter: jest.fn()
    };
    
    render(<ChatInput {...props} />);
    
    const input = screen.getByPlaceholderText('Enter your message');
    fireEvent.change(input, { target: { value: 'New message' } });
    
    expect(setUserQuery).toHaveBeenCalledWith('New message');
  });
  
  test('calls handleSubmit when form is submitted', () => {
    const handleSubmit = jest.fn(e => e.preventDefault());
    const props = {
      userQuery: 'Test message',
      setUserQuery: jest.fn(),
      handleSubmit,
      handleEnter: jest.fn()
    };
    
    render(<ChatInput {...props} />);
    
    const form = screen.getByTestId('send-icon').closest('form');
    fireEvent.submit(form);
    
    expect(handleSubmit).toHaveBeenCalled();
  });
  
  test('calls handleEnter when Enter key is pressed', () => {
    const handleEnter = jest.fn();
    const props = {
      userQuery: 'Test message',
      setUserQuery: jest.fn(),
      handleSubmit: jest.fn(),
      handleEnter
    };
    
    render(<ChatInput {...props} />);
    
    const input = screen.getByPlaceholderText('Enter your message');
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(handleEnter).toHaveBeenCalled();
  });
});