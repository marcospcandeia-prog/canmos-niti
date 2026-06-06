import "@testing-library/jest-dom/jest-globals"
import { render, screen, waitFor, fireEvent } from "@testing-library/react"
import ChatPage from "@/app/chat/page"

const mockGet = jest.fn()
const mockPost = jest.fn()

jest.mock("@/lib/api", () => ({
  get: (...args: unknown[]) => mockGet(...args),
  post: (...args: unknown[]) => mockPost(...args),
  __esModule: true,
  default: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
  },
}))

beforeAll(() => {
  Element.prototype.scrollIntoView = jest.fn()
})

beforeEach(() => {
  jest.clearAllMocks()
  mockGet.mockResolvedValue({ data: { llm: true } })
  mockPost.mockResolvedValue({
    data: {
      resposta: "O imposto de renda é calculado com base na tabela progressiva.",
      conversation_id: "conv-123",
      model: "llama3.2:3b",
      fontes: [],
    },
  })
})

describe("ChatPage", () => {
  it("shows initial assistant message", async () => {
    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByText(/assistente IA do CANMOS-NITI/)).toBeInTheDocument()
    })
  })

  it("shows Ollama online status", async () => {
    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByText("Ollama Online")).toBeInTheDocument()
    })
  })

  it("shows Ollama offline status on health check failure", async () => {
    mockGet.mockRejectedValue(new Error("Ollama not running"))

    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByText("Ollama Offline")).toBeInTheDocument()
    })
  })

  it("shows Ollama offline warning banner", async () => {
    mockGet.mockRejectedValue(new Error("Ollama not running"))

    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByText(/Ollama nao esta rodando/)).toBeInTheDocument()
    })
  })

  it("sends a message and receives response", async () => {
    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText("Digite sua duvida tributaria...")).toBeInTheDocument()
    })

    const textarea = screen.getByPlaceholderText("Digite sua duvida tributaria...")
    fireEvent.change(textarea, { target: { value: "Como declarar rendimentos?" } })

    fireEvent.submit(screen.getByText("Enviar").closest("form")!)

    await waitFor(() => {
      expect(screen.getByText("Como declarar rendimentos?")).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByText(/calculado com base na tabela progressiva/)).toBeInTheDocument()
    })
  })

  it("shows loading spinner while message sends", async () => {
    mockPost.mockImplementation(() => new Promise(() => {}))

    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText("Digite sua duvida tributaria...")).toBeInTheDocument()
    })

    const textarea = screen.getByPlaceholderText("Digite sua duvida tributaria...")
    fireEvent.change(textarea, { target: { value: "Test message" } })
    fireEvent.submit(screen.getByText("Enviar").closest("form")!)

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /enviar/i })).toBeDisabled()
    })
  })

  it("handles API error gracefully", async () => {
    mockPost.mockRejectedValue({
      response: { data: { detail: "Erro interno no servidor" } },
    })

    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText("Digite sua duvida tributaria...")).toBeInTheDocument()
    })

    const textarea = screen.getByPlaceholderText("Digite sua duvida tributaria...")
    fireEvent.change(textarea, { target: { value: "Test error" } })
    fireEvent.submit(screen.getByText("Enviar").closest("form")!)

    await waitFor(() => {
      expect(screen.getByText("Erro interno no servidor")).toBeInTheDocument()
    })
  })

  it("handles API error without detail gracefully", async () => {
    mockPost.mockRejectedValue(new Error("Network error"))

    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText("Digite sua duvida tributaria...")).toBeInTheDocument()
    })

    const textarea = screen.getByPlaceholderText("Digite sua duvida tributaria...")
    fireEvent.change(textarea, { target: { value: "Test error" } })
    fireEvent.submit(screen.getByText("Enviar").closest("form")!)

    await waitFor(() => {
      expect(screen.getByText(/Ollama esta rodando/)).toBeInTheDocument()
    })
  })

  it("clears chat on new conversation", async () => {
    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByText("Nova Conversa")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Nova Conversa"))

    await waitFor(() => {
      expect(screen.getByText("Conversa reiniciada! Como posso ajudar?")).toBeInTheDocument()
    })
  })

  it("shows sources when provided", async () => {
    mockPost.mockResolvedValue({
      data: {
        resposta: "Conforme a Receita Federal...",
        conversation_id: "conv-456",
        model: "llama3.2:3b",
        fontes: ["Lei 9.250/95", "Instrução Normativa RFB nº 2.000"],
      },
    })

    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText("Digite sua duvida tributaria...")).toBeInTheDocument()
    })

    const textarea = screen.getByPlaceholderText("Digite sua duvida tributaria...")
    fireEvent.change(textarea, { target: { value: "Quais as fontes?" } })
    fireEvent.submit(screen.getByText("Enviar").closest("form")!)

    await waitFor(() => {
      expect(screen.getByText(/Fontes consultadas/)).toBeInTheDocument()
    })

    expect(screen.getByText(/Lei 9.250\/95/)).toBeInTheDocument()
  })

  it("does not send empty message", async () => {
    render(<ChatPage />)

    await waitFor(() => {
      expect(screen.getByText("Enviar")).toBeInTheDocument()
    })

    fireEvent.submit(screen.getByText("Enviar").closest("form")!)
    expect(mockPost).not.toHaveBeenCalled()
  })
})
