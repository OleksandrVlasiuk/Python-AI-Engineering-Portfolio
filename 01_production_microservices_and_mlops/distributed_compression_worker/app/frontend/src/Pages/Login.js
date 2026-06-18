import React, { useState } from 'react';
import api from '../API';
import { useNavigate, Link } from 'react-router-dom';
import Cookies from 'js-cookie';
import './GuestPage.css';
import './SignupLogin.css';


const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null); 


  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      // Create a URLSearchParams object
      const requestBody = new URLSearchParams();
      requestBody.append('grant_type', 'password');
      requestBody.append('username', email);
      requestBody.append('password', password);
  
      const response = await api.post('/login', requestBody, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
  
      const { access_token, refresh_token } = response.data;

      // document.cookie = `access_token=${access_token};`;// Secure; HttpOnly
      // document.cookie = `refresh_token=${refresh_token};`;// Secure; HttpOnly
      Cookies.set("access_token", access_token);
      Cookies.set("refresh_token", refresh_token);
  
      navigate('/home');
    } catch (error) {
      setError('Username or password is incorrect');

      setEmail('');
      setPassword('');

      setTimeout(() => {
        setError(null);
      }, 1000);
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
        <h2>Log in</h2>
        <div className="mb-3">
          <input
            type="text"
            className="form-control"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <input
            type="password"
            className="form-control"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        {error && (
          <div className="alert alert-danger">{error}</div>
        )}
        <button className="btn btn-primary" onClick={handleLogin}>Login</button>
      </div>
    </div>
  );
};

export default Login;