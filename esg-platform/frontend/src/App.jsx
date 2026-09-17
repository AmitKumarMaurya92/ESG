import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './contexts/AuthContext.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import LandingPage from './pages/LandingPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import OnboardingPage from './pages/OnboardingPage.jsx'
import FacilitiesPage from './pages/FacilitiesPage.jsx'
import DocumentsPage from './pages/DocumentsPage.jsx'
import EmissionsPage from './pages/EmissionsPage.jsx'
import ReportsPage from './pages/ReportsPage.jsx'
import SuppliersPage from './pages/SuppliersPage.jsx'
import CompliancePage from './pages/CompliancePage.jsx'
import ChatPage from './pages/ChatPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'
import DashboardLayout from './layouts/DashboardLayout.jsx'

// Create a QueryClient instance — will be reused across all phases
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,  // 5 minutes
      retry: 2,
    },
  },
})

/**
 * Root application component.
 *
 * Phase 1: Landing page route.
 * Phase 2: Supabase integration (backend + frontend services).
 * Phase 3: Authentication (AuthContext, ProtectedRoute, Dashboard).
 */
export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected routes */}
            <Route 
              path="/onboarding" 
              element={
                <ProtectedRoute>
                  <OnboardingPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <DashboardPage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/facilities" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <FacilitiesPage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/documents" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <DocumentsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/emissions" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <EmissionsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/reports" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ReportsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/reports" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ReportsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/suppliers" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <SuppliersPage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/compliance" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <CompliancePage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/assistant" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ChatPage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/assistant" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ChatPage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <SettingsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}
