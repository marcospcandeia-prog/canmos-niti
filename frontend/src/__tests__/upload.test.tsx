import "@testing-library/jest-dom/jest-globals"
import { render, screen, waitFor, fireEvent } from "@testing-library/react"
import UploadPage from "@/app/documents/upload/page"
import { ToastProvider } from "@/components/Toast"

// UploadPage surfaces validation errors through the Toast context, so it must be
// rendered inside a ToastProvider for those messages to appear in the DOM.
const renderPage = () => render(<ToastProvider><UploadPage /></ToastProvider>)

const mockGet = jest.fn()
const mockPost = jest.fn()
const mockDelete = jest.fn()

jest.mock("@/lib/api", () => ({
  get: (...args: unknown[]) => mockGet(...args),
  post: (...args: unknown[]) => mockPost(...args),
  delete: (...args: unknown[]) => mockDelete(...args),
  __esModule: true,
  api: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
  default: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
}))

const mockDocuments = [
  {
    id: "doc-1",
    nome_original: "comprovante.pdf",
    tipo: "recibo_medico",
    mime_type: "application/pdf",
    status: "processed",
    created_at: "2026-06-03T22:00:00Z",
  },
  {
    id: "doc-2",
    nome_original: "nota-fiscal.jpg",
    tipo: null,
    mime_type: "image/jpeg",
    status: "uploaded",
    created_at: "2026-06-02T15:00:00Z",
  },
]

beforeEach(() => {
  jest.clearAllMocks()
  mockGet.mockResolvedValue({ data: [] })
  mockPost.mockResolvedValue({ data: { id: "new-doc" } })
  mockDelete.mockResolvedValue({})
})

describe("UploadPage", () => {
  it("shows loading state for documents", () => {
    mockGet.mockImplementation(() => new Promise(() => {}))
    renderPage()
    expect(screen.getByText("Carregando documentos...")).toBeInTheDocument()
  })

  it("renders upload area with drag-and-drop text", async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText("Upload de Documentos")).toBeInTheDocument()
    })

    expect(screen.getByText("Arraste arquivos aqui")).toBeInTheDocument()
    expect(screen.getByText("Selecionar Arquivos")).toBeInTheDocument()
  })

  it("shows empty state when no documents", async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText("Nenhum documento enviado ainda.")).toBeInTheDocument()
    })
  })

  it("renders document list", async () => {
    mockGet.mockResolvedValue({ data: mockDocuments })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("comprovante.pdf")).toBeInTheDocument()
    })

    expect(screen.getByText("nota-fiscal.jpg")).toBeInTheDocument()
    expect(screen.getByText("Processado")).toBeInTheDocument()
    expect(screen.getByText("Pendente")).toBeInTheDocument()
  })

  it("renders stats header", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockDocuments })
      .mockResolvedValueOnce({ data: { total: 5, processados: 3, pendentes: 2 } })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("Total:")).toBeInTheDocument()
    })

    expect(screen.getByText("5")).toBeInTheDocument()
  })

  it("calls api.get for documents and stats on mount", async () => {
    renderPage()

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith("/documents")
    })

    expect(mockGet).toHaveBeenCalledWith("/documents/stats")
  })

  function getFileInput(): HTMLInputElement {
    return document.querySelector('input[type="file"]')!
  }

  it("validates file type on upload", async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText("Selecionar Arquivos")).toBeInTheDocument()
    })

    const file = new File(["test"], "test.exe", { type: "application/x-msdownload" })
    const input = getFileInput()

    Object.defineProperty(input, "files", { value: [file] })
    fireEvent.change(input)

    await waitFor(() => {
      expect(screen.getByText(/Tipo de arquivo não permitido/)).toBeInTheDocument()
    })
  })

  it("validates file size on upload", async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText("Selecionar Arquivos")).toBeInTheDocument()
    })

    const bigFile = new File(["x".repeat(11 * 1024 * 1024)], "big.pdf", { type: "application/pdf" })
    const input = getFileInput()

    Object.defineProperty(input, "files", { value: [bigFile] })
    fireEvent.change(input)

    await waitFor(() => {
      expect(screen.getByText(/Arquivo muito grande/)).toBeInTheDocument()
    })
  })

  it("shows success message after upload", async () => {
    mockGet.mockResolvedValue({ data: [] })
    mockPost.mockResolvedValue({ data: { id: "new-doc" } })

    jest.useFakeTimers()

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("Selecionar Arquivos")).toBeInTheDocument()
    })

    const pdfFile = new File(["test"], "doc.pdf", { type: "application/pdf" })
    const input = getFileInput()

    fireEvent.change(input, { target: { files: [pdfFile] } })

    await waitFor(() => {
      expect(screen.getByText(/Upload concluído com sucesso/)).toBeInTheDocument()
    })

    jest.useRealTimers()
  })

  it("deletes a document", async () => {
    mockGet.mockResolvedValue({ data: mockDocuments })
    jest.spyOn(window, "confirm").mockReturnValue(true)

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("comprovante.pdf")).toBeInTheDocument()
    })

    const deleteButtons = screen.getAllByText("Excluir")
    fireEvent.click(deleteButtons[0])

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith("/documents/doc-1")
    })
  })

  it("handles upload error message", async () => {
    mockPost.mockRejectedValue({
      response: { data: { detail: "Falha no servidor" } },
    })

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("Selecionar Arquivos")).toBeInTheDocument()
    })

    const pdfFile = new File(["test"], "doc.pdf", { type: "application/pdf" })
    const input = getFileInput()
    fireEvent.change(input, { target: { files: [pdfFile] } })

    await waitFor(() => {
      expect(screen.getByText("Falha no servidor")).toBeInTheDocument()
    })
  })

  it("does not call delete when user cancels confirmation", async () => {
    mockGet.mockResolvedValue({ data: mockDocuments })
    jest.spyOn(window, "confirm").mockReturnValue(false)

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("comprovante.pdf")).toBeInTheDocument()
    })

    const deleteButtons = screen.getAllByText("Excluir")
    fireEvent.click(deleteButtons[0])

    expect(mockDelete).not.toHaveBeenCalled()
  })

  it("shows alert on delete error", async () => {
    mockGet.mockResolvedValue({ data: mockDocuments })
    jest.spyOn(window, "confirm").mockReturnValue(true)
    mockDelete.mockRejectedValue({
      response: { data: { detail: "Falha ao excluir" } },
    })
    jest.spyOn(window, "alert").mockImplementation(() => {})

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("comprovante.pdf")).toBeInTheDocument()
    })

    const deleteButtons = screen.getAllByText("Excluir")
    fireEvent.click(deleteButtons[0])

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalled()
    })
  })

  it("handles drag events and drag-and-drop upload", async () => {
    mockPost.mockResolvedValue({ data: { id: "dropped-doc" } })

    const { container } = renderPage()

    await waitFor(() => {
      expect(screen.getByText("Arraste arquivos aqui")).toBeInTheDocument()
    })

    const dropZone = container.querySelector('[class*="border-dashed"]')!

    fireEvent.dragOver(dropZone)
    expect(screen.getByText("Solte os arquivos aqui")).toBeInTheDocument()

    fireEvent.dragLeave(dropZone)
    expect(screen.getByText("Arraste arquivos aqui")).toBeInTheDocument()

    const pdfFile = new File(["test"], "dragged.pdf", { type: "application/pdf" })
    fireEvent.drop(dropZone, {
      dataTransfer: { files: [pdfFile] },
    })

    await waitFor(() => {
      expect(screen.getByText("Upload concluído com sucesso!")).toBeInTheDocument()
    })
  })

  it("handles stats load error gracefully", async () => {
    mockGet
      .mockResolvedValueOnce({ data: [] })
      .mockRejectedValueOnce(new Error("Stats error"))

    renderPage()

    await waitFor(() => {
      expect(screen.getByText("Upload de Documentos")).toBeInTheDocument()
    })

    expect(screen.getByText("Total:")).toBeInTheDocument()
    expect(screen.getAllByText("0").length).toBe(3)
  })
})
