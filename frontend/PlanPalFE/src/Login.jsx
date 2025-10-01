// src/Login.jsx
import React from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import './Login.css';

function Login({ onLoginSuccess }) {

  const handleLogin = useGoogleLogin({
    flow: 'auth-code',
    redirect_uri: 'https://plan-pal-ten.vercel.app',

    scope: 'https://www.googleapis.com/auth/calendar', 
    
    // The backend will handle the code exchange
    onSuccess: async (codeResponse) => {
      try {
        const res = await fetch("https://planpal-lrka.onrender.com/auth/google", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: codeResponse.code }),
        });

        if (!res.ok) {
          throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();
        //console.log("Data received from backend:", data);
        onLoginSuccess(data); // Passing the access_token to the App component
      } catch (error) {
        console.error("Failed to exchange auth code:", error);
      }
    },
    onError: (errorResponse) => {
      console.error("Login Failed:", errorResponse);
    },
  });

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="avatar">🤖</div>
        <h1>Welcome to PlanPal</h1>
        <p>Your intelligent calendar assistant. Log in to continue.</p>
        <button className="google-login-button" onClick={() => handleLogin()}>
          <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" />
          Sign in with Google
        </button>
      </div>
    </div>
  );
}

export default Login;