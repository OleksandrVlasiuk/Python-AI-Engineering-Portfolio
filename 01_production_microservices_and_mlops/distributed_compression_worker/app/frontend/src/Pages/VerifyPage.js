import React from 'react';
import { Link } from 'react-router-dom';
import './GuestPage.css';
import './SignupLogin.css';


const VeifyEmail = () => {
  
  return (
    <div className="guest-page-container" style={{ minHeight: "100vh" }}>
      <nav className="navbar navbar-dark bg-primary">
        <div className="container-fluid">
          <Link to="/" className="navbar-brand">
            Encode Your Text
          </Link>
        </div>
      </nav>
      <div className="page-form">
        <h2>Verify your email</h2>
      </div>
    </div>
  );
};

export default VeifyEmail;