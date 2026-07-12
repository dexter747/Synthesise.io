# Google OAuth Setup Guide

## Overview
This guide will help you configure Google OAuth for the Synthesize.io application.

## Prerequisites
- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)

## Setup Steps

### 1. Create a Google Cloud Project (if you don't have one)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter project name (e.g., "Synthesize.io")
5. Click "Create"

### 2. Enable Google+ API
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API" or "People API"
3. Click on it and click "Enable"

### 3. Configure OAuth Consent Screen
1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type
3. Click "Create"
4. Fill in the required information:
   - **App name**: Synthesize.io
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click "Save and Continue"
6. Skip the "Scopes" step (click "Save and Continue")
7. Add test users if in testing mode
8. Click "Save and Continue"

### 4. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application"
4. Configure the OAuth client:
   - **Name**: Synthesize.io Web Client
   - **Authorized JavaScript origins**:
     - `http://localhost:8000`
     - `http://localhost:3000`
   - **Authorized redirect URIs**:
     - `http://localhost:8000/api/v1/auth/oauth/google/callback`
5. Click "Create"
6. Copy the **Client ID** and **Client Secret**

### 5. Update Environment Variables
1. Open `/apps/api/.env.local`
2. Replace the placeholder values:
   ```bash
   GOOGLE_OAUTH_CLIENT_ID=your-actual-client-id-here
   GOOGLE_OAUTH_CLIENT_SECRET=your-actual-client-secret-here
   ```
3. Save the file
4. Restart the API server

### 6. Test the Integration
1. Go to `http://localhost:3000/auth/login`
2. Click "Sign in with Google"
3. You should be redirected to Google's login page
4. After authentication, you'll be redirected back to the app

## Production Setup
When deploying to production, make sure to:

1. Update the OAuth consent screen to "Production"
2. Add your production domain to the authorized origins and redirect URIs:
   - Authorized origins: `https://yourdomain.com`
   - Redirect URIs: `https://api.yourdomain.com/api/v1/auth/oauth/google/callback`
3. Update the environment variables in your production server

## Troubleshooting

### Error: "Access blocked: Authorization Error"
- Make sure your email is added as a test user in the OAuth consent screen
- Verify that the redirect URI matches exactly

### Error: "invalid_client"
- Double-check that the Client ID and Client Secret are correctly copied
- Make sure there are no extra spaces or quotes in the environment variables
- Restart the API server after updating the environment variables

### Error: "redirect_uri_mismatch"
- Verify that the redirect URI in Google Cloud Console matches:
  `http://localhost:8000/api/v1/auth/oauth/google/callback`
- Make sure there are no trailing slashes

## Security Notes
- Never commit your `.env.local` file to version control
- Keep your Client Secret secure
- Rotate credentials if they are exposed
- Use different OAuth clients for development and production
