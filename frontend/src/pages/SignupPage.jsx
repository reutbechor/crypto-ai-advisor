import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout.jsx'
import FormField from '../components/FormField.jsx'
import { ApiError, signupUser } from '../services/authApi.js'

const initialValues = {
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
}

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function SignupPage() {
  const navigate = useNavigate()
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  useEffect(() => {
    if (!isSuccess) {
      return undefined
    }

    const redirectTimer = window.setTimeout(() => navigate('/login'), 1000)
    return () => window.clearTimeout(redirectTimer)
  }, [isSuccess, navigate])

  function handleChange(event) {
    const { name, value } = event.target

    setValues((currentValues) => ({ ...currentValues, [name]: value }))
    setErrors((currentErrors) => ({
      ...currentErrors,
      [name]: undefined,
      ...(name === 'password' ? { confirmPassword: undefined } : {}),
    }))
    setApiError('')
    setIsSuccess(false)
  }

  function validate() {
    const nextErrors = {}

    if (!values.fullName.trim()) {
      nextErrors.fullName = 'Enter your full name.'
    }

    if (!values.email.trim()) {
      nextErrors.email = 'Enter your email address.'
    } else if (!emailPattern.test(values.email.trim())) {
      nextErrors.email = 'Enter a valid email address.'
    }

    if (!values.password) {
      nextErrors.password = 'Create a password.'
    } else if (values.password.length < 8) {
      nextErrors.password = 'Password must be at least 8 characters.'
    }

    if (!values.confirmPassword) {
      nextErrors.confirmPassword = 'Confirm your password.'
    } else if (values.confirmPassword !== values.password) {
      nextErrors.confirmPassword = 'Passwords do not match.'
    }

    return nextErrors
  }

  async function handleSubmit(event) {
    event.preventDefault()

    const nextErrors = validate()
    setErrors(nextErrors)
    setApiError('')
    setIsSuccess(false)

    if (Object.keys(nextErrors).length > 0) {
      return
    }

    setIsSubmitting(true)

    try {
      await signupUser({
        name: values.fullName.trim(),
        email: values.email.trim(),
        password: values.password,
      })
      setIsSuccess(true)
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setApiError('An account with this email already exists.')
      } else {
        setApiError('Unable to create your account. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      titleLines={['Create', 'Profile']}
      description="Set up your profile for insights shaped around you."
      titleId="signup-title"
      formLabel="Profile details"
    >
      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <FormField
          id="fullName"
          label="Full Name"
          value={values.fullName}
          onChange={handleChange}
          error={errors.fullName}
          autoComplete="name"
        />
        <FormField
          id="email"
          label="Email"
          type="email"
          value={values.email}
          onChange={handleChange}
          error={errors.email}
          autoComplete="email"
        />
        <FormField
          id="password"
          label="Password"
          type="password"
          value={values.password}
          onChange={handleChange}
          error={errors.password}
          autoComplete="new-password"
        />
        <FormField
          id="confirmPassword"
          label="Confirm Password"
          type="password"
          value={values.confirmPassword}
          onChange={handleChange}
          error={errors.confirmPassword}
          autoComplete="new-password"
        />

        {isSuccess && (
          <p className="form-success" role="status">
            Profile created successfully. Redirecting to sign in...
          </p>
        )}

        {apiError && (
          <p className="form-api-error" role="alert">
            {apiError}
          </p>
        )}

        <button
          className="button button--primary auth-submit"
          type="submit"
          disabled={isSubmitting || isSuccess}
        >
          {isSubmitting ? 'Creating profile...' : 'Create Profile'}
        </button>
      </form>

      <p className="auth-switch">
        Already have an account? <Link to="/login">Sign In</Link>
      </p>
    </AuthLayout>
  )
}

export default SignupPage
