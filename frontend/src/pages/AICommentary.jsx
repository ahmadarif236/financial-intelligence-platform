import { useState, useEffect } from 'react';
import api from '../lib/api';
import { Brain, AlertTriangle, Lightbulb, Shield, RefreshCw } from 'lucide-react';

export default function AICommentary() {
    const [commentary, setCommentary] = useState(null);
    const [loading, setLoading] = useState(true);

    const loadCommentary = () => {
        setLoading(true);
        api.get('/api/ai/commentary')
            .then(res => setCommentary(res.data))
            .catch(() => { })
            .finally(() => setLoading(false));
    };

    useEffect(() => { loadCommentary(); }, []);

    if (loading) return (
        <div style={{ textAlign: 'center', padding: 60 }}>
            <div className="spinner" style={{ margin: '0 auto 16px' }} />
            <h3>Generating AI Analysis...</h3>
            <p style={{ color: 'var(--text-secondary)', marginTop: 8 }}>Our AI is analyzing your financial data</p>
        </div>
    );

    if (!commentary) return (
        <div className="card" style={{ textAlign: 'center', padding: 48 }}>
            <Brain size={48} style={{ color: 'var(--text-muted)', marginBottom: 16 }} />
            <h3>No Commentary Available</h3>
            <p style={{ color: 'var(--text-secondary)', marginTop: 8 }}>Upload and map financial data to generate AI commentary</p>
        </div>
    );

    const healthClass = commentary.overall_health === 'good' ? 'health-good' :
        commentary.overall_health === 'warning' ? 'health-warning' : 'health-critical';

    return (
        <>
            <div className="page-header">
                <h1>AI CFO Commentary</h1>
                <p>Board-level financial analysis powered by artificial intelligence</p>
            </div>

            <div style={{ display: 'flex', gap: 12, marginBottom: 24, alignItems: 'center' }}>
                <div className={`health-overall ${healthClass}`}>
                    <Shield size={14} />
                    Financial Health: {commentary.overall_health?.toUpperCase()}
                </div>
                <button className="btn btn-secondary btn-sm" onClick={loadCommentary} style={{ marginLeft: 'auto' }}>
                    <RefreshCw size={14} /> Regenerate
                </button>
            </div>

            {/* Executive Summary */}
            <div className="card commentary-section">
                <h3>📋 Executive Summary</h3>
                <div className="commentary-text" style={{ whiteSpace: 'pre-wrap' }}>
                    {commentary.executive_summary}
                </div>
            </div>

            <div className="grid-2">
                {/* Revenue Analysis */}
                <div className="card commentary-section">
                    <h3>📊 Revenue & Margin Analysis</h3>
                    <div className="commentary-text">{commentary.revenue_analysis}</div>
                </div>

                {/* Cash Flow */}
                <div className="card commentary-section">
                    <h3>💰 Cash Flow Analysis</h3>
                    <div className="commentary-text">{commentary.cash_flow_analysis}</div>
                </div>
            </div>

            {/* Working Capital */}
            <div className="card commentary-section" style={{ marginTop: 24 }}>
                <h3>⚙️ Working Capital Commentary</h3>
                <div className="commentary-text">{commentary.working_capital_commentary}</div>
            </div>

            <div className="grid-2" style={{ marginTop: 24 }}>
                {/* Risk Flags */}
                <div className="card commentary-section">
                    <h3>🚩 Risk Flags</h3>
                    <ul className="commentary-flags">
                        {commentary.risk_flags?.map((flag, i) => (
                            <li key={i}><AlertTriangle size={14} style={{ marginRight: 8, verticalAlign: -2 }} />{flag}</li>
                        ))}
                    </ul>
                </div>

                {/* Covenant Warnings */}
                <div className="card commentary-section">
                    <h3>⚠️ Covenant Warnings</h3>
                    <ul className="commentary-flags">
                        {commentary.covenant_warnings?.map((w, i) => (
                            <li key={i} style={{ borderLeftColor: 'var(--warning)', background: 'rgba(245, 158, 11, 0.06)' }}>
                                {w}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Strategic Observations */}
            <div className="card commentary-section" style={{ marginTop: 24 }}>
                <h3>💡 Strategic Observations</h3>
                <ul className="commentary-flags commentary-observations">
                    {commentary.strategic_observations?.map((obs, i) => (
                        <li key={i}><Lightbulb size={14} style={{ marginRight: 8, verticalAlign: -2 }} />{obs}</li>
                    ))}
                </ul>
            </div>
        </>
    );
}
