import { UserButton, useUser, SignOutButton } from '@clerk/clerk-react'
import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './Profile.css'

export default function Profile() {
  const { user, isLoaded } = useUser()
  const [stats, setStats] = useState({
    totalChats: 0,
    documentsUploaded: 0,
    queriesProcessed: 0,
    lastActive: new Date().toLocaleDateString()
  })

  useEffect(() => {
    // Load user stats from localStorage or API
    const savedStats = localStorage.getItem(`userStats_${user?.id}`)
    if (savedStats) {
      setStats(JSON.parse(savedStats))
    }
  }, [user?.id])

  if (!isLoaded) {
    return (
      <div className="profile-loading">
        <div className="loading-spinner"></div>
        <p>Loading your profile...</p>
      </div>
    )
  }

  const quickActions = [
    {
      title: 'Start New Chat',
      description: 'Begin a conversation with our Legal AI Assistant',
      icon: 'Chat',
      link: '/chat',
      primary: true,
      status: 'active'
    },
    {
      title: 'Upload Documents',
      description: 'Add legal documents for AI analysis',
      icon: 'Docs',
      link: '/chat',
      primary: false,
      status: 'active'
    },
    {
      title: 'Chat History',
      description: 'Review your previous conversations',
      icon: 'History',
      action: () => console.log('View history'),
      primary: false,
      status: 'coming-soon'
    },
    {
      title: 'Settings',
      description: 'Customize your AI preferences',
      icon: 'Settings',
      action: () => console.log('Open settings'),
      primary: false,
      status: 'coming-soon'
    }
  ]

  return (
    <div className="profile-container">
      {/* Header Section */}
      <div className="profile-header">
        <div className="header-content">
          <div className="user-info-section">
            <div className="user-avatar">
              {user?.imageUrl ? (
                <img src={user.imageUrl} alt="Profile" className="avatar-image" />
              ) : (
                <div className="avatar-placeholder">
                  {user?.firstName?.charAt(0) || user?.emailAddresses?.[0]?.emailAddress?.charAt(0) || 'U'}
                </div>
              )}
            </div>
            <div className="user-details">
              <h1 className="user-name">
                {user?.fullName || 'Welcome User'}
              </h1>
              <p className="user-email">
                {user?.primaryEmailAddress?.emailAddress}
              </p>
              <div className="user-status">
                <span className="status-dot active"></span>
                <span className="status-text">Online</span>
              </div>
            </div>
          </div>
          <div className="header-actions">
            <UserButton 
              afterSignOutUrl="/"
              appearance={{
                elements: {
                  avatarBox: "h-10 w-10",
                  userButtonPopoverCard: "bg-slate-800 border-slate-700",
                  userButtonPopoverActionButton: "text-slate-200 hover:bg-slate-700"
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">Chat</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.totalChats}</h3>
              <p className="stat-label">Total Chats</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">Docs</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.documentsUploaded}</h3>
              <p className="stat-label">Documents</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">Search</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.queriesProcessed}</h3>
              <p className="stat-label">Queries</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">Time</div>
            <div className="stat-content">
              <h3 className="stat-number">{stats.lastActive}</h3>
              <p className="stat-label">Last Active</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="actions-section">
        <h2 className="section-title">Quick Actions</h2>
        <div className="actions-grid">
          {quickActions.map((action, index) => (
            <div key={index} className={`action-card ${action.primary ? 'primary' : ''} ${action.status}`}>
              <div className="action-icon">{action.icon}</div>
              <div className="action-content">
                <h3 className="action-title">{action.title}</h3>
                <p className="action-description">{action.description}</p>
              </div>
              <div className="action-button">
                {action.link ? (
                  <Link to={action.link} className="btn">
                    {action.status === 'active' ? 'Go' : 'Soon'}
                  </Link>
                ) : (
                  <button 
                    onClick={action.action} 
                    className="btn"
                    disabled={action.status !== 'active'}
                  >
                    {action.status === 'active' ? 'Open' : 'Soon'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Account Information */}
      <div className="account-section">
        <h2 className="section-title">Account Information</h2>
        <div className="account-grid">
          <div className="info-card">
            <h3 className="info-title">Personal Details</h3>
            <div className="info-content">
              <div className="info-item">
                <span className="info-label">Full Name</span>
                <span className="info-value">{user?.fullName || 'Not provided'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Email</span>
                <span className="info-value">{user?.primaryEmailAddress?.emailAddress}</span>
              </div>
              <div className="info-item">
                <span className="info-label">User ID</span>
                <span className="info-value user-id">{user?.id}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Account Created</span>
                <span className="info-value">
                  {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown'}
                </span>
              </div>
            </div>
          </div>

          <div className="info-card">
            <h3 className="info-title">System Integration</h3>
            <div className="info-content">
              <div className="integration-item">
                <div className="integration-status active">
                  <span className="status-dot"></span>
                  <span className="status-label">Authentication</span>
                </div>
                <span className="integration-value">Clerk OAuth Active</span>
              </div>
              <div className="integration-item">
                <div className="integration-status active">
                  <span className="status-dot"></span>
                  <span className="status-label">Backend API</span>
                </div>
                <span className="integration-value">localhost:8000</span>
              </div>
              <div className="integration-item">
                <div className="integration-status active">
                  <span className="status-dot"></span>
                  <span className="status-label">WebSocket</span>
                </div>
                <span className="integration-value">Real-time Connected</span>
              </div>
              <div className="integration-item">
                <div className="integration-status active">
                  <span className="status-dot"></span>
                  <span className="status-label">Session</span>
                </div>
                <span className="integration-value">Active & Synced</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="activity-section">
        <h2 className="section-title">Recent Activity</h2>
        <div className="activity-card">
          <div className="activity-list">
            <div className="activity-item">
              <div className="activity-icon">Welcome</div>
              <div className="activity-content">
                <p className="activity-text">Welcome to LegalX!</p>
                <span className="activity-time">Just now</span>
              </div>
            </div>
            <div className="activity-item">
              <div className="activity-icon">Auth</div>
              <div className="activity-content">
                <p className="activity-text">Successfully authenticated with Google OAuth</p>
                <span className="activity-time">Today</span>
              </div>
            </div>
            <div className="activity-item">
              <div className="activity-icon">Setup</div>
              <div className="activity-content">
                <p className="activity-text">Profile setup completed</p>
                <span className="activity-time">Today</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}