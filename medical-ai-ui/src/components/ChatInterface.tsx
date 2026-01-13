import { useState, useRef, useEffect, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { ChatMessage, WebSocketMessage, QueryRequest } from '../types/medical.types';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { StreamingMessage } from './StreamingMessage';

interface ChatInterfaceProps {
  sessionId: string;
}

export const ChatInterface = ({ sessionId }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const streamingMessageRef = useRef<string>('');

  const handleWebSocketMessage = useCallback((wsMessage: WebSocketMessage) => {
    switch (wsMessage.type) {
      case 'status':
        // Update streaming message with status
        setCurrentStreamingMessage(wsMessage.data);
        streamingMessageRef.current = wsMessage.data;
        break;

      case 'chunk':
        // Append chunk to current streaming message
        setCurrentStreamingMessage(prev => {
          const newMessage = prev + wsMessage.data;
          streamingMessageRef.current = newMessage;
          return newMessage;
        });
        break;

      case 'complete':
        // Finalize the streaming message
        setIsStreaming(false);
        if (streamingMessageRef.current) {
          const assistantMessage: ChatMessage = {
            id: `msg_${Date.now()}_${Math.random()}`,
            type: 'assistant',
            content: streamingMessageRef.current,
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, assistantMessage]);
          setCurrentStreamingMessage('');
          streamingMessageRef.current = '';
        }
        break;

      case 'error':
        setIsStreaming(false);
        const errorMessage: ChatMessage = {
          id: `msg_${Date.now()}_${Math.random()}`,
          type: 'assistant',
          content: `Error: ${wsMessage.data}`,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
        setCurrentStreamingMessage('');
        streamingMessageRef.current = '';
        break;
    }
  }, []);

  const { connectionState, sendMessage, clearMessages } = useWebSocket(
    'ws://localhost:8000/ws/query',
    handleWebSocketMessage
  );

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage]);

  const handleSendMessage = (query: string) => {
    if (!query.trim()) return;

    // Clear previous messages for new session
    clearMessages();

    // Add user message
    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}_${Math.random()}`,
      type: 'user',
      content: query,
      timestamp: new Date(),
    };
    setMessages([userMessage]);

    // Start streaming
    setIsStreaming(true);
    setCurrentStreamingMessage('');
    streamingMessageRef.current = '';

    // Send to WebSocket
    const request: QueryRequest = {
      query,
      session_id: sessionId,
      model: 'google/gemini-3-flash-preview'
    };
    sendMessage(request);
  };





  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="h-96 overflow-y-auto p-4">
        <MessageList messages={messages} />
        {isStreaming && (
          <StreamingMessage content={currentStreamingMessage} />
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t p-4">
        <InputBox
          onSendMessage={handleSendMessage}
          disabled={connectionState !== 'connected' || isStreaming}
        />
      </div>
    </div>
  );
};