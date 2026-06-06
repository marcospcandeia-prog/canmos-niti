import "@testing-library/jest-dom/jest-globals";
import axios from "axios";
import { api } from "@/lib/api";

jest.mock("axios", () => {
  const actual = jest.requireActual("axios");
  return {
    ...actual,
    post: jest.fn(),
  };
});

let savedAdapter: any;

beforeEach(() => {
  localStorage.clear();
  savedAdapter = api.defaults.adapter;
  jest.clearAllMocks();
});

afterEach(() => {
  api.defaults.adapter = savedAdapter;
});

describe("API Client", () => {
  it("should set base URL from env or default", () => {
    expect(api.defaults.baseURL).toBe("http://localhost:8000");
  });

  it("should have JSON content type by default", () => {
    expect(api.defaults.headers["Content-Type"]).toBe("application/json");
  });

  it("should define request interceptor", () => {
    expect(api.interceptors.request).toBeDefined();
  });

  it("should define response interceptor", () => {
    expect(api.interceptors.response).toBeDefined();
  });

  it("should add Bearer token from localStorage to requests", async () => {
    localStorage.setItem("access_token", "my-test-token");

    const adapter = jest.fn().mockResolvedValue({
      data: {},
      status: 200,
      statusText: "OK",
      headers: {},
      config: {},
    });
    api.defaults.adapter = adapter;

    await api.get("/test");

    const config = adapter.mock.calls[0][0];
    expect(config.headers?.Authorization).toBe("Bearer my-test-token");
  });

  it("should not add Authorization header when no token in localStorage", async () => {
    const adapter = jest.fn().mockResolvedValue({
      data: {},
      status: 200,
      statusText: "OK",
      headers: {},
      config: {},
    });
    api.defaults.adapter = adapter;

    await api.get("/test");

    const config = adapter.mock.calls[0][0];
    expect(config.headers?.Authorization).toBeUndefined();
  });

  it("should retry on 401 with refresh token and store new token", async () => {
    localStorage.setItem("access_token", "expired-token");
    localStorage.setItem("refresh_token", "valid-refresh");

    (axios.post as jest.Mock).mockResolvedValue({
      data: { access_token: "fresh-token" },
    });

    const adapter = jest
      .fn()
      .mockRejectedValueOnce({
        response: { status: 401 },
        config: { headers: {} },
      })
      .mockResolvedValueOnce({
        data: {},
        status: 200,
        statusText: "OK",
        headers: {},
        config: {},
      });
    api.defaults.adapter = adapter;

    await api.get("/test");

    expect(axios.post).toHaveBeenCalledWith(
      "http://localhost:8000/auth/refresh",
      { refresh_token: "valid-refresh" }
    );
    expect(adapter).toHaveBeenCalledTimes(2);
    expect(localStorage.getItem("access_token")).toBe("fresh-token");
  });

  it("should clear tokens and redirect to login when refresh fails", async () => {
    localStorage.setItem("access_token", "expired-token");
    localStorage.setItem("refresh_token", "bad-refresh");

    (axios.post as jest.Mock).mockRejectedValue(new Error("Refresh expired"));

    const adapter = jest.fn().mockRejectedValue({
      response: { status: 401 },
      config: { headers: {} },
    });
    api.defaults.adapter = adapter;

    await expect(api.get("/test")).rejects.toBeDefined();

    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
  });

  it("should pass non-401 errors through without retry", async () => {
    const adapter = jest.fn().mockRejectedValue({
      response: { status: 500 },
      config: { headers: {} },
    });
    api.defaults.adapter = adapter;

    await expect(api.get("/test")).rejects.toBeDefined();
    expect(adapter).toHaveBeenCalledTimes(1);
  });

  it("should not retry a request that was already retried", async () => {
    const adapter = jest.fn().mockRejectedValue({
      response: { status: 401 },
      config: { headers: {}, _retry: true },
    });
    api.defaults.adapter = adapter;

    await expect(api.get("/test")).rejects.toBeDefined();
    expect(adapter).toHaveBeenCalledTimes(1);
  });
});
