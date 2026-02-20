import { useState, useEffect } from 'react';
import api from '../lib/api';
import toast from 'react-hot-toast';
import { GitBranch, Check, AlertTriangle, RefreshCw } from 'lucide-react';

export default function Mapping() {
    const [mappings, setMappings] = useState([]);
    const [masterAccounts, setMasterAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [autoMapping, setAutoMapping] = useState(false);
    const [filter, setFilter] = useState('all'); // all, mapped, unmapped

    useEffect(() => { loadData(); }, []);

    const loadData = async () => {
        try {
            const [mRes, maRes] = await Promise.all([
                api.get('/mapping/'),
                api.get('/mapping/master-accounts'),
            ]);
            setMappings(mRes.data);
            setMasterAccounts(maRes.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const runAutoMap = async () => {
        setAutoMapping(true);
        try {
            const res = await api.post('/mapping/auto-map');
            toast.success(`Auto-mapped ${res.data.mapped} of ${res.data.total} accounts`);
            loadData();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Auto-mapping failed');
        } finally {
            setAutoMapping(false);
        }
    };

    const manualMap = async (mappingId, masterAccountId) => {
        try {
            await api.post('/mapping/manual-map', {
                mapping_id: mappingId,
                master_account_id: parseInt(masterAccountId),
            });
            toast.success('Account mapped successfully');
            loadData();
        } catch (err) {
            toast.error('Mapping failed');
        }
    };

    const filtered = mappings.filter(m => {
        if (filter === 'mapped') return m.is_mapped;
        if (filter === 'unmapped') return !m.is_mapped;
        return true;
    });

    const mappedCount = mappings.filter(m => m.is_mapped).length;
    const unmappedCount = mappings.filter(m => !m.is_mapped).length;

    if (loading) return <div className="loading-spinner"><div className="spinner" /></div>;

    return (
        <>
            <div className="page-header">
                <h1>Chart of Accounts Mapping</h1>
                <p>Map your accounts to IFRS-standard chart of accounts</p>
            </div>

            <div style={{ display: 'flex', gap: 12, marginBottom: 24, alignItems: 'center', flexWrap: 'wrap' }}>
                <button className="btn btn-primary" onClick={runAutoMap} disabled={autoMapping}>
                    <RefreshCw size={16} className={autoMapping ? 'spin' : ''} />
                    {autoMapping ? 'Auto-mapping...' : 'Run Auto-Mapping'}
                </button>

                <div style={{ display: 'flex', gap: 8 }}>
                    <span className="badge badge-success">✓ {mappedCount} Mapped</span>
                    <span className="badge badge-warning">⚠ {unmappedCount} Unmapped</span>
                </div>

                <div className="tabs" style={{ marginBottom: 0, marginLeft: 'auto' }}>
                    <button className={`tab ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>All ({mappings.length})</button>
                    <button className={`tab ${filter === 'mapped' ? 'active' : ''}`} onClick={() => setFilter('mapped')}>Mapped ({mappedCount})</button>
                    <button className={`tab ${filter === 'unmapped' ? 'active' : ''}`} onClick={() => setFilter('unmapped')}>Unmapped ({unmappedCount})</button>
                </div>
            </div>

            {mappings.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: 48 }}>
                    <GitBranch size={48} style={{ color: 'var(--text-muted)', marginBottom: 16 }} />
                    <h3>No Accounts Found</h3>
                    <p style={{ color: 'var(--text-secondary)', marginTop: 8 }}>Upload a Trial Balance first to map accounts</p>
                </div>
            ) : (
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Source Code</th>
                                <th>Source Name</th>
                                <th>Source Type</th>
                                <th>Status</th>
                                <th>Mapped To (IFRS)</th>
                                <th>By</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map((m) => (
                                <tr key={m.id}>
                                    <td style={{ fontFamily: 'monospace', fontWeight: 600 }}>{m.source_code}</td>
                                    <td>{m.source_name}</td>
                                    <td><span className="badge badge-info">{m.source_type || '—'}</span></td>
                                    <td>
                                        {m.is_mapped ? (
                                            <span className="badge badge-success"><Check size={12} /> Mapped</span>
                                        ) : (
                                            <span className="badge badge-warning"><AlertTriangle size={12} /> Unmapped</span>
                                        )}
                                    </td>
                                    <td>
                                        {m.is_mapped ? (
                                            <span style={{ fontSize: 13 }}>{m.master_code} – {m.master_name}</span>
                                        ) : (
                                            <select
                                                className="mapping-select"
                                                defaultValue=""
                                                onChange={(e) => manualMap(m.id, e.target.value)}
                                            >
                                                <option value="" disabled>Select IFRS account...</option>
                                                {masterAccounts.map((ma) => (
                                                    <option key={ma.id} value={ma.id}>
                                                        {ma.code} – {ma.name} ({ma.category})
                                                    </option>
                                                ))}
                                            </select>
                                        )}
                                    </td>
                                    <td><span className="badge badge-info">{m.mapped_by || '—'}</span></td>
                                    <td>
                                        {m.is_mapped && (
                                            <select
                                                className="mapping-select"
                                                value={masterAccounts.find(ma => ma.code === m.master_code)?.id || ''}
                                                onChange={(e) => manualMap(m.id, e.target.value)}
                                                style={{ minWidth: 160 }}
                                            >
                                                {masterAccounts.map((ma) => (
                                                    <option key={ma.id} value={ma.id}>
                                                        {ma.code} – {ma.name}
                                                    </option>
                                                ))}
                                            </select>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </>
    );
}
