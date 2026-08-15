import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader.jsx'
import SelectableOption from '../components/SelectableOption.jsx'
import useAuth from '../hooks/useAuth.js'
import { ApiError } from '../services/apiClient.js'
import { completeOnboarding } from '../services/onboardingApi.js'


const cryptoOptions = [
  { value: 'bitcoin', label: 'Bitcoin', meta: 'BTC' },
  { value: 'ethereum', label: 'Ethereum', meta: 'ETH' },
  { value: 'solana', label: 'Solana', meta: 'SOL' },
  { value: 'cardano', label: 'Cardano', meta: 'ADA' },
  { value: 'ripple', label: 'XRP', meta: 'XRP' },
]

const investorOptions = [
  {
    value: 'hodler',
    label: 'HODLer',
    description: 'Focused on long-term holding.',
    meta: '01',
  },
  {
    value: 'day_trader',
    label: 'Day Trader',
    description: 'Interested in shorter-term market moves.',
    meta: '02',
  },
  {
    value: 'nft_collector',
    label: 'NFT Collector',
    description: 'Interested in digital collectibles and Web3 assets.',
    meta: '03',
  },
]

const contentOptions = [
  { value: 'market_news', label: 'Market News', meta: 'NEWS' },
  { value: 'coin_prices', label: 'Coin Prices', meta: 'DATA' },
  { value: 'ai_insights', label: 'AI Insights', meta: 'AI' },
  { value: 'fun', label: 'Fun', meta: 'FUN' },
]

const stepContent = [
  {
    title: 'What are you interested in?',
    description: 'Choose the crypto assets you want to follow.',
  },
  {
    title: 'How do you invest?',
    description: 'Choose the option that best describes your style.',
  },
  {
    title: 'What would you like to see?',
    description: 'Choose the content that matters most to you.',
  },
]

function OnboardingPage() {
  const navigate = useNavigate()
  const { logout, refreshUser, token, updateUser } = useAuth()
  const [step, setStep] = useState(1)
  const [cryptoAssets, setCryptoAssets] = useState([])
  const [investorType, setInvestorType] = useState('')
  const [contentPreferences, setContentPreferences] = useState([])
  const [validationError, setValidationError] = useState('')
  const [apiError, setApiError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  function toggleMultipleSelection(value, setter) {
    setter((currentValues) =>
      currentValues.includes(value)
        ? currentValues.filter((currentValue) => currentValue !== value)
        : [...currentValues, value],
    )
    setValidationError('')
    setApiError('')
  }

  function continueToNextStep() {
    if (step === 1 && cryptoAssets.length === 0) {
      setValidationError('Choose at least one crypto asset to continue.')
      return
    }

    if (step === 2 && !investorType) {
      setValidationError('Choose the investor type that best describes you.')
      return
    }

    setValidationError('')
    setApiError('')
    setStep((currentStep) => currentStep + 1)
  }

  function goBack() {
    setValidationError('')
    setApiError('')
    setStep((currentStep) => currentStep - 1)
  }

  async function handleSubmit(event) {
    event.preventDefault()

    if (contentPreferences.length === 0) {
      setValidationError('Choose at least one content type to finish setup.')
      return
    }

    setValidationError('')
    setApiError('')
    setIsSubmitting(true)

    try {
      const result = await completeOnboarding(
        {
          crypto_assets: cryptoAssets,
          investor_type: investorType,
          content_preferences: contentPreferences,
        },
        token,
      )
      updateUser(result.user)
      navigate('/dashboard', { replace: true })
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        logout()
        return
      }

      if (error instanceof ApiError && error.status === 409) {
        setApiError('Your onboarding has already been completed.')

        try {
          const currentUser = await refreshUser()
          if (currentUser?.onboarding_completed) {
            navigate('/dashboard', { replace: true })
          }
        } catch {
          logout()
        }
        return
      }

      setApiError('Unable to save your preferences. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const currentContent = stepContent[step - 1]

  return (
    <main className="onboarding-page">
      <div className="onboarding-shell">
        <PageHeader />

        <div className="onboarding-layout">
          <aside className="onboarding-intro">
            <div>
              <p className="eyebrow">Personalization</p>
              <h1>Built around you.</h1>
              <p>
                Three quick choices help CoinSight shape your crypto experience.
              </p>
            </div>
            <button className="onboarding-logout" type="button" onClick={logout}>
              Logout
            </button>
          </aside>

          <section className="onboarding-form-area" aria-labelledby="onboarding-title">
            <form className="onboarding-card" onSubmit={handleSubmit} noValidate>
              <div className="onboarding-progress">
                <span>Step {step} of 3</span>
                <div className="progress-bars" aria-hidden="true">
                  {[1, 2, 3].map((progressStep) => (
                    <span
                      className={progressStep <= step ? 'progress-bar--active' : ''}
                      key={progressStep}
                    />
                  ))}
                </div>
              </div>

              <header className="onboarding-question">
                <h2 id="onboarding-title">{currentContent.title}</h2>
                <p>{currentContent.description}</p>
              </header>

              {step === 1 && (
                <div className="selection-grid selection-grid--assets">
                  {cryptoOptions.map((option) => (
                    <SelectableOption
                      key={option.value}
                      {...option}
                      selected={cryptoAssets.includes(option.value)}
                      onSelect={() => toggleMultipleSelection(option.value, setCryptoAssets)}
                    />
                  ))}
                </div>
              )}

              {step === 2 && (
                <div className="selection-grid selection-grid--investor">
                  {investorOptions.map((option) => (
                    <SelectableOption
                      key={option.value}
                      {...option}
                      selected={investorType === option.value}
                      onSelect={() => {
                        setInvestorType(option.value)
                        setValidationError('')
                        setApiError('')
                      }}
                    />
                  ))}
                </div>
              )}

              {step === 3 && (
                <div className="selection-grid selection-grid--content">
                  {contentOptions.map((option) => (
                    <SelectableOption
                      key={option.value}
                      {...option}
                      selected={contentPreferences.includes(option.value)}
                      onSelect={() =>
                        toggleMultipleSelection(option.value, setContentPreferences)
                      }
                    />
                  ))}
                </div>
              )}

              <div className="onboarding-feedback" aria-live="polite">
                {validationError && (
                  <p className="field-error" role="alert">
                    {validationError}
                  </p>
                )}
                {apiError && (
                  <p className="form-api-error" role="alert">
                    {apiError}
                  </p>
                )}
              </div>

              <div className="onboarding-actions">
                {step > 1 && (
                  <button
                    className="button button--secondary"
                    type="button"
                    disabled={isSubmitting}
                    onClick={goBack}
                  >
                    Back
                  </button>
                )}

                {step < 3 ? (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={continueToNextStep}
                  >
                    Continue
                  </button>
                ) : (
                  <button
                    className="button button--primary"
                    type="submit"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? 'Saving preferences...' : 'Finish Setup'}
                  </button>
                )}
              </div>
            </form>
          </section>
        </div>
      </div>
    </main>
  )
}

export default OnboardingPage
