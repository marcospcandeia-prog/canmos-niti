jest.mock("next/link", () => {
  const React = require("react")
  const MockLink = ({ children, href, ...props }: { children: React.ReactNode; href: string; [key: string]: unknown }) => {
    return React.createElement("a", { href, ...props }, children)
  }
  MockLink.displayName = "MockLink"
  return MockLink
})

jest.mock("next/navigation", () => {
  const mockPush = jest.fn()
  return {
    useRouter: () => ({ push: mockPush, replace: jest.fn(), prefetch: jest.fn(), back: jest.fn(), forward: jest.fn(), refresh: jest.fn() }),
    usePathname: () => "/",
    useSearchParams: () => new URLSearchParams(),
  }
})
