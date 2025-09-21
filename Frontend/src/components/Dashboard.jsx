import { UserButton, useUser, SignOutButton } from '@clerk/clerk-react'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { user, isLoaded } = useUser()

  if (!isLoaded) {
    return <div style={{ padding: '2rem', color: '#ffffff' }}>Loading...</div>
  }

  return (
    <div style={{ 
      padding: '2rem', 
      background: '#0a0a0f', 
      minHeight: '100vh', 
      color: '#ffffff' 
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '2rem',
        maxWidth: '1200px',
        margin: '0 auto 2rem auto'
      }}>
        <h1 style={{ margin: 0, color: '#ffffff' }}>Dashboard</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <UserButton afterSignOutUrl="/" />
        </div>
      </div>
      
      <div style={{ 
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* User Info Section */}
        <div style={{ 
          backgroundColor: 'rgba(15, 23, 42, 0.8)', 
          padding: '1.5rem', 
          borderRadius: '12px',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          marginBottom: '2rem'
        }}>
          <h2 style={{ color: '#ffffff', marginBottom: '1rem' }}>Welcome back!</h2>
          {user && (
            <div style={{ marginBottom: '1rem' }}>
              <p style={{ margin: '0.5rem 0', color: '#e2e8f0' }}>
                <strong>Name:</strong> {user.fullName || 'Not provided'}
              </p>
              <p style={{ margin: '0.5rem 0', color: '#e2e8f0' }}>
                <strong>Email:</strong> {user.primaryEmailAddress?.emailAddress}
              </p>
              <p style={{ margin: '0.5rem 0', color: '#94a3b8', fontSize: '0.875rem' }}>
                <strong>User ID:</strong> {user.id}
              </p>
            </div>
          )}
          <p style={{ color: '#94a3b8', margin: 0 }}>
            You are successfully authenticated with Google OAuth through Clerk!
          </p>
        </div>

        {/* Quick Actions */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          {/* Chat Section */}
          <div style={{ 
            backgroundColor: 'rgba(15, 23, 42, 0.8)', 
            padding: '1.5rem', 
            borderRadius: '12px',
            border: '1px solid rgba(59, 130, 246, 0.2)'
          }}>
            <h3 style={{ color: '#ffffff', marginBottom: '1rem' }}>Legal AI Chat</h3>
            <p style={{ color: '#94a3b8', marginBottom: '1.5rem', lineHeight: '1.5' }}>
              Ask questions about legal documents and get AI-powered insights with source references.
            </p>
            <Link 
              to="/chat" 
              style={{ 
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '12px 24px', 
                background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                color: 'white', 
                textDecoration: 'none', 
                borderRadius: '8px',
                fontSize: '0.95rem',
                fontWeight: '600',
                transition: 'all 0.3s ease'
              }}
            >
              Start Chat →
            </Link>
          </div>

          {/* Documents Section */}
          <div style={{ 
            backgroundColor: 'rgba(15, 23, 42, 0.8)', 
            padding: '1.5rem', 
            borderRadius: '12px',
            border: '1px solid rgba(59, 130, 246, 0.2)'
          }}>
            <h3 style={{ color: '#ffffff', marginBottom: '1rem' }}>Document Management</h3>
            <p style={{ color: '#94a3b8', marginBottom: '1.5rem', lineHeight: '1.5' }}>
              Upload and manage your legal documents for AI analysis and searchable queries.
            </p>
            <button 
              style={{ 
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '12px 24px', 
                backgroundColor: 'transparent',
                border: '1px solid rgba(148, 163, 184, 0.3)',
                color: '#e2e8f0', 
                borderRadius: '8px',
                fontSize: '0.95rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              disabled
            >
              Coming Soon
            </button>
          </div>

          {/* Jobs Section */}
          <div style={{ 
            backgroundColor: 'rgba(15, 23, 42, 0.8)', 
            padding: '1.5rem', 
            borderRadius: '12px',
            border: '1px solid rgba(59, 130, 246, 0.2)'
          }}>
            <h3 style={{ color: '#ffffff', marginBottom: '1rem' }}>Job Queue</h3>
            <p style={{ color: '#94a3b8', marginBottom: '1.5rem', lineHeight: '1.5' }}>
              Monitor the status of your document processing and query jobs.
            </p>
            <button 
              style={{ 
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '12px 24px', 
                backgroundColor: 'transparent',
                border: '1px solid rgba(148, 163, 184, 0.3)',
                color: '#e2e8f0', 
                borderRadius: '8px',
                fontSize: '0.95rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              disabled
            >
              Coming Soon
            </button>
          </div>
        </div>

        {/* Backend Integration Status */}
        <div style={{ 
          backgroundColor: 'rgba(15, 23, 42, 0.8)', 
          padding: '1.5rem', 
          borderRadius: '12px',
          border: '1px solid rgba(34, 197, 94, 0.2)'
        }}>
          <h3 style={{ color: '#22c55e', marginBottom: '1rem' }}>System Integration</h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '1rem' 
          }}>
            <div>
              <p style={{ color: '#e2e8f0', fontWeight: '500', margin: '0 0 0.25rem 0' }}>Authentication</p>
              <p style={{ color: '#22c55e', fontSize: '0.875rem', margin: 0 }}>✓ Clerk Integration Active</p>
            </div>
            <div>
              <p style={{ color: '#e2e8f0', fontWeight: '500', margin: '0 0 0.25rem 0' }}>Backend API</p>
              <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>http://localhost:8000</p>
            </div>
            <div>
              <p style={{ color: '#e2e8f0', fontWeight: '500', margin: '0 0 0.25rem 0' }}>WebSocket</p>
              <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>ws://localhost:8000/ws/{user.id}</p>
            </div>
            <div>
              <p style={{ color: '#e2e8f0', fontWeight: '500', margin: '0 0 0.25rem 0' }}>User Session</p>
              <p style={{ color: '#22c55e', fontSize: '0.875rem', margin: 0 }}>✓ Active & Synced</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}