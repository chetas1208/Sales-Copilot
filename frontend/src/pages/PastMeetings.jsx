import { useState, useEffect } from 'react'
import { ClockIcon, BuildingOfficeIcon, UserIcon } from '@heroicons/react/24/outline'

const PastMeetings = ({ user }) => {
  const [meetings, setMeetings] = useState([])
  const [selectedMeeting, setSelectedMeeting] = useState(null)

  useEffect(() => {
    // Load meetings from localStorage
    const loadMeetings = () => {
      const allKeys = Object.keys(localStorage)
      const meetingKeys = allKeys.filter(key => key.startsWith('meeting_'))

      const loadedMeetings = meetingKeys.map(key => {
        const data = JSON.parse(localStorage.getItem(key))
        return {
          id: key.replace('meeting_', ''),
          ...data
        }
      }).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))

      setMeetings(loadedMeetings)
    }

    loadMeetings()
  }, [])

  const formatDate = (dateString) => {
    if (!dateString) return 'Not scheduled'
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">
            Past Meetings
          </h1>
          <p className="text-white opacity-90">
            Review insights and follow-ups from previous meetings
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Meetings List */}
          <div className="lg:col-span-1 space-y-4">
            {meetings.length === 0 ? (
              <div className="card text-center py-8">
                <ClockIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No past meetings yet</p>
                <p className="text-sm text-gray-400 mt-2">
                  Prepare your first meeting to see it here
                </p>
              </div>
            ) : (
              meetings.map((meeting) => (
                <div
                  key={meeting.id}
                  onClick={() => setSelectedMeeting(meeting)}
                  className={`card cursor-pointer transition-all ${
                    selectedMeeting?.id === meeting.id
                      ? 'ring-2 ring-primary-500 shadow-xl'
                      : 'hover:shadow-xl'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">
                        {meeting.companyName}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {meeting.prospectName} - {meeting.prospectRole}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center text-xs text-gray-500">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {formatDate(meeting.createdAt)}
                  </div>

                  {meeting.meetingDate && (
                    <div className="mt-2 text-xs text-primary-600 font-medium">
                      Meeting: {formatDate(meeting.meetingDate)}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Meeting Details */}
          <div className="lg:col-span-2">
            {!selectedMeeting ? (
              <div className="card text-center py-16">
                <BuildingOfficeIcon className="h-20 w-20 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Select a meeting to view details</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Meeting Info */}
                <div className="card">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">
                    {selectedMeeting.companyName}
                  </h2>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Prospect</p>
                      <div className="flex items-center">
                        <UserIcon className="h-5 w-5 text-gray-400 mr-2" />
                        <div>
                          <p className="font-medium text-gray-900">
                            {selectedMeeting.prospectName}
                          </p>
                          <p className="text-sm text-gray-600">
                            {selectedMeeting.prospectRole}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div>
                      <p className="text-sm text-gray-600 mb-1">Company</p>
                      <div className="flex items-center">
                        <BuildingOfficeIcon className="h-5 w-5 text-gray-400 mr-2" />
                        <div>
                          <p className="font-medium text-gray-900">
                            {selectedMeeting.companyName}
                          </p>
                          {selectedMeeting.companyWebsite && (
                            <a
                              href={selectedMeeting.companyWebsite}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-primary-600 hover:underline"
                            >
                              Visit website →
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {selectedMeeting.meetingGoal && (
                    <div className="mt-4 p-4 bg-primary-50 rounded-lg">
                      <p className="text-sm font-medium text-primary-900 mb-1">
                        Meeting Goal
                      </p>
                      <p className="text-sm text-primary-700">
                        {selectedMeeting.meetingGoal}
                      </p>
                    </div>
                  )}

                  {selectedMeeting.additionalNotes && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm font-medium text-gray-900 mb-1">
                        Notes
                      </p>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {selectedMeeting.additionalNotes}
                      </p>
                    </div>
                  )}
                </div>

                {/* LinkedIn Data */}
                {selectedMeeting.linkedinData && (
                  <div className="card">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">
                      LinkedIn Profile
                    </h3>
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <p className="font-medium text-gray-900">
                        {selectedMeeting.linkedinData.name}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {selectedMeeting.linkedinData.headline}
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        {selectedMeeting.linkedinData.location}
                      </p>
                      {selectedMeeting.linkedinData.summary && (
                        <p className="text-sm text-gray-700 mt-3">
                          {selectedMeeting.linkedinData.summary}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* AI Insights */}
                {selectedMeeting.insights && (
                  <div className="card">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">
                      AI Insights
                    </h3>

                    <div className="space-y-4">
                      {selectedMeeting.insights.companyOverview && (
                        <div>
                          <h4 className="font-semibold text-gray-900 mb-2">
                            Company Overview
                          </h4>
                          <p className="text-sm text-gray-700">
                            {selectedMeeting.insights.companyOverview}
                          </p>
                        </div>
                      )}

                      {selectedMeeting.insights.keyProducts && (
                        <div>
                          <h4 className="font-semibold text-gray-900 mb-2">
                            Key Products
                          </h4>
                          <ul className="text-sm text-gray-700 list-disc list-inside">
                            {selectedMeeting.insights.keyProducts.map((product, i) => (
                              <li key={i}>{product}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {selectedMeeting.insights.talkingPoints && (
                        <div>
                          <h4 className="font-semibold text-gray-900 mb-2">
                            Talking Points
                          </h4>
                          <ul className="text-sm text-gray-700 space-y-2">
                            {selectedMeeting.insights.talkingPoints.map((point, i) => (
                              <li key={i} className="flex items-start">
                                <span className="text-primary-600 mr-2">✓</span>
                                {point}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default PastMeetings
