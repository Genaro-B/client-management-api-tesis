import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { login as apiLogin, changePassword as apiChangePassword, getStoredUser, saveUser, updateUser } from '../services/authService.js'
import { toast } from 'sonner'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [initializing, setInitializing] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    setUser(getStoredUser())
    setInitializing(false)
  }, [])

  const login = useCallback(async (email, password) => {
    setLoading(true)
    setError(null)
    try {
      const userData = await apiLogin(email, password)
      saveUser(userData)
      setUser(userData)
      toast.success(`Bienvenido, ${userData.nombre}`)
      return userData
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const changePassword = useCallback(async (currentPassword, newPassword) => {
    const result = await apiChangePassword(currentPassword, newPassword)
    // Limpiar el flag en el usuario en memoria y persistir el cambio
    setUser((prev) => {
      const updated = { ...prev, password_change_required: false }
      saveUser(updated)
      return updated
    })
    toast.success('Contraseña actualizada correctamente')
    return result
  }, [])

  const logout = useCallback(() => {
    sessionStorage.removeItem('crm_user')
    sessionStorage.removeItem('crm_token')
    setUser(null)
    toast.success('Sesión cerrada correctamente')
  }, [])

  const updateProfile = useCallback((data) => {
    const updated = updateUser(data)
    if (updated) {
      setUser(updated)
      toast.success('Perfil actualizado correctamente')
    }
    return updated
  }, [])

  const updateAvatar = useCallback((base64) => {
    const updated = updateUser({ avatar: base64 })
    if (updated) {
      setUser(updated)
      toast.success('Foto de perfil actualizada')
    }
    return updated
  }, [])

  const value = {
    user,
    initializing,
    loading,
    error,
    login,
    logout,
    changePassword,
    updateProfile,
    updateAvatar,
    setError,
    isAdmin: user?.role === 'admin',
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  return ctx
}