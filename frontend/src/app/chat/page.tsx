'use client';

import { useState, useRef, useEffect } from 'react';
import api from '@/lib/api';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { useChatStore } from '@/stores/chatStore';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    conversations,
    conversationId,
    loading,
    modelReady,
    showHistory,
    sendMessage,
    loadConversations,
    loadConversation,
    clearChat,
    toggleHistory,
    setModelReady,
    addIntroMessage,
  } = useChatStore();

  useEffect(() => {
    checkHealth();
    addIntroMessage();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkHealth = async () => {
    try {
      const response = await api.get('/ai/health');
      setModelReady(response.data.llm);
    } catch {
      setModelReady(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const message = input.trim();
    setInput('');
    await sendMessage(message);
  };

  return (
    <div className="flex h-screen">
      {showHistory && (
        <div className="w-72 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h2 className="font-semibold text-gray-900">Histórico</h2>
            <p className="text-xs text-gray-500">Conversas anteriores</p>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {conversations.length === 0 ? (
              <div className="p-4 text-center text-sm text-gray-500">Nenhuma conversa anterior</div>
            ) : (
              <div className="space-y-1">
                {conversations.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => loadConversation(conv.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition hover:bg-gray-100 ${
                      conv.id === conversationId ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                    }`}
                  >
                    <p className="font-medium truncate">{conv.titulo}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {new Date(conv.created_at).toLocaleDateString('pt-BR')}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col">
        <div className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button onClick={toggleHistory} className="text-gray-500 hover:text-gray-700 transition">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Assistente IA</h1>
                <p className="text-sm text-gray-600">Tire suas dúvidas tributárias</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {modelReady !== null && (
                <span className={`flex items-center text-xs ${modelReady ? 'text-green-600' : 'text-red-600'}`}>
                  <span className={`w-2 h-2 rounded-full mr-1 ${modelReady ? 'bg-green-500' : 'bg-red-500'}`} />
                  {modelReady ? 'Ollama Online' : 'Ollama Offline'}
                </span>
              )}
              <button
                onClick={clearChat}
                className="px-3 py-1 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Nova Conversa
              </button>
            </div>
          </div>
        </div>

        <div className="flex-1 max-w-5xl w-full mx-auto px-8 py-6 flex flex-col">
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                Inicie uma conversa ou selecione uma anterior
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-md'
                        : msg.content.startsWith('*')
                        ? 'bg-gray-100 text-gray-500 text-xs italic rounded-bl-md'
                        : 'bg-white border border-gray-200 rounded-bl-md shadow-sm'
                    }`}
                  >
                    <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                    <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-200' : 'text-gray-400'}`}>
                      {msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))
            )}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {modelReady === false && (
            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                O Ollama não está rodando. O assistente IA requer o Ollama com o modelo llama3.2:3b.
                Execute: <code className="bg-yellow-100 px-1 rounded">docker compose up -d ollama && docker compose exec ollama ollama pull llama3.2:3b</code>
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-gray-200 shadow-sm p-2">
            <div className="flex items-end space-x-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder="Digite sua dúvida tributária..."
                rows={2}
                disabled={loading}
                className="flex-1 resize-none px-4 py-2 text-sm border-none focus:ring-0 outline-none disabled:bg-transparent"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                )}
                <span>Enviar</span>
              </button>
            </div>
            <p className="px-4 pb-1 text-xs text-gray-400">Shift+Enter para nova linha</p>
          </form>
        </div>
      </div>
    </div>
  );
}
