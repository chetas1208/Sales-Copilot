import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  PlusIcon,
  ChartBarIcon,
  ClockIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline'

const Dashboard = ({ user }) => {
  const [stats, setStats] = useState({
    totalMeetings: 0,
    upcomingMeetings: 0,
    activeResearch: 0,
    linkedinProfiles: 0,
  })

  useEffect(() => {
    // TODO: Fetch real stats from API
    setStats({
      totalMeetings: 12,
      upcomingMeetings: 3,
      activeResearch: 2,
      linkedinProfiles: 8,
    })
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name}! 👋
          </h1>
          <p className="text-gray-600">
            Prepare for your next sales call with AI-powered insights
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Link to="/meeting-prep">
            <div className="card hover:shadow-xl transition-shadow cursor-pointer">
              <div className="flex items-center">
                <div className="p-3 bg-primary-100 rounded-lg">
                  <PlusIcon className="h-8 w-8 text-primary-600" />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Prepare New Meeting
                  </h3>
                  <p className="text-sm text-gray-600">
                    Research prospects and get AI insights
                  </p>
                </div>
              </div>
            </div>
          </Link>

          <Link to="/past-meetings">
            <div className="card hover:shadow-xl transition-shadow cursor-pointer">
              <div className="flex items-center">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <ClockIcon className="h-8 w-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    View Past Meetings
                  </h3>
                  <p className="text-sm text-gray-600">
                    Review insights and follow-ups
                  </p>
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Total Meetings
                </p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats.totalMeetings}
                </p>
              </div>
              <ChartBarIcon className="h-12 w-12 text-primary-600 opacity-50" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Upcoming
                </p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats.upcomingMeetings}
                </p>
              </div>
              <ClockIcon className="h-12 w-12 text-green-600 opacity-50" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Active Research
                </p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats.activeResearch}
                </p>
              </div>
              <ChartBarIcon className="h-12 w-12 text-orange-600 opacity-50" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  LinkedIn Profiles
                </p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats.linkedinProfiles}
                </p>
              </div>
              <UserGroupIcon className="h-12 w-12 text-blue-600 opacity-50" />
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Recent Activity
          </h2>
          <div className="space-y-4">
            <div className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-900">
                  Research completed for Stripe Inc.
                </p>
                <p className="text-sm text-gray-600">2 hours ago</p>
              </div>
            </div>

            <div className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-900">
                  LinkedIn profile analyzed: John Doe
                </p>
                <p className="text-sm text-gray-600">5 hours ago</p>
              </div>
            </div>

            <div className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-900">
                  Meeting insights generated for Acme Corp
                </p>
                <p className="text-sm text-gray-600">Yesterday</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
