import "@testing-library/jest-dom/jest-globals"
import { render, screen, waitFor, fireEvent } from "@testing-library/react"
import DashboardPage from "@/app/dashboard/page"

const mockPush = jest.fn()

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}))

const mockGet = jest.fn()

jest.mock("@/lib/api", () => ({
  get: (...args: unknown[]) => mockGet(...args),
  __esModule: true,
  default: { get: (...args: unknown[]) => mockGet(...args) },
}))

const mockSummary = {
  ano_base: 2025,
  restituicao_estimada: 1500.50,
  imposto_devido: 3200.00,
  total_rendimentos: 85000.00,
  documentos_enviados: 12,
  documentos_processados: 8,
  total_tax_events: 45,
  alertas: [
    { severidade: "warning", mensagem: "Rendimento incompleto" },
    { severidade: "info", mensagem: "Prazo final: 30/05" },
  ],
}

const mockUser = {
  id: "1",
  nome: "João Silva",
  email: "joao@test.com",
}

beforeEach(() => {
  jest.clearAllMocks()
  localStorage.clear()
  mockGet.mockResolvedValue({})
})

afterEach(() => {
  jest.useRealTimers()
})

describe("DashboardPage", () => {
  it("redirects to login when no token", () => {
    render(<DashboardPage />)
    expect(mockPush).toHaveBeenCalledWith("/auth/login")
  })

  it("shows loading state initially", () => {
    localStorage.setItem("access_token", "fake-token")
    mockGet.mockImplementation(() => new Promise(() => {}))
    render(<DashboardPage />)
    expect(screen.getByText("Carregando...")).toBeInTheDocument()
  })

  it("renders summary cards with data", async () => {
    localStorage.setItem("access_token", "fake-token")
    mockGet
      .mockResolvedValueOnce({ data: mockSummary })
      .mockResolvedValueOnce({ data: mockUser })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("CANMOS-NITI")).toBeInTheDocument()
    })

    expect(screen.getByText("R$ 1500.50")).toBeInTheDocument()
    expect(screen.getByText("R$ 3200.00")).toBeInTheDocument()
    expect(screen.getByText("R$ 85000.00")).toBeInTheDocument()
    expect(screen.getByText("8 / 12")).toBeInTheDocument()
    expect(screen.getByText("João Silva")).toBeInTheDocument()
  })

  it("renders alerts when present", async () => {
    localStorage.setItem("access_token", "fake-token")
    mockGet
      .mockResolvedValueOnce({ data: mockSummary })
      .mockResolvedValueOnce({ data: mockUser })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("Alertas")).toBeInTheDocument()
    })

    expect(screen.getByText("Rendimento incompleto")).toBeInTheDocument()
    expect(screen.getByText("Prazo final: 30/05")).toBeInTheDocument()
  })

  it("hides alerts section when empty", async () => {
    localStorage.setItem("access_token", "fake-token")
    mockGet
      .mockResolvedValueOnce({ data: { ...mockSummary, alertas: [] } })
      .mockResolvedValueOnce({ data: mockUser })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("CANMOS-NITI")).toBeInTheDocument()
    })

    expect(screen.queryByText("Alertas")).not.toBeInTheDocument()
  })

  it("renders action cards", async () => {
    localStorage.setItem("access_token", "fake-token")
    mockGet
      .mockResolvedValueOnce({ data: mockSummary })
      .mockResolvedValueOnce({ data: mockUser })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("Enviar Documentos")).toBeInTheDocument()
    })

    expect(screen.getByText("Declarações IRPF")).toBeInTheDocument()
    expect(screen.getByText("Assistente IA")).toBeInTheDocument()
  })

  it("calls logout and redirects", async () => {
    localStorage.setItem("access_token", "fake-token")
    localStorage.setItem("refresh_token", "fake-refresh")
    mockGet
      .mockResolvedValueOnce({ data: mockSummary })
      .mockResolvedValueOnce({ data: mockUser })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("Sair")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Sair"))

    expect(localStorage.getItem("access_token")).toBeNull()
    expect(localStorage.getItem("refresh_token")).toBeNull()
    expect(mockPush).toHaveBeenCalledWith("/auth/login")
  })

  it("renders ano_base from summary", async () => {
    localStorage.setItem("access_token", "fake-token")
    mockGet
      .mockResolvedValueOnce({ data: mockSummary })
      .mockResolvedValueOnce({ data: mockUser })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("Ano base: 2025")).toBeInTheDocument()
    })
  })
})
