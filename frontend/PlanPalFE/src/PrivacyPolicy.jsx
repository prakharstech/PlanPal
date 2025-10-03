import React from 'react';
import { Link } from 'react-router-dom';
import './Login.css'; // We can reuse the login styles for a consistent look

function PrivacyPolicy() {
  return (
    <div className="login-container">
      <div className="login-box" style={{ textAlign: 'left', maxWidth: '800px', overflowY: 'auto', maxHeight: '90vh' }}>
        <h1 style={{ textAlign: 'center' }}>Privacy Policy for PlanPal</h1>
        <p style={{ textAlign: 'center', marginBottom: '30px' }}>Last Updated: October 3, 2025</p>

        <h3>1. Introduction</h3>
        <p>Welcome to PlanPal ("we," "us," or "our"). This policy explains how we collect, use, and share information when you use our AI-powered calendar assistant.</p>

        <h3>2. Information We Collect</h3>
        <ul>
          <li><p><strong>Google Account Information:</strong> Your name and email address to personalize your experience.</p></li>
          <li><p><strong>Google Calendar Data:</strong> We require read and write access to your primary Google Calendar to view, create, modify, and delete events based on your commands.</p></li>
          <li><p><strong>Google Authentication Tokens:</strong> We store an access token in your browser's local storage to securely interact with your Google Calendar. This is not stored on our servers.</p></li>
        </ul>

        <h3>3. How We Use Your Information</h3>
        <p>Your data is used exclusively to provide PlanPal's features, such as processing your commands, checking for scheduling conflicts, and personalizing the interface.</p>
        
        <h3>4. How We Share Your Information</h3>
        <p>We do not sell your personal data. Information is only shared with essential third-party services:</p>
        <ul>
          <li><p><strong>Google LLC:</strong> All calendar interactions are processed through Google's own API, adhering to the Google API Services User Data Policy.</p></li>
          <li><p><strong>Mistral AI:</strong> Your natural language commands are sent to the Mistral AI API to be understood and processed.</p></li>
        </ul>

        <h3>5. Data Security</h3>
        <p>Your Google authentication token is stored securely in your browser. All communication between the app and our servers is encrypted using HTTPS.</p>

        <h3>6. Your Rights and Choices</h3>
        <p>You can revoke PlanPal's access to your Google Account at any time by visiting the <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer">Google Account permissions page</a>.</p>

        <h3>7. Contact Us</h3>
        <p>If you have any questions, please contact us at <a href="mailto:prakhar.srivastava0509@gmail.com">prakhar.srivastava0509@gmail.com</a>.</p>
        
        <div style={{ textAlign: 'center', marginTop: '30px' }}>
          <Link to="/" className="google-login-button">Back to App</Link>
        </div>
      </div>
    </div>
  );
}

export default PrivacyPolicy;