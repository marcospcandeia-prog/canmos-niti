import { create } from 'zustand'
import { api } from '@/lib/api'
import type { Document, UploadingFile } from '@/types'

interface DocumentStats {
  total: number
  processados: number
  pendentes: number
}

interface DocumentState {
  documents: Document[]
  uploadingFiles: UploadingFile[]
  stats: DocumentStats
  loading: boolean
  initialized: boolean
  loadDocuments: () => Promise<void>
  loadStats: () => Promise<void>
  uploadFile: (file: File) => Promise<string | null>
  deleteDocument: (id: string) => Promise<void>
  processOcr: (id: string) => Promise<void>
  clearUploadingFiles: () => void
  init: () => Promise<void>
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [],
  uploadingFiles: [],
  stats: { total: 0, processados: 0, pendentes: 0 },
  loading: false,
  initialized: false,

  init: async () => {
    if (get().initialized) return
    set({ initialized: true })
    await get().loadDocuments()
    await get().loadStats()
  },

  loadDocuments: async () => {
    set({ loading: true })
    try {
      const res = await api.get('/documents')
      set({ documents: res.data })
    } catch {
    } finally {
      set({ loading: false })
    }
  },

  loadStats: async () => {
    try {
      const res = await api.get('/documents/stats')
      set({ stats: res.data })
    } catch {
    }
  },

  uploadFile: async (file: File) => {
    const idx = get().uploadingFiles.length
    set((s) => ({
      uploadingFiles: [...s.uploadingFiles, { file, progress: 0, status: 'uploading' }],
    }))

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          const progress = e.total ? Math.round((e.loaded * 100) / e.total) : 0
          set((s) => ({
            uploadingFiles: s.uploadingFiles.map((f, i) =>
              i === idx ? { ...f, progress } : f
            ),
          }))
        },
      })

      set((s) => ({
        uploadingFiles: s.uploadingFiles.map((f, i) =>
          i === idx ? { ...f, status: 'success' as const, progress: 100, documentId: res.data.id } : f
        ),
      }))

      await get().loadDocuments()
      await get().loadStats()

      setTimeout(() => {
        set((s) => ({
          uploadingFiles: s.uploadingFiles.filter((_, i) => i !== idx),
        }))
      }, 3000)

      return res.data.id
    } catch (err: any) {
      const error = err.response?.data?.detail || 'Erro ao fazer upload'
      set((s) => ({
        uploadingFiles: s.uploadingFiles.map((f, i) =>
          i === idx ? { ...f, status: 'error' as const, error } : f
        ),
      }))
      return null
    }
  },

  deleteDocument: async (id: string) => {
    await api.delete(`/documents/${id}`)
    set((s) => ({ documents: s.documents.filter((d) => d.id !== id) }))
    await get().loadStats()
  },

  processOcr: async (id: string) => {
    await api.post(`/ocr/process/${id}`)
    await get().loadDocuments()
  },

  clearUploadingFiles: () => set({ uploadingFiles: [] }),
}))
