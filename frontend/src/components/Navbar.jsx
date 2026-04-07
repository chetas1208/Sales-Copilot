import { Link, useLocation } from 'react-router-dom'
import { UserCircleIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline'

const Navbar = ({ user, onLogout }) => {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex space-x-8">
            <Link
              to="/"
              className="flex items-center text-2xl font-bold text-primary-600"
            >
              Meetstream AI
            </Link>

            <div className="hidden md:flex md:space-x-4 md:items-center">
              <Link
                to="/"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  isActive('/')
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Dashboard
              </Link>
              <Link
                to="/meeting-prep"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  isActive('/meeting-prep')
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Prepare Meeting
              </Link>
              <Link
                to="/past-meetings"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  isActive('/past-meetings')
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Past Meetings
              </Link>
              <Link
                to="/profile"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  isActive('/profile')
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Profile
              </Link>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <UserCircleIcon className="h-8 w-8 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">
                {user?.name || user?.email}
              </span>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
