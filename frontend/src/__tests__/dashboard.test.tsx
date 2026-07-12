import "@testing-library/jest-dom/jest-globals"
import { render, screen, waitFor, fireEvent } from "@testing-library/react"
import DashboardPage from "@/app/dashboard/page"

const mockGet = jest.fn()

jest.mock("@/lib/api", () => ({
  get: (...args: unknown[]) => mockGet(...args),
  __esModule: true,
  api: { get: (...args: unknown[]) => mockGet(...args) },
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

beforeEach(() => {
  jest.clearAllMocks()
})

describe("DashboardPage", () => {
  it("shows loading state initially", () => {
    mockGet.mockImplementation(() => new Promise(() => {}))
    render(<DashboardPage />)
    expect(screen.getByText("Carregando...")).toBeInTheDocument()
  })

  it("renders summary cards with data", async () => {
    mockGet.mockResolvedValue({ data: mockSummary })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("R$ 1500.50")).toBeInTheDocument()
    })

    expect(screen.getByText("R$ 3200.00")).toBeInTheDocument()
    expect(screen.getByText("R$ 85000.00")).toBeInTheDocument()
    expect(screen.getByText("8 / 12")).toBeInTheDocument()
  })

  it("renders alerts when present", async () => {
    mockGet.mockResolvedValue({ data: mockSummary })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("Alertas")).toBeInTheDocument()
    })

    expect(screen.getByText("Rendimento incompleto")).toBeInTheDocument()
    expect(screen.getByText("Prazo final: 30/05")).toBeInTheDocument()
  })

  it("hides alerts section when empty", async () => {
    mockGet.mockResolvedValue({ data: { ...mockSummary, alertas: [] } })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("Dashboard")).toBeInTheDocument()
    })

    expect(screen.queryByText("Alertas")).not.toBeInTheDocument()
  })

  it("renders action cards", async () => {
    mockGet.mockResolvedValue({ data: mockSummary })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("Enviar Documentos")).toBeInTheDocument()
    })

    expect(screen.getByText("Declarações IRPF")).toBeInTheDocument()
    expect(screen.getByText("Assistente IA")).toBeInTheDocument()
  })

  it("renders year selector with current year", async () => {
    mockGet.mockResolvedValue({ data: mockSummary })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("Dashboard")).toBeInTheDocument()
    })

    expect(screen.getByRole("combobox")).toBeInTheDocument()
    expect(screen.getByRole("combobox")).toHaveValue(String(new Date().getFullYear()))
  })

  it("changes year and refetches data", async () => {
    mockGet.mockResolvedValue({ data: mockSummary })

    render(<DashboardPage />)

    await waitFor(() => {
      expect(screen.getByText("Dashboard")).toBeInTheDocument()
    })

    const select = screen.getByRole("combobox")
    fireEvent.change(select, { target: { value: "2024" } })

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalledWith("/dashboard/summary?ano_base=2024")
    })
  })
})
