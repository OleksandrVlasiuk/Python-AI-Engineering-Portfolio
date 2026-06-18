import React, { useState } from 'react';
import api from '../API';
import { useNavigate, Link } from 'react-router-dom';
import './GuestPage.css';
import './SignupLogin.css';

const Signup = () => {
  const [name, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const navigate = useNavigate();

  const handleSignup = async () => {
    try {
      await api.post('/signup', { name, email, password });

      navigate('/verify');
    } catch (error) {
      console.error('Signup failed', error);
    }
  };

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
        <h2>Sign up</h2>
        <div className="mb-3">
          <input
            type="text"
            className="form-control custom-width" 
            placeholder="Username"
            value={name}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <input
            type="text"
            className="form-control custom-width"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <input
            type="password"
            className="form-control custom-width" 
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button className="btn btn-primary" onClick={handleSignup}>
          Sign up
        </button>
      </div>
    </div>
  );
};

export default Signup;
