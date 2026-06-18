import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import './GuestPage.css';

const GuestPage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const access_token = Cookies.get('access_token');
    if (access_token) {
      navigate('/home');
    }
  }, [navigate]);

  return (
    <div className="guest-page-container">
      <nav className='navbar navbar-dark bg-primary'>
        <div className='container-fluid'>
          <a className='navbar-brand' href='#'>Encode Your Text</a>
        </div>
      </nav>
      <div className="guest-page-content">
        <div className="button-container">
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/signup')}>
            Sign up
          </button>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/login')}>
            Login
          </button>
        </div>
      </div>
    </div>
  );
}

export default GuestPage;
