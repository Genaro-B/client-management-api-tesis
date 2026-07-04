import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage.jsx'
import ClientsPage from './pages/ClientsPage.jsx'
import ProductsPage from './pages/ProductsPage.jsx'
import MetricsPage from './pages/MetricsPage.jsx'
import InactiveClientsPage from './pages/InactiveClientsPage.jsx'
import InteractionsPage from './pages/InteractionsPage.jsx'
import ProfilePage from './pages/ProfilePage.jsx'
import { Toaster } from 'sonner'
import useAuth from './hooks/useAuth.js'

function ProtectedRoute({ children }) {
  const { isAuthenticated, initializing } = useAuth()
  if (initializing) return null
  if (!isAuthenticated) return <Navigate to="/" replace />
  return children
}

function PublicRoute({ children }) {
  const { isAuthenticated, initializing } = useAuth()
  if (initializing) return null
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <ClientsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/products"
          element={
            <ProtectedRoute>
              <ProductsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/metrics"
          element={
            <ProtectedRoute>
              <MetricsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/interactions"
          element={
            <ProtectedRoute>
              <InteractionsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/inactive"
          element={
            <ProtectedRoute>
              <InactiveClientsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster richColors closeButton position="top-right" />
    </BrowserRouter>
  )
}
