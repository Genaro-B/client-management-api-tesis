import '@testing-library/jest-dom'

// jsdom no implementa matchMedia — useTheme lo necesita para detectar
// la preferencia de color del sistema.
window.matchMedia = window.matchMedia || ((query) => ({
  matches: false,
  media: query,
  addEventListener: () => {},
  removeEventListener: () => {},
  addListener: () => {},
  removeListener: () => {},
  dispatchEvent: () => false,
}))

afterEach(() => {
  localStorage.clear()
  sessionStorage.clear()
  document.documentElement.classList.remove('dark')
})