import { create } from 'zustand'
import { api } from '@/lib/api'
import type { Message, Conversation } from '@/types'

interface ChatState {
  messages: Message[]
  conversations: Conversation[]
  conversationId: string | null
  loading: boolean
  modelReady: boolean | null
  showHistory: boolean
  sendMessage: (content: string) => Promise<void>
  loadConversations: () => Promise<void>
  loadConversation: (id: string) => Promise<void>
  clearChat: () => Promise<void>
  toggleHistory: () => void
  setModelReady: (v: boolean | null) => void
  addIntroMessage: () => void
}

const INTRO_MESSAGE: Message = {
  id: 'intro',
  role: 'assistant',
  content:
    'Ola! Eu sou o assistente IA do CANMOS-NITI. Posso ajudar com duvidas sobre:\n\n' +
    '- Declaracao de Imposto de Renda (IRPF)\n' +
    '- Deducoes permitidas\n' +
    '- Prazos e obrigacoes fiscais\n' +
    '- Documentacao necessaria\n\n' +
    'Como posso ajudar hoje?',
  timestamp: new Date(),
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  conversations: [],
  conversationId: null,
  loading: false,
  modelReady: null,
  showHistory: false,

  sendMessage: async (content: string) => {
    const { conversationId } = get()

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }

    set((s) => ({ messages: [...s.messages, userMessage], loading: true }))

    try {
      const res = await api.post('/ai/chat', {
        mensagem: content,
        conversation_id: conversationId,
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.data.resposta,
        timestamp: new Date(),
      }

      const newMessages = [...get().messages, assistantMessage]

      if (res.data.fontes?.length > 0) {
        newMessages.push({
          id: (Date.now() + 2).toString() + '-sources',
          role: 'assistant',
          content: `*Fontes consultadas:* ${res.data.fontes.join(', ')}`,
          timestamp: new Date(),
        })
      }

      set({
        messages: newMessages,
        conversationId: res.data.conversation_id,
        loading: false,
      })
    } catch (err: any) {
      set((s) => ({
        messages: [
          ...s.messages,
          {
            id: (Date.now() + 1).toString(),
            role: 'assistant' as const,
            content:
              err.response?.data?.detail ||
              'Erro ao processar mensagem. Verifique se o Ollama está rodando e tente novamente.',
            timestamp: new Date(),
          },
        ],
        loading: false,
      }))
    }
  },

  loadConversations: async () => {
    try {
      const res = await api.get('/ai/conversations')
      set({ conversations: res.data })
    } catch {
    }
  },

  loadConversation: async (id: string) => {
    try {
      const res = await api.get(`/ai/conversations/${id}/messages`)
      const loaded: Message[] = res.data.map((m: any) => ({
        id: m.id.toString(),
        role: m.role,
        content: m.content,
        timestamp: new Date(m.created_at),
      }))
      set({ messages: loaded, conversationId: id, showHistory: false })
    } catch {
    }
  },

  clearChat: async () => {
    try {
      await api.post('/ai/clear')
    } catch {
    }
    set({ messages: [INTRO_MESSAGE], conversationId: null })
  },

  toggleHistory: () => {
    const { showHistory } = get()
    if (!showHistory) {
      get().loadConversations()
    }
    set({ showHistory: !showHistory })
  },

  setModelReady: (v) => set({ modelReady: v }),

  addIntroMessage: () => set({ messages: [INTRO_MESSAGE] }),
}))
