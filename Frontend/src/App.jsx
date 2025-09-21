import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react'
import HomePage from './components/HomePage'
import SignInPage from './components/SignInPage'
import SignUpPage from './components/SignUpPage'
import Profile from './components/Profile'
import ChatPage from './components/ChatPage'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/sign-up" element={<SignUpPage />} />
        
        {/* Protected Routes */}
        <Route 
          path="/dashboard" 
          element={
            <>
              <SignedIn>
                <Profile />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          } 
        />
        
        <Route 
          path="/profile" 
          element={
            <>
              <SignedIn>
                <Profile />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          } 
        />
        
        <Route 
          path="/chat" 
          element={
            <>
              <SignedIn>
                <ChatPage />
              </SignedIn>
              <SignedOut>
                <RedirectToSignIn />
              </SignedOut>
            </>
          } 
        />
      </Routes>
    </Router>
  )
}

export default App
