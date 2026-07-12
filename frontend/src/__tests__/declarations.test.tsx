import "@testing-library/jest-dom/jest-globals"
import { render, screen, waitFor, fireEvent } from "@testing-library/react"
import DeclarationsPage from "@/app/declarations/page"

const mockGet = jest.fn()
const mockPost = jest.fn()

jest.mock("@/lib/api", () => ({
  get: (...args: unknown[]) => mockGet(...args),
  post: (...args: unknown[]) => mockPost(...args),
  __esModule: true,
  api: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
  },
  default: {
    get: (...args: unknown[]) => mockGet(...args),
    post: (...args: unknown[]) => mockPost(...args),
  },
}))

const mockDeclarations = [
  {
    id: 1,
    ano_base: 2025,
    status: "draft",
    restituicao_estimada: 500.00,
    imposto_devido: 0,
    created_at: "2026-06-03T22:00:00Z",
    updated_at: "2026-06-03T22:00:00Z",
  },
  {
    id: 2,
    ano_base: 2025,
    status: "submitted",
    restituicao_estimada: 0,
    imposto_devido: 1200.00,
    created_at: "2026-06-01T10:00:00Z",
    updated_at: "2026-06-01T10:00:00Z",
  },
]

beforeEach(() => {
  jest.clearAllMocks()
  mockGet.mockResolvedValue({ data: [] })
  mockPost.mockResolvedValue({})
})

describe("DeclarationsPage", () => {
  it("shows loading state initially", () => {
    mockGet.mockImplementation(() => new Promise(() => {}))
    render(<DeclarationsPage />)
    expect(screen.getByText("Carregando declarações...")).toBeInTheDocument()
  })

  it("renders info card", async () => {
    render(<DeclarationsPage />)

    await waitFor(() => {
      expect(screen.getByText("Como funciona")).toBeInTheDocument()
    })

    expect(screen.getByText(/Envie seus documentos fiscais/)).toBeInTheDocument()
  })

  it("shows empty state when no declarations", async () => {
    render(<DeclarationsPage />)

    await waitFor(() => {
      expect(screen.getByText("Nenhuma declaração encontrada")).toBeInTheDocument()
    })

    expect(screen.getByText("Criar Primeira Declaração")).toBeInTheDocument()
  })

  it("renders declarations list", async () => {
    mockGet.mockResolvedValue({ data: mockDeclarations })

    render(<DeclarationsPage />)

    await waitFor(() => {
      expect(screen.getByText("Rascunho")).toBeInTheDocument()
    })

    expect(screen.getByText("Enviada")).toBeInTheDocument()
    expect(screen.getByText("Restituir R$ 500,00")).toBeInTheDocument()
    expect(screen.getByText("Pagar R$ 1.200,00")).toBeInTheDocument()
  })

  it("calls api.get on mount", async () => {
    render(<DeclarationsPage />)

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith("/tax/declarations")
    })
  })

  it("creates a new declaration", async () => {
    mockGet.mockResolvedValue({ data: [] })
    mockPost.mockResolvedValue({ data: { id: 1, ano_base: 2025, status: "draft" } })

    render(<DeclarationsPage />)

    await waitFor(() => {
      expect(screen.getByText("Criar Primeira Declaração")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Criar Primeira Declaração"))

    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledWith("/tax/declaration/2025")
    })
  })

  it("shows creating state on button", async () => {
    mockGet.mockResolvedValue({ data: [] })
    mockPost.mockImplementation(() => new Promise(() => {}))

    render(<DeclarationsPage />)

    await waitFor(() => {
      expect(screen.getByText("Criar Primeira Declaração")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Criar Primeira Declaração"))

    await waitFor(() => {
      const creatingButtons = screen.getAllByText("Criando...")
      expect(creatingButtons.length).toBeGreaterThanOrEqual(1)
    })
  })

  it("calculates taxes", async () => {
    mockGet.mockResolvedValue({ data: mockDeclarations })
    mockPost.mockResolvedValue({
      data: {
        restituicao_estimada: 800.00,
        imposto_devido: 0,
        total_rendimentos: 90000.00,
        total_deducoes: 15000.00,
        base_calculo: 75000.00,
        total_retencao: 10000.00,
        imposto_pagar: 0,
      },
    })

    render(<DeclarationsPage />)

    await waitFor(() => {
      expect(screen.getByText("Calcular Impostos")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Calcular Impostos"))

    await waitFor(() => {
      expect(screen.getByText("Rendimentos Tributáveis")).toBeInTheDocument()
    })

    expect(screen.getByText("R$ 90.000,00")).toBeInTheDocument()
    expect(screen.getByText("R$ 15.000,00")).toBeInTheDocument()
    expect(screen.getByText("R$ 75.000,00")).toBeInTheDocument()
  })

  it("changes year via select", async () => {
    render(<DeclarationsPage />)

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toBeInTheDocument()
    })

    const select = screen.getByRole("combobox") as HTMLSelectElement
    expect(select.value).toBe("2025")

    fireEvent.change(select, { target: { value: "2024" } })

    expect(select.value).toBe("2024")
  })

})
