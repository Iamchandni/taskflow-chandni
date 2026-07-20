// react-router v6 data router calls `new Request(url, {signal})` on every navigation.
// Node.js 16 and jsdom 21 don't expose a global Request, so navigation throws in tests.
// This file is included as a vitest setupFile to provide the minimal polyfill needed.
if (typeof globalThis.Request === 'undefined') {
  ;(globalThis as any).Request = class Request {
    url: string
    method: string
    signal: AbortSignal

    constructor(input: string, init?: { signal?: AbortSignal; method?: string }) {
      this.url = input
      this.method = (init?.method || 'GET').toUpperCase()
      this.signal = init?.signal || new AbortController().signal
    }
  }
}
