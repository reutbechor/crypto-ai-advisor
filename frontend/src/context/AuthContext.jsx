import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { useNavigate } from 'react-router-dom'
import { getCurrentUser, loginUser } from '../services/authApi.js'
import AuthContext from './auth-context.js'


const TOKEN_STORAGE_KEY = 'coinsight_access_token'

export function AuthProvider({ children }) {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedToken = window.sessionStorage.getItem(TOKEN_STORAGE_KEY)

    if (!storedToken) {
      setLoading(false)
      return undefined
    }

    let isActive = true

    getCurrentUser(storedToken)
      .then((currentUser) => {
        if (isActive) {
          setToken(storedToken)
          setUser(currentUser)
        }
      })
      .catch(() => {
        if (isActive) {
          window.sessionStorage.removeItem(TOKEN_STORAGE_KEY)
        }
      })
      .finally(() => {
        if (isActive) {
          setLoading(false)
        }
      })

    return () => {
      isActive = false
    }
  }, [])

  const login = useCallback(async (credentials) => {
    const result = await loginUser(credentials)

    // Production apps should prefer an HTTP-only secure cookie architecture.
    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, result.access_token)
    setToken(result.access_token)
    setUser(result.user)

    return result.user
  }, [])

  const logout = useCallback(() => {
    window.sessionStorage.removeItem(TOKEN_STORAGE_KEY)
    setToken(null)
    setUser(null)
    navigate('/login', { replace: true })
  }, [navigate])

  const updateUser = useCallback((updatedUser) => {
    setUser(updatedUser)
  }, [])

  const refreshUser = useCallback(async () => {
    if (!token) {
      return null
    }

    const currentUser = await getCurrentUser(token)
    setUser(currentUser)
    return currentUser
  }, [token])

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(user && token),
      loading,
      login,
      logout,
      updateUser,
      refreshUser,
    }),
    [loading, login, logout, refreshUser, token, updateUser, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
