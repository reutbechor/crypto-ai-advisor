import { useState } from 'react'
import { Link } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout.jsx'
import FormField from '../components/FormField.jsx'

const initialValues = {
  email: '',
  password: '',
}

function LoginPage() {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState({})
  const [isSuccess, setIsSuccess] = useState(false)

  function handleChange(event) {
    const { name, value } = event.target

    setValues((currentValues) => ({ ...currentValues, [name]: value }))
    setErrors((currentErrors) => ({ ...currentErrors, [name]: undefined }))
    setIsSuccess(false)
  }

  function validate() {
    const nextErrors = {}

    if (!values.email.trim()) {
      nextErrors.email = 'Enter your email address.'
    }

    if (!values.password) {
      nextErrors.password = 'Enter your password.'
    }

    return nextErrors
  }

  function handleSubmit(event) {
    event.preventDefault()

    const nextErrors = validate()
    setErrors(nextErrors)
    setIsSuccess(Object.keys(nextErrors).length === 0)
  }

  return (
    <AuthLayout
      title="Welcome back"
      description="Sign in to continue to CoinSight AI."
      titleId="login-title"
    >
      <form className="auth-form" onSubmit={handleSubmit} noValidate>
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
          autoComplete="current-password"
        />

        {isSuccess && (
          <p className="form-success" role="status">
            Your details look good. Sign-in will be connected later.
          </p>
        )}

        <button className="button button--primary auth-submit" type="submit">
          Sign In
        </button>
      </form>

      <p className="auth-switch">
        Don&apos;t have an account? <Link to="/signup">Create one</Link>
      </p>
    </AuthLayout>
  )
}

export default LoginPage
