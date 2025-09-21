import { Link } from 'react-router-dom'
import { SignedIn, SignedOut, UserButton } from '@clerk/clerk-react'
import HeroSection from './HeroSection'

export default function HomePage() {
  return (
    <div>
      {/* Navigation Header */}
      <header style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        background: 'rgba(15, 20, 25, 0.9)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(59, 130, 246, 0.15)',
        padding: '1rem 2rem'
      }}>
        <nav style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          <div style={{ 
            color: 'white', 
            fontSize: '1.5rem', 
            fontWeight: 'bold' 
          }}>
            LegalX
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <SignedOut>
              <Link 
                to="/sign-in" 
                style={{ 
                  color: '#94a3b8',
                  textDecoration: 'none',
                  fontSize: '0.95rem',
                  transition: 'color 0.3s ease'
                }}
              >
                Sign In
              </Link>
              <Link 
                to="/sign-up" 
                style={{ 
                  padding: '8px 16px', 
                  backgroundColor: '#3b82f6', 
                  color: 'white', 
                  textDecoration: 'none', 
                  borderRadius: '6px',
                  fontSize: '0.95rem',
                  transition: 'all 0.3s ease'
                }}
              >
                Get Started
              </Link>
            </SignedOut>
            
            <SignedIn>
              <Link 
                to="/chat" 
                style={{ 
                  color: '#94a3b8',
                  textDecoration: 'none',
                  fontSize: '0.95rem',
                  marginRight: '1rem'
                }}
              >
                Chat
              </Link>
              <Link 
                to="/profile" 
                style={{ 
                  color: '#94a3b8',
                  textDecoration: 'none',
                  fontSize: '0.95rem',
                  marginRight: '1rem'
                }}
              >
                Profile
              </Link>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <HeroSection />
    </div>
  )
}