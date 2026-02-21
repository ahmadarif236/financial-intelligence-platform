import { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
    LayoutDashboard, Upload, GitBranch, FileText, BarChart3,
    Brain, Download, Building2, LogOut, Menu, X
} from 'lucide-react';

const navItems = [
    {
        section: 'Overview', items: [
            { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        ]
    },
    {
        section: 'Data', items: [
            { path: '/dashboard/upload', label: 'Upload Data', icon: Upload },
            { path: '/dashboard/mapping', label: 'Account Mapping', icon: GitBranch },
        ]
    },
    {
        section: 'Analysis', items: [
            { path: '/dashboard/statements', label: 'Financial Statements', icon: FileText },
            { path: '/dashboard/ratios', label: 'Financial Ratios', icon: BarChart3 },
            { path: '/dashboard/ai-commentary', label: 'AI Commentary', icon: Brain },
        ]
    },
    {
        section: 'Reports', items: [
            { path: '/dashboard/export', label: 'Export Reports', icon: Download },
        ]
    },
    {
        section: 'Settings', items: [
            { path: '/dashboard/company', label: 'Company Profile', icon: Building2 },
        ]
    },
];

export default function DashboardLayout() {
    const { user, logout } = useAuth();
    const location = useLocation();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);
    const closeMobileMenu = () => setIsMobileMenuOpen(false);

    return (
        <div className="layout">
            <div className="mobile-header">
                <div className="mobile-logo">
                    <h2>GCC CFO AI</h2>
                </div>
                <button className="mobile-menu-btn" onClick={toggleMobileMenu}>
                    {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {isMobileMenuOpen && (
                <div className="mobile-overlay" onClick={closeMobileMenu}></div>
            )}

            <aside className={`sidebar ${isMobileMenuOpen ? 'open' : ''}`}>
                <div className="sidebar-logo">
                    <h2>GCC CFO AI</h2>
                    <span>Financial Intelligence Platform</span>
                </div>

                <nav className="sidebar-nav">
                    {navItems.map((section) => (
                        <div key={section.section} className="nav-section">
                            <div className="nav-section-title">{section.section}</div>
                            {section.items.map((item) => (
                                <NavLink
                                    key={item.path}
                                    to={item.path}
                                    end={item.path === '/dashboard'}
                                    className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                                    onClick={closeMobileMenu}
                                >
                                    <item.icon />
                                    {item.label}
                                </NavLink>
                            ))}
                        </div>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <div className="user-info">
                        <div className="user-avatar">
                            {user?.full_name?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <div>
                            <div className="user-name">{user?.full_name || 'User'}</div>
                            <div className="user-role">Admin</div>
                        </div>
                    </div>
                    <button className="btn btn-secondary btn-sm btn-full" onClick={logout} style={{ marginTop: 8 }}>
                        <LogOut size={14} />
                        Sign Out
                    </button>
                </div>
            </aside>

            <main className="main-content">
                <Outlet />
            </main>
        </div>
    );
}
