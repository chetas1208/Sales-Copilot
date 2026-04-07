import { useState } from 'react'
import { apiService } from '../services/api'
import {
  MagnifyingGlassIcon,
  SparklesIcon,
  UserIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline'

const MeetingPrep = ({ user }) => {
  const [meetingData, setMeetingData] = useState({
    prospectName: '',
    prospectEmail: '',
    prospectLinkedIn: '',
    prospectRole: '',
    companyName: '',
    companyWebsite: '',
    companyLinkedIn: '',
    meetingDate: '',
    meetingGoal: '',
    additionalNotes: '',
  })

  const [isResearching, setIsResearching] = useState(false)
  const [insights, setInsights] = useState(null)
  const [linkedinData, setLinkedinData] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setMeetingData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const fetchLinkedInProfile = async (linkedinUrl) => {
    try {
      // TODO: Integrate Apify LinkedIn scraper
      // const response = await apiService.fetchLinkedInProfile(linkedinUrl)
      // return response.data

      // Simulated LinkedIn data
      return {
        name: meetingData.prospectName,
        headline: 'VP of Sales at Tech Company',
        location: 'San Francisco, CA',
        summary: 'Experienced sales leader with 10+ years in SaaS...',
        experience: [
          { title: 'VP of Sales', company: 'Current Company', duration: '2 years' }
        ],
        education: [
          { school: 'Stanford University', degree: 'MBA' }
        ]
      }
    } catch (error) {
      console.error('Error fetching LinkedIn:', error)
      return null
    }
  }

  const handleResearch = async () => {
    if (!meetingData.companyWebsite) {
      alert('Please enter company website to start research')
      return
    }

    setIsResearching(true)

    try {
      // Fetch LinkedIn data if URL provided
      if (meetingData.prospectLinkedIn) {
        const profileData = await fetchLinkedInProfile(meetingData.prospectLinkedIn)
        setLinkedinData(profileData)
      }

      // Start AI research
      const response = await apiService.startResearch(
        meetingData.companyWebsite,
        []
      )

      // Simulated insights
      setInsights({
        companyOverview: 'Tech startup focused on AI-powered sales tools...',
        keyProducts: ['Product A', 'Product B', 'Product C'],
        recentNews: 'Recently raised $10M Series A',
        talkingPoints: [
          'Emphasize our integration capabilities',
          'Highlight ROI case studies in similar industry',
          'Address scalability concerns proactively'
        ],
        objectionHandlers: {
          price: 'Focus on cost savings from automation',
          timing: 'Pilot program available in 2 weeks'
        }
      })

      // Save meeting prep
      const meetingId = Date.now()
      localStorage.setItem(`meeting_${meetingId}`, JSON.stringify({
        ...meetingData,
        insights,
        linkedinData,
        createdAt: new Date().toISOString()
      }))

    } catch (error) {
      console.error('Research error:', error)
      alert('Research failed. Please check backend connection.')
    } finally {
      setIsResearching(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Prepare for Meeting
          </h1>
          <p className="text-gray-600">
            Enter prospect details and get AI-powered insights
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Prospect Information */}
            <div className="card">
              <div className="flex items-center mb-4">
                <UserIcon className="h-6 w-6 text-primary-600 mr-2" />
                <h2 className="text-xl font-bold text-gray-900">
                  Prospect Information
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="prospectName" className="label">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    id="prospectName"
                    name="prospectName"
                    required
                    value={meetingData.prospectName}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="John Doe"
                  />
                </div>

                <div>
                  <label htmlFor="prospectEmail" className="label">
                    Email
                  </label>
                  <input
                    type="email"
                    id="prospectEmail"
                    name="prospectEmail"
                    value={meetingData.prospectEmail}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="john@company.com"
                  />
                </div>

                <div>
                  <label htmlFor="prospectRole" className="label">
                    Role/Title *
                  </label>
                  <input
                    type="text"
                    id="prospectRole"
                    name="prospectRole"
                    required
                    value={meetingData.prospectRole}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="VP of Sales"
                  />
                </div>

                <div>
                  <label htmlFor="prospectLinkedIn" className="label">
                    LinkedIn Profile URL
                  </label>
                  <input
                    type="url"
                    id="prospectLinkedIn"
                    name="prospectLinkedIn"
                    value={meetingData.prospectLinkedIn}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="https://linkedin.com/in/johndoe"
                  />
                </div>
              </div>
            </div>

            {/* Company Information */}
            <div className="card">
              <div className="flex items-center mb-4">
                <BuildingOfficeIcon className="h-6 w-6 text-primary-600 mr-2" />
                <h2 className="text-xl font-bold text-gray-900">
                  Company Information
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="companyName" className="label">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    id="companyName"
                    name="companyName"
                    required
                    value={meetingData.companyName}
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
                    value={meetingData.companyWebsite}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="https://acme.com"
                  />
                </div>

                <div className="md:col-span-2">
                  <label htmlFor="companyLinkedIn" className="label">
                    Company LinkedIn URL
                  </label>
                  <input
                    type="url"
                    id="companyLinkedIn"
                    name="companyLinkedIn"
                    value={meetingData.companyLinkedIn}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="https://linkedin.com/company/acme"
                  />
                </div>
              </div>
            </div>

            {/* Meeting Details */}
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Meeting Details
              </h2>

              <div className="space-y-4">
                <div>
                  <label htmlFor="meetingDate" className="label">
                    Meeting Date & Time
                  </label>
                  <input
                    type="datetime-local"
                    id="meetingDate"
                    name="meetingDate"
                    value={meetingData.meetingDate}
                    onChange={handleChange}
                    className="input-field"
                  />
                </div>

                <div>
                  <label htmlFor="meetingGoal" className="label">
                    Meeting Goal *
                  </label>
                  <input
                    type="text"
                    id="meetingGoal"
                    name="meetingGoal"
                    required
                    value={meetingData.meetingGoal}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="Discovery call, demo, closing, etc."
                  />
                </div>

                <div>
                  <label htmlFor="additionalNotes" className="label">
                    Additional Notes
                  </label>
                  <textarea
                    id="additionalNotes"
                    name="additionalNotes"
                    value={meetingData.additionalNotes}
                    onChange={handleChange}
                    rows="3"
                    className="input-field"
                    placeholder="Any other context or specific topics to discuss..."
                  />
                </div>
              </div>
            </div>

            <button
              onClick={handleResearch}
              disabled={isResearching}
              className="btn-primary w-full flex items-center justify-center text-lg py-3"
            >
              {isResearching ? (
                <>
                  <SparklesIcon className="animate-spin h-6 w-6 mr-2" />
                  AI is researching...
                </>
              ) : (
                <>
                  <MagnifyingGlassIcon className="h-6 w-6 mr-2" />
                  Start AI Research
                </>
              )}
            </button>
          </div>

          {/* Insights Panel */}
          <div className="lg:col-span-1">
            <div className="card sticky top-4">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                AI Insights
              </h2>

              {!insights && !linkedinData && (
                <div className="text-center py-8">
                  <SparklesIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 text-sm">
                    Click "Start AI Research" to generate insights
                  </p>
                </div>
              )}

              {linkedinData && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    LinkedIn Profile
                  </h3>
                  <div className="bg-blue-50 p-4 rounded-lg text-sm">
                    <p className="font-medium">{linkedinData.name}</p>
                    <p className="text-gray-600">{linkedinData.headline}</p>
                    <p className="text-gray-500 text-xs mt-2">
                      {linkedinData.location}
                    </p>
                  </div>
                </div>
              )}

              {insights && (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">
                      Company Overview
                    </h3>
                    <p className="text-sm text-gray-600">
                      {insights.companyOverview}
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">
                      Key Products
                    </h3>
                    <ul className="text-sm text-gray-600 list-disc list-inside">
                      {insights.keyProducts.map((product, i) => (
                        <li key={i}>{product}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">
                      Talking Points
                    </h3>
                    <ul className="text-sm text-gray-600 space-y-2">
                      {insights.talkingPoints.map((point, i) => (
                        <li key={i} className="flex items-start">
                          <span className="text-primary-600 mr-2">✓</span>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MeetingPrep
