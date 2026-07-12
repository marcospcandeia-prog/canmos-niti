// Auto-applied manual mock for the `zustand` package (Jest picks up mocks
// adjacent to node_modules automatically). It wraps the real `create`/`createStore`
// so that every store created during tests is reset to its initial state after
// each test — Zustand stores are module-level singletons and would otherwise leak
// state (e.g. a store's `initialized` flag) across tests in the same file.
import { act } from "@testing-library/react"

const { create: actualCreate, createStore: actualCreateStore } =
  jest.requireActual("zustand")

export const storeResetFns = new Set<() => void>()

const createUncurried = (stateCreator: unknown) => {
  const store = actualCreate(stateCreator)
  const initialState = store.getState()
  storeResetFns.add(() => {
    store.setState(initialState, true)
  })
  return store
}

// Support both the curried `create()(stateCreator)` and the direct
// `create(stateCreator)` call signatures used by Zustand.
export const create = ((stateCreator: unknown) => {
  return typeof stateCreator === "function"
    ? createUncurried(stateCreator)
    : createUncurried
}) as typeof actualCreate

const createStoreUncurried = (stateCreator: unknown) => {
  const store = actualCreateStore(stateCreator)
  const initialState = store.getState()
  storeResetFns.add(() => {
    store.setState(initialState, true)
  })
  return store
}

export const createStore = ((stateCreator: unknown) => {
  return typeof stateCreator === "function"
    ? createStoreUncurried(stateCreator)
    : createStoreUncurried
}) as typeof actualCreateStore

afterEach(() => {
  act(() => {
    storeResetFns.forEach((resetFn) => resetFn())
  })
})
