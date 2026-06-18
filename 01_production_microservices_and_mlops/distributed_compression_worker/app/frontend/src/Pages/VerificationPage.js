import React, { useEffect, useState } from 'react';
import api from '../API';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import Cookies from 'js-cookie';
import './GuestPage.css';
import './SignupLogin.css';

const Verification = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [verificationStatus, setVerificationStatus] = useState('');

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const token = searchParams.get('token');

    if (token) {
      api.post('/verification', { token })
        .then((response) => {
          if (response.status === 200) {
            // Cookies.set("access_token", response.data.access_token);
            // Cookies.set("refresh_token", response.data.refresh_token);
            // navigate('/home');
            
            setTimeout(() => {
                navigate('/login');
              }, 2000);
            setVerificationStatus('Email verified successfully');

          } else {
            setVerificationStatus('Email verification failed');
          }
        })
        .catch((error) => {
          console.error('Email verification failed', error);
          setVerificationStatus('Email verification failed');
        });
    } else {
      setVerificationStatus('Token missing');
    }
  }, [location]);

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
        <h3>Verifying Email</h3>
        <h2>{verificationStatus}</h2>
      </div>
    </div>
  );
};

export default Verification;