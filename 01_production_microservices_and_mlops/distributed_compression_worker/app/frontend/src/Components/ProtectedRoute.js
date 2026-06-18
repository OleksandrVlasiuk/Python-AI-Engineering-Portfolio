import React from 'react';
import { Navigate } from 'react-router-dom';
import Cookies from 'js-cookie';

const ProtectedRoute = ({ element, ...rest }) => {
  const isAuth = Cookies.get('access_token') ? true : false;

  return isAuth ? element : <Navigate to="/login" replace />;
};

export default ProtectedRoute;