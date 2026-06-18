import './App.css';
import React, {useState, useEffect} from 'react';
import api from './API';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Cookies from 'js-cookie';
import Login from './Pages/Login';
import Home from './Pages/Home'; 
import Signup from './Pages/Signup';
import GuestPage from './Pages/GuestPage';
import ProtectedRoute from './Components/ProtectedRoute';
import VeifyEmail from './Pages/VerifyPage';
import Verification from './Pages/VerificationPage';

const App = () => {
  
  // Function to refresh the access token
  const refreshAccessToken = async () => {
    try {
      const refreshToken = Cookies.get('refresh_token');
      const response = await api.post('/refresh', { refresh_token: refreshToken });

      if (response.data && response.data.access_token) {
        Cookies.set('access_token', response.data.access_token);
      }
    } catch (error) {
      console.error('Failed to refresh access token', error);
    }
  };

  useEffect(() => {
    // Check if the access token is present, if not, try to refresh it
    const accessToken = Cookies.get('access_token');
    if (!accessToken) {
      refreshAccessToken();
    }
  }, []);
  
  return (
    <Router>
      <Routes>
        <Route path="/" element={<GuestPage />} />
        <Route path="/verify" element={<VeifyEmail/>}/>
        <Route path="/verification" element={<Verification/>}/>
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        <Route path="/home" element={<ProtectedRoute element={<Home />} />} />
      </Routes>
    </Router>
  );
};

export default App;
