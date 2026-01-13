import { useState } from 'react';
import { ChatInterface } from './components/ChatInterface';
import { ConnectionStatus } from './components/ConnectionStatus';

function App() {
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-4">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Medical AI Assistant
          </h1>
          <p className="text-gray-600">
            Get personalized medical guidance powered by advanced AI
          </p>
        </header>

        <div className="mb-4">
          <ConnectionStatus />
        </div>

        <ChatInterface sessionId={sessionId} />
      </div>
    </div>
  );
}

export default App;