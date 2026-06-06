import "@testing-library/jest-dom/jest-globals"
import { render, screen } from "@testing-library/react"
import TermosPage from "@/app/termos/page"

describe("Termos Page", () => {
  it("should render the termos heading", async () => {
    const page = await TermosPage()
    render(page)
    expect(screen.getByText("Termos de Uso - CANMOS-NITI")).toBeInTheDocument()
  })

  it("should render back link to register", async () => {
    const page = await TermosPage()
    render(page)
    expect(screen.getByText("← Voltar para Registro")).toBeInTheDocument()
  })

  it("should render accept button", async () => {
    const page = await TermosPage()
    render(page)
    expect(screen.getByText("Aceitar e Continuar")).toBeInTheDocument()
  })

  it("should render link to privacidade", async () => {
    const page = await TermosPage()
    render(page)
    expect(screen.getByText("Ver Política de Privacidade")).toBeInTheDocument()
  })

  it("should mention important limitation notice", async () => {
    const page = await TermosPage()
    render(page)
    expect(screen.getByText(/não substitui a orientação de um contador/)).toBeInTheDocument()
  })

  it("should list service description", async () => {
    const page = await TermosPage()
    render(page)
    expect(screen.getByText("2. Descrição do Serviço")).toBeInTheDocument()
  })

  it("should mention LGPD and Marco Civil", async () => {
    const page = await TermosPage()
    render(page)
    expect(screen.getByText(/Lei 13.709\/2018/)).toBeInTheDocument()
  })
})
