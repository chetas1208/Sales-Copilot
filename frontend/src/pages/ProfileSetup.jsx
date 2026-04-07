import { useState, useEffect } from 'react'
import { apiService } from '../services/api'
import { CheckCircleIcon } from '@heroicons/react/24/outline'

const ProfileSetup = ({ user }) => {
  const [profile, setProfile] = useState({
    companyName: '',
    companyWebsite: '',
    industry: '',
    companySize: '',
    yourRole: '',
    productsServices: '',
    valueProposition: '',
    targetMarket: '',
    competitors: '',
  })

  const [isSaving, setIsSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    // Load existing profile
    const loadProfile = async () => {
      try {
        const storedProfile = localStorage.getItem(`profile_${user.id}`)
        if (storedProfile) {
          setProfile(JSON.parse(storedProfile))
        }
      } catch (error) {
        console.error('Error loading profile:', error)
      }
    }
    loadProfile()
  }, [user])

  const handleChange = (e) => {
    const { name, value } = e.target
    setProfile((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSaving(true)

    try {
      // Save to localStorage (and API in future)
      localStorage.setItem(`profile_${user.id}`, JSON.stringify(profile))

      // TODO: Save to backend
      // await apiService.saveProfile({ userId: user.id, ...profile })

      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (error) {
      console.error('Error saving profile:', error)
      alert('Failed to save profile. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="card">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Company Profile
            </h1>
            <p className="text-gray-600">
              Tell us about your company so we can provide better sales insights
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Company Information */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Company Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="companyName" className="label">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    id="companyName"
                    name="companyName"
                    required
                    value={profile.companyName}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="Acme Inc."
                  />
                </div>

                <div>
                  <label htmlFor="companyWebsite" className="label">
                    Company Website *
                  </label>
                  <input
                    type="url"
                    id="companyWebsite"
                    name="companyWebsite"
                    required
                    value={profile.companyWebsite}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="https://acme.com"
                  />
                </div>

                <div>
                  <label htmlFor="industry" className="label">
                    Industry *
                  </label>
                  <input
                    type="text"
                    id="industry"
                    name="industry"
                    required
                    value={profile.industry}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="SaaS, Enterprise Software, etc."
                  />
                </div>

                <div>
                  <label htmlFor="companySize" className="label">
                    Company Size
                  </label>
                  <select
                    id="companySize"
                    name="companySize"
                    value={profile.companySize}
                    onChange={handleChange}
                    className="input-field"
                  >
                    <option value="">Select size</option>
                    <option value="1-10">1-10 employees</option>
                    <option value="11-50">11-50 employees</option>
                    <option value="51-200">51-200 employees</option>
                    <option value="201-500">201-500 employees</option>
                    <option value="500+">500+ employees</option>
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label htmlFor="yourRole" className="label">
                    Your Role *
                  </label>
                  <input
                    type="text"
                    id="yourRole"
                    name="yourRole"
                    required
                    value={profile.yourRole}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="Sales Rep, Account Executive, etc."
                  />
                </div>
              </div>
            </div>

            {/* Product/Service Information */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                What You Offer
              </h2>
              <div className="space-y-6">
                <div>
                  <label htmlFor="productsServices" className="label">
                    Products/Services *
                  </label>
                  <textarea
                    id="productsServices"
                    name="productsServices"
                    required
                    value={profile.productsServices}
                    onChange={handleChange}
                    rows="3"
                    className="input-field"
                    placeholder="Describe your main products or services..."
                  />
                </div>

                <div>
                  <label htmlFor="valueProposition" className="label">
                    Value Proposition *
                  </label>
                  <textarea
                    id="valueProposition"
                    name="valueProposition"
                    required
                    value={profile.valueProposition}
                    onChange={handleChange}
                    rows="3"
                    className="input-field"
                    placeholder="What makes your solution unique? What problems do you solve?"
                  />
                </div>

                <div>
                  <label htmlFor="targetMarket" className="label">
                    Target Market *
                  </label>
                  <textarea
                    id="targetMarket"
                    name="targetMarket"
                    required
                    value={profile.targetMarket}
                    onChange={handleChange}
                    rows="2"
                    className="input-field"
                    placeholder="Who are your ideal customers? (e.g., Enterprise SaaS companies, SMBs in healthcare)"
                  />
                </div>

                <div>
                  <label htmlFor="competitors" className="label">
                    Main Competitors
                  </label>
                  <textarea
                    id="competitors"
                    name="competitors"
                    value={profile.competitors}
                    onChange={handleChange}
                    rows="2"
                    className="input-field"
                    placeholder="List your main competitors (one per line)"
                  />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex items-center justify-between pt-4">
              {saved && (
                <div className="flex items-center text-green-600">
                  <CheckCircleIcon className="h-5 w-5 mr-2" />
                  <span className="text-sm font-medium">Profile saved!</span>
                </div>
              )}
              <button
                type="submit"
                disabled={isSaving}
                className="btn-primary ml-auto"
              >
                {isSaving ? 'Saving...' : 'Save Profile'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ProfileSetup
