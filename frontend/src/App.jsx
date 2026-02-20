import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Mapping from './pages/Mapping';
import Statements from './pages/Statements';
import Ratios from './pages/Ratios';
import AICommentary from './pages/AICommentary';
import ExportPage from './pages/ExportPage';
import CompanyProfile from './pages/CompanyProfile';
import './index.css';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading-spinner"><div className="spinner" /></div>;
  if (!user) return <Navigate to="/login" />;
  return children;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Register />} />
      <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="upload" element={<Upload />} />
        <Route path="mapping" element={<Mapping />} />
        <Route path="statements" element={<Statements />} />
        <Route path="ratios" element={<Ratios />} />
        <Route path="ai-commentary" element={<AICommentary />} />
        <Route path="export" element={<ExportPage />} />
        <Route path="company" element={<CompanyProfile />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster position="top-right" toastOptions={{
          style: { background: '#1e1e3a', color: '#f1f5f9', border: '1px solid rgba(255,255,255,0.08)' }
        }} />
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}
