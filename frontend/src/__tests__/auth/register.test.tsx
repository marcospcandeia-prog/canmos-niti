import "@testing-library/jest-dom/jest-globals";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import RegisterPage from "@/app/auth/register/page";

const mockPush = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

const mockPost = jest.fn();
jest.mock("@/lib/api", () => ({
  post: (...args: unknown[]) => mockPost(...args),
  __esModule: true,
  default: { post: (...args: unknown[]) => mockPost(...args) },
}));

function submitForm() {
  const form = screen.getByRole("button", { name: "Criar Conta" }).closest("form")!;
  fireEvent.submit(form);
}

describe("RegisterPage", () => {
  beforeEach(() => {
    mockPush.mockClear();
    mockPost.mockClear();
  });

  it("should render the registration form", () => {
    render(<RegisterPage />);
    expect(screen.getByRole("heading", { name: "Criar Conta" })).toBeInTheDocument();
    expect(screen.getByLabelText("Nome Completo *")).toBeInTheDocument();
    expect(screen.getByLabelText("Email *")).toBeInTheDocument();
    expect(screen.getByLabelText("CPF *")).toBeInTheDocument();
    expect(screen.getByLabelText("Senha *")).toBeInTheDocument();
    expect(screen.getByLabelText("Confirmar Senha *")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Criar Conta" })).toBeInTheDocument();
  });

  it("should show validation errors for empty form", async () => {
    render(<RegisterPage />);
    submitForm();

    await waitFor(() => {
      expect(screen.getByText("Nome completo é obrigatório")).toBeInTheDocument();
      expect(screen.getByText("Email é obrigatório")).toBeInTheDocument();
      expect(screen.getByText("CPF é obrigatório")).toBeInTheDocument();
      expect(screen.getByText("Senha é obrigatória")).toBeInTheDocument();
      expect(screen.getByText("Confirmação de senha é obrigatória")).toBeInTheDocument();
    });
  });

  it("should validate single name", async () => {
    render(<RegisterPage />);
    fireEvent.change(screen.getByLabelText("Nome Completo *"), {
      target: { value: "Joao" },
    });
    submitForm();

    await waitFor(() => {
      expect(screen.getByText("Digite seu nome completo")).toBeInTheDocument();
    });
  });

  it("should validate invalid email", async () => {
    render(<RegisterPage />);
    fireEvent.change(screen.getByLabelText("Email *"), {
      target: { value: "invalido" },
    });
    submitForm();

    await waitFor(() => {
      expect(screen.getByText("Email inválido")).toBeInTheDocument();
    });
  });

  it("should validate CPF with all same digits", async () => {
    render(<RegisterPage />);
    const cpfInput = screen.getByLabelText("CPF *");
    fireEvent.change(cpfInput, { target: { value: "11111111111" } });
    submitForm();

    await waitFor(() => {
      expect(screen.getByText("CPF inválido")).toBeInTheDocument();
    });
  });

  it("should reject CPF with invalid check digits", async () => {
    render(<RegisterPage />);
    const cpfInput = screen.getByLabelText("CPF *");
    fireEvent.change(cpfInput, { target: { value: "12345678901" } });
    submitForm();

    await waitFor(() => {
      expect(screen.getByText("CPF inválido")).toBeInTheDocument();
    });
  });

  it("should accept a valid CPF and submit", async () => {
    render(<RegisterPage />);
    fireEvent.change(screen.getByLabelText("Nome Completo *"), {
      target: { value: "João Silva" },
    });
    fireEvent.change(screen.getByLabelText("Email *"), {
      target: { value: "joao@teste.com" },
    });
    fireEvent.change(screen.getByLabelText("CPF *"), {
      target: { value: "52998224725" },
    });
    fireEvent.change(screen.getByLabelText("Senha *"), {
      target: { value: "senha12345" },
    });
    fireEvent.change(screen.getByLabelText("Confirmar Senha *"), {
      target: { value: "senha12345" },
    });
    fireEvent.click(screen.getByLabelText(/Aceito os/));

    mockPost.mockResolvedValueOnce({ data: { id: 1 } });

    submitForm();

    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledWith("/auth/register", {
        nome: "João Silva",
        email: "joao@teste.com",
        cpf: "52998224725",
        senha: "senha12345",
        lgpd_consent: true,
      });
    });
  });

  it("should validate password mismatch", async () => {
    render(<RegisterPage />);
    fireEvent.change(screen.getByLabelText("Senha *"), {
      target: { value: "senha12345" },
    });
    fireEvent.change(screen.getByLabelText("Confirmar Senha *"), {
      target: { value: "senha54321" },
    });
    submitForm();

    await waitFor(() => {
      expect(screen.getByText("As senhas não coincidem")).toBeInTheDocument();
    });
  });

  it("should require terms acceptance", async () => {
    render(<RegisterPage />);
    fireEvent.change(screen.getByLabelText("Nome Completo *"), {
      target: { value: "João Silva" },
    });
    fireEvent.change(screen.getByLabelText("Email *"), {
      target: { value: "joao@teste.com" },
    });
    fireEvent.change(screen.getByLabelText("CPF *"), {
      target: { value: "52998224725" },
    });
    fireEvent.change(screen.getByLabelText("Senha *"), {
      target: { value: "senha12345" },
    });
    fireEvent.change(screen.getByLabelText("Confirmar Senha *"), {
      target: { value: "senha12345" },
    });
    submitForm();

    await waitFor(() => {
      expect(
        screen.getByText("Você deve aceitar os termos para continuar")
      ).toBeInTheDocument();
    });
  });

  it("should display API error on submission failure", async () => {
    render(<RegisterPage />);
    fireEvent.change(screen.getByLabelText("Nome Completo *"), {
      target: { value: "João Silva" },
    });
    fireEvent.change(screen.getByLabelText("Email *"), {
      target: { value: "joao@teste.com" },
    });
    fireEvent.change(screen.getByLabelText("CPF *"), {
      target: { value: "52998224725" },
    });
    fireEvent.change(screen.getByLabelText("Senha *"), {
      target: { value: "senha12345" },
    });
    fireEvent.change(screen.getByLabelText("Confirmar Senha *"), {
      target: { value: "senha12345" },
    });
    fireEvent.click(screen.getByLabelText(/Aceito os/));

    mockPost.mockRejectedValueOnce({
      response: { data: { detail: "Email já cadastrado" } },
    });

    submitForm();

    await waitFor(() => {
      expect(screen.getByText("Email já cadastrado")).toBeInTheDocument();
    });
  });

  it("should show success message and redirect after registration", async () => {
    jest.useFakeTimers();
    render(<RegisterPage />);

    fireEvent.change(screen.getByLabelText("Nome Completo *"), {
      target: { value: "João Silva" },
    });
    fireEvent.change(screen.getByLabelText("Email *"), {
      target: { value: "joao@teste.com" },
    });
    fireEvent.change(screen.getByLabelText("CPF *"), {
      target: { value: "52998224725" },
    });
    fireEvent.change(screen.getByLabelText("Senha *"), {
      target: { value: "senha12345" },
    });
    fireEvent.change(screen.getByLabelText("Confirmar Senha *"), {
      target: { value: "senha12345" },
    });
    fireEvent.click(screen.getByLabelText(/Aceito os/));

    mockPost.mockResolvedValueOnce({ data: { id: 1 } });

    submitForm();

    await waitFor(() => {
      expect(
        screen.getByText("Conta criada com sucesso! Redirecionando para login...")
      ).toBeInTheDocument();
    });

    jest.advanceTimersByTime(2000);
    expect(mockPush).toHaveBeenCalledWith("/auth/login?registered=true");
    jest.useRealTimers();
  });
});
