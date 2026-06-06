import "@testing-library/jest-dom/jest-globals"
import { render, screen, waitFor, fireEvent, within } from "@testing-library/react"
import ProfilePage from "@/app/profile/page"

const mockPush = jest.fn()

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}))

const mockGet = jest.fn()
const mockPut = jest.fn()
const mockPost = jest.fn()
const mockDelete = jest.fn()

jest.mock("@/lib/api", () => ({
  get: (...args: unknown[]) => mockGet(...args),
  put: (...args: unknown[]) => mockPut(...args),
  post: (...args: unknown[]) => mockPost(...args),
  delete: (...args: unknown[]) => mockDelete(...args),
  __esModule: true,
  default: {
    get: (...args: unknown[]) => mockGet(...args),
    put: (...args: unknown[]) => mockPut(...args),
    post: (...args: unknown[]) => mockPost(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
  },
}))

const mockProfile = {
  id: "1",
  email: "joao@test.com",
  cpf: "52998224725",
  nome: "João Silva",
  telefone: "11999999999",
  endereco: "Rua A, 123",
  cidade: "São Paulo",
  estado: "SP",
  cep: "01001000",
  data_nascimento: "1990-01-01",
  status: "active",
  created_at: "2026-01-15T10:00:00Z",
  updated_at: "2026-06-03T22:00:00Z",
}

const mockStats = {
  total_documents: 10,
  documents_processed: 7,
  total_tax_events: 35,
  declarations_count: 3,
  last_activity: "2026-06-03T20:00:00Z",
}

beforeEach(() => {
  jest.clearAllMocks()
  mockGet.mockResolvedValue({})
  mockPut.mockResolvedValue({})
  mockPost.mockResolvedValue({})
  mockDelete.mockResolvedValue({})
})

describe("ProfilePage", () => {
  it("shows loading state initially", () => {
    mockGet.mockImplementation(() => new Promise(() => {}))
    render(<ProfilePage />)
    expect(screen.getByText("Carregando perfil...")).toBeInTheDocument()
  })

  it("renders profile data after loading", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockProfile })
      .mockResolvedValueOnce({ data: mockStats })

    render(<ProfilePage />)

    await waitFor(() => {
      expect(screen.getByText("Meu Perfil")).toBeInTheDocument()
    })

    expect(screen.getByDisplayValue("João Silva")).toBeInTheDocument()
    expect(screen.getByText("joao@test.com")).toBeInTheDocument()
    expect(screen.getByText("529.982.247-25")).toBeInTheDocument()
    expect(screen.getByText("Ativa")).toBeInTheDocument()
  })

  it("renders stats cards", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockProfile })
      .mockResolvedValueOnce({ data: mockStats })

    render(<ProfilePage />)

    await waitFor(() => {
      expect(screen.getByText("Documentos Enviados")).toBeInTheDocument()
    })

    expect(screen.getByText("10")).toBeInTheDocument()
    expect(screen.getByText("Declarações Criadas")).toBeInTheDocument()
    expect(screen.getByText("3")).toBeInTheDocument()
  })

  it("switches tabs", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockProfile })
      .mockResolvedValueOnce({ data: mockStats })

    render(<ProfilePage />)

    await waitFor(() => {
      expect(screen.getByText("Informações Pessoais")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Segurança"))

    expect(screen.getByRole("heading", { name: "Alterar Senha" })).toBeInTheDocument()
    expect(document.querySelector('input[type="password"]')).toBeInTheDocument()

    fireEvent.click(screen.getByText("Privacidade & Dados"))

    expect(screen.getByText("Seus Direitos (LGPD)")).toBeInTheDocument()
    expect(screen.getByText("Excluir Minha Conta")).toBeInTheDocument()
  })

  it("enters edit mode and cancels", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockProfile })
      .mockResolvedValueOnce({ data: mockStats })

    render(<ProfilePage />)

    await waitFor(() => {
      expect(screen.getByText("Editar Perfil")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Editar Perfil"))

    expect(screen.getByText("Salvar Alterações")).toBeInTheDocument()
    expect(screen.getByText("Cancelar")).toBeInTheDocument()

    fireEvent.click(screen.getByText("Cancelar"))

    await waitFor(() => {
      expect(screen.getByText("Editar Perfil")).toBeInTheDocument()
    })
  })

  it("saves profile changes", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockProfile })
      .mockResolvedValueOnce({ data: mockStats })

    render(<ProfilePage />)

    await waitFor(() => {
      expect(screen.getByText("Editar Perfil")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Editar Perfil"))

    const nomeInput = screen.getByDisplayValue("João Silva")
    fireEvent.change(nomeInput, { target: { value: "João Souza" } })

    fireEvent.click(screen.getByText("Salvar Alterações"))

    await waitFor(() => {
      expect(mockPut).toHaveBeenCalledWith("/users/me", expect.objectContaining({ nome: "João Souza" }))
    })
  })

  it("shows success after profile save", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockProfile })
      .mockResolvedValueOnce({ data: mockStats })
      .mockResolvedValue({ data: mockProfile })

    render(<ProfilePage />)

    await waitFor(() => {
      expect(screen.getByText("Editar Perfil")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Editar Perfil"))
    fireEvent.click(screen.getByText("Salvar Alterações"))

    await waitFor(() => {
      expect(screen.getByText("Perfil atualizado com sucesso!")).toBeInTheDocument()
    })
  })

  function fillPasswordForm(
    values: { senha_atual?: string; nova_senha?: string; confirmar_senha?: string }
  ) {
    const inputs = document.querySelectorAll<HTMLInputElement>('input[type="password"]')
    if (values.senha_atual) fireEvent.change(inputs[0], { target: { value: values.senha_atual } })
    if (values.nova_senha) fireEvent.change(inputs[1], { target: { value: values.nova_senha } })
    if (values.confirmar_senha) fireEvent.change(inputs[2], { target: { value: values.confirmar_senha } })
  }

  function getPasswordForm(): HTMLFormElement {
    return document.querySelector('form')!
  }

  it("validates password mismatch", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockProfile })
      .mockResolvedValueOnce({ data: mockStats })

    render(<ProfilePage />)

    await waitFor(() => {
      expect(screen.getByText("Informações Pessoais")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Segurança"))

    fillPasswordForm({ senha_atual: "old123", nova_senha: "new12345", confirmar_senha: "different" })
    fireEvent.submit(getPasswordForm())

    await waitFor(() => {
      expect(screen.getByText("As senhas não coincidem")).toBeInTheDocument()
    })
  })

  it("validates minimum password length", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockProfile })
      .mockResolvedValueOnce({ data: mockStats })

    render(<ProfilePage />)

    await waitFor(() => {
      expect(screen.getByText("Informações Pessoais")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Segurança"))

    fillPasswordForm({ senha_atual: "old123", nova_senha: "short", confirmar_senha: "short" })
    fireEvent.submit(getPasswordForm())

    await waitFor(() => {
      expect(screen.getByText("A nova senha deve ter no mínimo 8 caracteres")).toBeInTheDocument()
    })
  })

  it("changes password successfully", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockProfile })
      .mockResolvedValueOnce({ data: mockStats })

    render(<ProfilePage />)

    await waitFor(() => {
      expect(screen.getByText("Informações Pessoais")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Segurança"))

    fillPasswordForm({ senha_atual: "old12345", nova_senha: "new12345", confirmar_senha: "new12345" })
    fireEvent.submit(getPasswordForm())

    await waitFor(() => {
      expect(screen.getByText("Senha alterada com sucesso!")).toBeInTheDocument()
    })
  })

  it("shows delete confirmation and cancels", async () => {
    mockGet
      .mockResolvedValueOnce({ data: mockProfile })
      .mockResolvedValueOnce({ data: mockStats })

    render(<ProfilePage />)

    await waitFor(() => {
      expect(screen.getByText("Informações Pessoais")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Privacidade & Dados"))

    await waitFor(() => {
      expect(screen.getByText("Excluir Minha Conta")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Excluir Minha Conta"))

    expect(screen.getByText("Confirmar Exclusão de Conta")).toBeInTheDocument()

    fireEvent.click(screen.getByText("Cancelar"))

    await waitFor(() => {
      expect(screen.getByText("Excluir Minha Conta")).toBeInTheDocument()
    })
  })
})
