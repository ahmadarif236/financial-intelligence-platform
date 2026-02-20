import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../lib/api';
import { TrendingUp, TrendingDown, DollarSign, BarChart3, Wallet, ArrowUpRight, Building2 } from 'lucide-react';

export default function Dashboard() {
    const { user } = useAuth();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/dashboard/')
            .then(res => setData(res.data))
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="loading-spinner"><div className="spinner" /></div>;

    const kpis = data?.kpis || {};
    const company = data?.company;
    const hasData = data?.has_data;

    const formatCurrency = (val) => {
        if (!val && val !== 0) return '—';
        if (Math.abs(val) >= 1000000) return `${(val / 1000000).toFixed(1)}M`;
        if (Math.abs(val) >= 1000) return `${(val / 1000).toFixed(1)}K`;
        return val.toLocaleString();
    };

    return (
        <>
            <div className="page-header">
                <h1>CFO Dashboard</h1>
                <p>{company ? `${company.name} · ${company.country} · ${company.currency}` : 'Welcome to GCC CFO AI'}</p>
            </div>

            {!hasData ? (
                <div className="welcome-card">
                    <h2>👋 Welcome, {user?.full_name}!</h2>
                    <p>Get started by setting up your company profile and uploading your financial data.</p>
                    <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
                        {!company && (
                            <Link to="/dashboard/company" className="btn btn-primary">
                                <Building2 size={16} /> Set Up Company
                            </Link>
                        )}
                        <Link to="/dashboard/upload" className="btn btn-secondary">
                            <ArrowUpRight size={16} /> Upload Data
                        </Link>
                    </div>
                </div>
            ) : (
                <>
                    <div className="kpi-grid">
                        <div className="kpi-card">
                            <div className="kpi-label">Revenue</div>
                            <div className="kpi-value">{formatCurrency(kpis.revenue)}<span className="kpi-unit">{company?.currency}</span></div>
                        </div>
                        <div className="kpi-card">
                            <div className="kpi-label">EBITDA</div>
                            <div className="kpi-value">{formatCurrency(kpis.ebitda)}<span className="kpi-unit">{company?.currency}</span></div>
                        </div>
                        <div className="kpi-card">
                            <div className="kpi-label">Net Profit</div>
                            <div className="kpi-value" style={{ color: kpis.net_profit >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                                {formatCurrency(kpis.net_profit)}<span className="kpi-unit">{company?.currency}</span>
                            </div>
                        </div>
                        <div className="kpi-card">
                            <div className="kpi-label">Cash Position</div>
                            <div className="kpi-value">{formatCurrency(kpis.cash_position)}<span className="kpi-unit">{company?.currency}</span></div>
                        </div>
                        <div className="kpi-card">
                            <div className="kpi-label">Net Debt</div>
                            <div className="kpi-value">{formatCurrency(kpis.net_debt)}<span className="kpi-unit">{company?.currency}</span></div>
                        </div>
                        <div className="kpi-card">
                            <div className="kpi-label">Working Capital</div>
                            <div className="kpi-value" style={{ color: kpis.working_capital >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                                {formatCurrency(kpis.working_capital)}<span className="kpi-unit">{company?.currency}</span>
                            </div>
                        </div>
                        <div className="kpi-card">
                            <div className="kpi-label">Gross Margin</div>
                            <div className="kpi-value">{kpis.gross_margin || 0}<span className="kpi-unit">%</span></div>
                        </div>
                        <div className="kpi-card">
                            <div className="kpi-label">Net Margin</div>
                            <div className="kpi-value">{kpis.net_margin || 0}<span className="kpi-unit">%</span></div>
                        </div>
                    </div>

                    <div className="grid-3" style={{ marginTop: 24 }}>
                        <Link to="/dashboard/statements" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
                            <h3 style={{ marginBottom: 8 }}>📊 Financial Statements</h3>
                            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>View P&L, Balance Sheet, and Cash Flow</p>
                        </Link>
                        <Link to="/dashboard/ratios" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
                            <h3 style={{ marginBottom: 8 }}>📈 Financial Ratios</h3>
                            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Liquidity, Profitability, Leverage analysis</p>
                        </Link>
                        <Link to="/dashboard/ai-commentary" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
                            <h3 style={{ marginBottom: 8 }}>🤖 AI Commentary</h3>
                            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Board-level financial insights</p>
                        </Link>
                    </div>
                </>
            )}
        </>
    );
}
