'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import api from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatResponse {
  resposta: string;
  conversation_id: string;
  model: string;
  fontes: string[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'intro',
      role: 'assistant',
      content: 'Ola! Eu sou o assistente IA do CANMOS-NITI. Posso ajudar com duvidas sobre:\n\n• Declaracao de Imposto de Renda (IRPF)\n• Deducoes permitidas\n• Prazos e obrigacoes fiscais\n• Documentacao necessaria\n\nComo posso ajudar hoje?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [modelReady, setModelReady] = useState<boolean | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    checkHealth();
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

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post<ChatResponse>('/ai/chat', {
        mensagem: userMessage.content,
        conversation_id: conversationId,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.resposta,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setConversationId(response.data.conversation_id);

      if (response.data.fontes.length > 0) {
        setMessages(prev => [
          ...prev,
          {
            id: (Date.now() + 2).toString() + '-sources',
            role: 'assistant',
            content: `*Fontes consultadas:* ${response.data.fontes.join(', ')}`,
            timestamp: new Date(),
          },
        ]);
      }
    } catch (err: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: err.response?.data?.detail || 'Erro ao processar mensagem. Verifique se o Ollama esta rodando.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await api.post('/ai/clear');
    } catch {
      // ignore
    }
    setMessages([
      {
        id: 'intro',
        role: 'assistant',
        content: 'Conversa reiniciada! Como posso ajudar?',
        timestamp: new Date(),
      },
    ]);
    setConversationId(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
                ← Dashboard
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Assistente IA</h1>
            </div>
            <div className="flex items-center space-x-3">
              {modelReady !== null && (
                <span className={`flex items-center text-xs ${modelReady ? 'text-green-600' : 'text-red-600'}`}>
                  <span className={`w-2 h-2 rounded-full mr-1 ${modelReady ? 'bg-green-500' : 'bg-red-500'}`}></span>
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
      </div>

      {/* Chat Area */}
      <div className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-md'
                    : msg.content.startsWith('*')
                    ? 'bg-gray-100 text-gray-500 text-xs italic rounded-bl-md'
                    : 'bg-white border border-gray-200 rounded-bl-md shadow-sm'
                }`}
              >
                <p className="whitespace-pre-wrap text-sm leading-relaxed">
                  {msg.content}
                </p>
                <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-200' : 'text-gray-400'}`}>
                  {msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Model Info */}
        {modelReady === false && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              O Ollama nao esta rodando. O assistente IA requer o Ollama com o modelo llama3.2:3b.
              Execute: <code className="bg-yellow-100 px-1 rounded">docker compose up -d ollama && docker compose exec ollama ollama pull llama3.2:3b</code>
            </p>
          </div>
        )}

        {/* Input Area */}
        <form onSubmit={sendMessage} className="bg-white rounded-2xl border border-gray-200 shadow-sm p-2">
          <div className="flex items-end space-x-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(e);
                }
              }}
              placeholder="Digite sua duvida tributaria..."
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
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
              <span>Enviar</span>
            </button>
          </div>
          <p className="px-4 pb-1 text-xs text-gray-400">
            Shift+Enter para nova linha
          </p>
        </form>
      </div>
    </div>
  );
}
