# Clerk Google OAuth Setup Guide

## Step 1: Register at Clerk.com
1. Go to [clerk.com](https://clerk.com) and create an account
2. Create a new application for your project
3. Note down your application details

## Step 2: Enable Google OAuth
1. In your Clerk dashboard, navigate to "Social Connections"
2. Enable Google OAuth provider
3. Configure your Google OAuth settings if needed

## Step 3: Get Your Clerk Keys
1. Go to the "API Keys" section in your Clerk dashboard
2. Copy your **Publishable Key** (starts with `pk_test_` or `pk_live_`)
3. You'll need this for the next step

## Step 4: Configure Environment Variables
1. Open the `.env` file in your project root
2. Replace `pk_test_your-publishable-key-here` with your actual Clerk Publishable Key:
   ```
   VITE_CLERK_PUBLISHABLE_KEY=pk_test_your-actual-key-here
   ```

## Step 5: Test the Setup
1. Start the development server:
   ```bash
   npm run dev
   ```
2. Open your browser and navigate to `http://localhost:5173`
3. Click "Sign In" and test the Google OAuth flow
4. After successful authentication, you should be redirected to the dashboard

## Features Implemented
- ✅ Clerk React SDK integration
- ✅ Google OAuth authentication
- ✅ Protected routes
- ✅ Sign-in/Sign-up pages
- ✅ Dashboard with user information
- ✅ User management with UserButton

## File Structure
```
src/
├── components/
│   ├── HomePage.jsx       # Landing page with auth options
│   ├── SignInPage.jsx     # Sign-in page with Clerk component
│   ├── SignUpPage.jsx     # Sign-up page with Clerk component
│   └── Dashboard.jsx      # Protected dashboard page
├── App.jsx                # Main app with routing
└── main.jsx               # App entry point with ClerkProvider
```

## Environment Variables Required
- `VITE_CLERK_PUBLISHABLE_KEY` - Your Clerk publishable key
- `VITE_CLERK_SIGN_IN_URL` - Sign-in page URL (/sign-in)
- `VITE_CLERK_SIGN_UP_URL` - Sign-up page URL (/sign-up)
- `VITE_CLERK_AFTER_SIGN_IN_URL` - Redirect URL after sign-in (/dashboard)
- `VITE_CLERK_AFTER_SIGN_UP_URL` - Redirect URL after sign-up (/dashboard)