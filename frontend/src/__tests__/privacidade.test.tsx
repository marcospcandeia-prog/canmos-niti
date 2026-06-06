import "@testing-library/jest-dom/jest-globals"
import { render, screen } from "@testing-library/react"
import PrivacidadePage from "@/app/privacidade/page"

describe("Privacidade Page", () => {
  it("should render the privacy policy heading", async () => {
    const page = await PrivacidadePage()
    render(page)
    expect(screen.getByText("Política de Privacidade (LGPD)")).toBeInTheDocument()
  })

  it("should render back link to register", async () => {
    const page = await PrivacidadePage()
    render(page)
    expect(screen.getByText("← Voltar para Registro")).toBeInTheDocument()
  })

  it("should render accept button", async () => {
    const page = await PrivacidadePage()
    render(page)
    expect(screen.getByText("Aceitar e Continuar")).toBeInTheDocument()
  })

  it("should render link to termos", async () => {
    const page = await PrivacidadePage()
    render(page)
    expect(screen.getByText("Ver Termos de Uso")).toBeInTheDocument()
  })

  it("should mention LGPD compliance", async () => {
    const page = await PrivacidadePage()
    render(page)
    expect(screen.getByText(/Conformidade LGPD/)).toBeInTheDocument()
  })

  it("should list user rights under LGPD", async () => {
    const page = await PrivacidadePage()
    render(page)
    expect(screen.getByText("6. Seus Direitos (LGPD Art. 18)")).toBeInTheDocument()
  })
})
