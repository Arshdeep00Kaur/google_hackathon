import React from 'react'
import './HeroSection.css'

const HeroSection = () => {
  return (
    <section className="hero-section">
      <div className="grid-background"></div>
      <div className="hero-content">
        <div className="announcement-badge">
          Exciting announcement
        </div>
        
        <h1 className="hero-title">
          AI-Powered Legal Assistant
          <br />
          that works for you
        </h1>
        
        <p className="hero-subtitle">
          Transform your legal document analysis with advanced AI technology.
          <br />
          Upload documents, ask questions, and get instant insights with source citations.
        </p>
        
        <div className="cta-buttons">
          <button className="btn-primary">
            Try it free
            <span className="arrow">→</span>
          </button>
          <button className="btn-secondary">
            Learn more
          </button>
        </div>
      </div>
    </section>
  )
}

export default HeroSection