import "@testing-library/jest-dom/jest-globals"
import { render, screen } from "@testing-library/react"
import Home from "@/app/page"

const mockPush = jest.fn()

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}))

describe("Home Page", () => {
  beforeEach(() => {
    localStorage.clear()
    jest.clearAllMocks()
  })

  it("should redirect to dashboard when token exists", () => {
    localStorage.setItem("access_token", "valid-token")
    render(<Home />)
    expect(mockPush).toHaveBeenCalledWith("/dashboard")
  })

  it("should redirect to login when no token", () => {
    render(<Home />)
    expect(mockPush).toHaveBeenCalledWith("/auth/login")
  })

  it("should show loading message", () => {
    render(<Home />)
    expect(screen.getByText("Carregando...")).toBeInTheDocument()
  })
})
