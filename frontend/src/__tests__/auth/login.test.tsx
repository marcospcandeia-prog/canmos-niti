import "@testing-library/jest-dom/jest-globals";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import LoginPage from "@/app/auth/login/page";

const mockPush = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
  useSearchParams: () => new URLSearchParams(),
}));

const mockPost = jest.fn();
jest.mock("@/lib/api", () => ({
  post: (...args: unknown[]) => mockPost(...args),
  __esModule: true,
  default: { post: (...args: unknown[]) => mockPost(...args) },
}));

function submitForm() {
  const form = screen.getByRole("button", { name: "Entrar" }).closest("form")!;
  fireEvent.submit(form);
}

describe("LoginPage", () => {
  beforeEach(() => {
    mockPush.mockClear();
    mockPost.mockClear();
    localStorage.clear();
  });

  it("should render the login form", () => {
    render(<LoginPage />);
    expect(screen.getByText("CANMOS-NITI")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Senha")).toBeInTheDocument();
  });

  it("should submit login form and store tokens", async () => {
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "teste@teste.com" },
    });
    fireEvent.change(screen.getByLabelText("Senha"), {
      target: { value: "senha12345" },
    });

    mockPost.mockResolvedValueOnce({
      data: { access_token: "access-123", refresh_token: "refresh-456" },
    });

    submitForm();

    await waitFor(() => {
      expect(mockPost).toHaveBeenCalledWith("/auth/login", {
        email: "teste@teste.com",
        senha: "senha12345",
      });
    });

    expect(localStorage.getItem("access_token")).toBe("access-123");
    expect(localStorage.getItem("refresh_token")).toBe("refresh-456");
    expect(mockPush).toHaveBeenCalledWith("/dashboard");
  });

  it("should display error on login failure", async () => {
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "teste@teste.com" },
    });
    fireEvent.change(screen.getByLabelText("Senha"), {
      target: { value: "senha_errada" },
    });

    mockPost.mockRejectedValueOnce({
      response: { data: { detail: "Credenciais inválidas" } },
    });

    submitForm();

    await waitFor(() => {
      expect(screen.getByText("Credenciais inválidas")).toBeInTheDocument();
    });
  });

  it("should show loading state during submission", async () => {
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "teste@teste.com" },
    });
    fireEvent.change(screen.getByLabelText("Senha"), {
      target: { value: "senha12345" },
    });

    mockPost.mockImplementationOnce(() => new Promise(() => {}));

    submitForm();

    await waitFor(() => {
      expect(screen.getByText("Entrando...")).toBeInTheDocument();
    });
  });
});
