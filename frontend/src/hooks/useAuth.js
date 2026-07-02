import { useState, useEffect, useCallback } from 'react'
import { login as apiLogin, getStoredUser, saveUser, updateUser } from '../services/authService.js'
import { toast } from 'sonner'

export default function useAuth() {
  const [user, setUser] = useState(null)
  const [initializing, setInitializing] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    setUser(getStoredUser())
    setInitializing(false)
  }, [])

  const login = useCallback(async (email) => {
    setLoading(true)
    setError(null)
    try {
      const userData = await apiLogin(email)
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

  const logout = useCallback(() => {
    sessionStorage.removeItem('crm_user')
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

  return {
    user,
    initializing,
    loading,
    error,
    login,
    logout,
    updateProfile,
    updateAvatar,
    setError,
    isAdmin: user?.role === 'admin',
    isAuthenticated: !!user,
  }
}
