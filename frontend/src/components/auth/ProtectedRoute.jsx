import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../../auth/authUtils';

/**
 * Wraps a route so that only authenticated users can access it.
 * Unauthenticated visitors are redirected to /login.
 */
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default ProtectedRoute;
