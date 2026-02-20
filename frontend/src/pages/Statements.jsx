import { useState, useEffect } from 'react';
import api from '../lib/api';

export default function Statements() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('pnl');

    useEffect(() => {
        api.get('/statements/all')
            .then(res => setData(res.data))
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="loading-spinner"><div className="spinner" /></div>;

    if (!data) return (
        <div className="card" style={{ textAlign: 'center', padding: 48 }}>
            <h3>No Financial Data</h3>
            <p style={{ color: 'var(--text-secondary)', marginTop: 8 }}>Upload and map your accounts to generate statements</p>
        </div>
    );

    const renderStatement = (statement) => {
        if (!statement) return null;
        return (
            <div className="card">
                <h2 style={{ marginBottom: 20, fontSize: 20 }}>{statement.title}</h2>
                {statement.sections.map((section, idx) => (
                    <div key={idx} className="statement-section">
                        {section.is_subtotal ? (
                            <div className="statement-subtotal">
                                <span>{section.name}</span>
                                <span>{section.total?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                            </div>
                        ) : (
                            <>
                                <div className="statement-section-header">
                                    <span>{section.name}</span>
                                    <span>{section.total?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                                </div>
                                {section.items?.map((item, iIdx) => (
                                    <div key={iIdx} className="statement-item">
                                        <span>{item.line}</span>
                                        <span>{item.amount?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                                    </div>
                                ))}
                            </>
                        )}
                    </div>
                ))}
            </div>
        );
    };

    return (
        <>
            <div className="page-header">
                <h1>Financial Statements</h1>
                <p>IFRS-compliant financial statements generated from your data</p>
            </div>

            <div className="tabs">
                <button className={`tab ${activeTab === 'pnl' ? 'active' : ''}`} onClick={() => setActiveTab('pnl')}>
                    Profit & Loss
                </button>
                <button className={`tab ${activeTab === 'bs' ? 'active' : ''}`} onClick={() => setActiveTab('bs')}>
                    Balance Sheet
                </button>
                <button className={`tab ${activeTab === 'cf' ? 'active' : ''}`} onClick={() => setActiveTab('cf')}>
                    Cash Flow
                </button>
            </div>

            {activeTab === 'pnl' && renderStatement(data.profit_loss)}
            {activeTab === 'bs' && renderStatement(data.balance_sheet)}
            {activeTab === 'cf' && renderStatement(data.cash_flow)}
        </>
    );
}
