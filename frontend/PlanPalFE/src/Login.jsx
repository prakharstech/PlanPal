// src/Login.jsx
import React from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import { Link } from 'react-router-dom';
import './Login.css';

function Login({ onLoginSuccess }) {

  const handleLogin = useGoogleLogin({
  flow: 'auth-code',
  scope: "openid email profile https://www.googleapis.com/auth/calendar",

  onSuccess: async (codeResponse) => {
  try {
    const res = await fetch("https://planpal-lrka.onrender.com/auth/google", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: codeResponse.code }),
    });

    const data = await res.json();

    // ✅ Transform backend → frontend expected format
    onLoginSuccess({
      token: data.access_token,
      user: {
        email: data.email,
        name: data.name
      }
    });

  } catch (error) {
    console.error("Failed to exchange auth code:", error);
  }
},


  onError: (err) => console.error(err),
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
        <p style={{ marginTop: '20px', fontSize: '12px' }}>
          By signing in, you agree to our <Link to="/privacy">Privacy Policy</Link>.
        </p>
      </div>
    </div>
  );
}

export default Login;
