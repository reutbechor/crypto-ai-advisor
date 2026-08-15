import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout.jsx'
import FormField from '../components/FormField.jsx'
import useAuth from '../hooks/useAuth.js'
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
  const { login } = useAuth()
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

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
    let accountCreated = false

    try {
      await signupUser({
        name: values.fullName.trim(),
        email: values.email.trim(),
        password: values.password,
      })
      accountCreated = true
      setIsSuccess(true)

      await new Promise((resolve) => window.setTimeout(resolve, 700))

      const authenticatedUser = await login({
        email: values.email.trim(),
        password: values.password,
      })
      const destination = authenticatedUser.onboarding_completed
        ? '/dashboard'
        : '/onboarding'
      navigate(destination, { replace: true })
    } catch (error) {
      if (accountCreated) {
        navigate('/login', { replace: true })
        return
      }

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
            Profile created successfully. Preparing your experience...
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
