import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import api from '../lib/api';
import toast from 'react-hot-toast';
import { Upload as UploadIcon, FileSpreadsheet, Download, CheckCircle, AlertCircle } from 'lucide-react';

export default function Upload() {
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [history, setHistory] = useState([]);
    const [historyLoaded, setHistoryLoaded] = useState(false);

    const loadHistory = () => {
        api.get('/api/upload/history').then(res => {
            setHistory(res.data);
            setHistoryLoaded(true);
        });
    };

    useState(() => { loadHistory(); }, []);

    const onDrop = useCallback(async (acceptedFiles) => {
        const file = acceptedFiles[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        setUploading(true);
        setResult(null);

        try {
            const res = await api.post('/api/upload/trial-balance', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setResult(res.data);
            if (res.data.status === 'success') {
                toast.success(`Successfully processed ${res.data.entries_processed} entries`);
            } else {
                toast.error('File has validation errors');
            }
            loadHistory();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Upload failed');
            setResult({ status: 'error', validation: { errors: [err.response?.data?.detail || 'Upload failed'] } });
        } finally {
            setUploading(false);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'], 'application/vnd.ms-excel': ['.xls'] },
        maxFiles: 1,
    });

    const downloadTemplate = () => {
        api.get('/api/upload/template', { responseType: 'blob' }).then(res => {
            const url = URL.createObjectURL(res.data);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'trial_balance_template.xlsx';
            a.click();
            URL.revokeObjectURL(url);
            toast.success('Template downloaded');
        });
    };

    return (
        <>
            <div className="page-header">
                <h1>Upload Financial Data</h1>
                <p>Upload your Trial Balance or General Ledger in Excel format</p>
            </div>

            <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
                <button className="btn btn-secondary" onClick={downloadTemplate}>
                    <Download size={16} /> Download Template
                </button>
            </div>

            <div {...getRootProps()} className={`upload-zone ${isDragActive ? 'active' : ''}`}>
                <input {...getInputProps()} />
                {uploading ? (
                    <>
                        <div className="spinner" style={{ margin: '0 auto 12px' }} />
                        <h3>Processing file...</h3>
                        <p>Validating structure, cleaning data, and detecting duplicates</p>
                    </>
                ) : (
                    <>
                        <UploadIcon size={48} />
                        <h3>Drop your Excel file here</h3>
                        <p>or click to browse. Supports .xlsx and .xls files</p>
                        <p style={{ marginTop: 8, fontSize: 12 }}>Trial Balance format: Account Code | Account Name | Debit | Credit</p>
                    </>
                )}
            </div>

            {result && (
                <div className="card" style={{ marginTop: 24 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                        {result.status === 'success' ? (
                            <><CheckCircle size={20} color="var(--success)" /> <h3 style={{ color: 'var(--success)' }}>Upload Successful</h3></>
                        ) : (
                            <><AlertCircle size={20} color="var(--danger)" /> <h3 style={{ color: 'var(--danger)' }}>Validation Issues</h3></>
                        )}
                    </div>

                    {result.entries_processed && (
                        <p style={{ marginBottom: 12, color: 'var(--text-secondary)' }}>
                            ✅ {result.entries_processed} entries processed and saved
                        </p>
                    )}

                    {result.validation?.errors?.length > 0 && (
                        <div style={{ marginBottom: 12 }}>
                            <h4 style={{ color: 'var(--danger)', marginBottom: 6, fontSize: 13 }}>Errors:</h4>
                            {result.validation.errors.map((e, i) => (
                                <div key={i} className="error-message">{e}</div>
                            ))}
                        </div>
                    )}

                    {result.validation?.warnings?.length > 0 && (
                        <div>
                            <h4 style={{ color: 'var(--warning)', marginBottom: 6, fontSize: 13 }}>Warnings:</h4>
                            {result.validation.warnings.map((w, i) => (
                                <p key={i} style={{ fontSize: 13, color: 'var(--warning)', marginBottom: 4 }}>⚠ {w}</p>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {history.length > 0 && (
                <div className="card" style={{ marginTop: 24 }}>
                    <h3 style={{ marginBottom: 16 }}>Upload History</h3>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>File Name</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th className="text-right">Rows</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {history.map((u) => (
                                    <tr key={u.id}>
                                        <td><FileSpreadsheet size={14} style={{ marginRight: 6, verticalAlign: -2 }} />{u.filename}</td>
                                        <td>{u.file_type?.replace('_', ' ')}</td>
                                        <td><span className={`badge badge-${u.status === 'completed' ? 'success' : u.status === 'failed' ? 'danger' : 'warning'}`}>{u.status}</span></td>
                                        <td className="text-right">{u.row_count || '—'}</td>
                                        <td>{u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </>
    );
}
