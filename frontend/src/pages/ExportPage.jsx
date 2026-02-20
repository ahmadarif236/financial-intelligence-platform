import { useState } from 'react';
import api from '../lib/api';
import toast from 'react-hot-toast';
import { FileText, FileSpreadsheet, Download } from 'lucide-react';

export default function ExportPage() {
    const [exporting, setExporting] = useState(null);

    const exportPDF = async () => {
        setExporting('pdf');
        try {
            const res = await api.get('/export/pdf', { responseType: 'blob' });
            const url = URL.createObjectURL(res.data);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Financial_Report.pdf';
            a.click();
            URL.revokeObjectURL(url);
            toast.success('PDF report downloaded');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to export PDF');
        } finally {
            setExporting(null);
        }
    };

    const exportExcel = async () => {
        setExporting('excel');
        try {
            const res = await api.get('/export/excel', { responseType: 'blob' });
            const url = URL.createObjectURL(res.data);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Financial_Report.xlsx';
            a.click();
            URL.revokeObjectURL(url);
            toast.success('Excel report downloaded');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to export Excel');
        } finally {
            setExporting(null);
        }
    };

    return (
        <>
            <div className="page-header">
                <h1>Export Reports</h1>
                <p>Generate and download board-ready financial reports</p>
            </div>

            <div className="export-options">
                <div className="export-card" onClick={exportPDF} style={{ opacity: exporting === 'pdf' ? 0.6 : 1 }}>
                    {exporting === 'pdf' ? <div className="spinner" style={{ margin: '0 auto 16px' }} /> : <FileText size={48} />}
                    <h3>PDF Report</h3>
                    <p>Board-ready PDF with financial statements, ratios, charts, and AI commentary</p>
                    <button className="btn btn-primary btn-sm" style={{ marginTop: 16 }} disabled={!!exporting}>
                        <Download size={14} /> {exporting === 'pdf' ? 'Generating...' : 'Download PDF'}
                    </button>
                </div>

                <div className="export-card" onClick={exportExcel} style={{ opacity: exporting === 'excel' ? 0.6 : 1 }}>
                    {exporting === 'excel' ? <div className="spinner" style={{ margin: '0 auto 16px' }} /> : <FileSpreadsheet size={48} />}
                    <h3>Excel Report</h3>
                    <p>Structured Excel workbook with P&L, Balance Sheet, and Financial Ratios</p>
                    <button className="btn btn-success btn-sm" style={{ marginTop: 16 }} disabled={!!exporting}>
                        <Download size={14} /> {exporting === 'excel' ? 'Generating...' : 'Download Excel'}
                    </button>
                </div>
            </div>

            <div className="card" style={{ marginTop: 32 }}>
                <h3 style={{ marginBottom: 12 }}>Report Contents</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                    <div>
                        <h4 style={{ fontSize: 13, color: 'var(--accent-primary)', marginBottom: 8 }}>Financial Statements</h4>
                        <ul style={{ listStyle: 'none', padding: 0 }}>
                            <li style={{ padding: '4px 0', fontSize: 13, color: 'var(--text-secondary)' }}>✓ Profit & Loss Statement</li>
                            <li style={{ padding: '4px 0', fontSize: 13, color: 'var(--text-secondary)' }}>✓ Balance Sheet</li>
                            <li style={{ padding: '4px 0', fontSize: 13, color: 'var(--text-secondary)' }}>✓ Cash Flow Statement</li>
                        </ul>
                    </div>
                    <div>
                        <h4 style={{ fontSize: 13, color: 'var(--accent-primary)', marginBottom: 8 }}>Analysis & Commentary</h4>
                        <ul style={{ listStyle: 'none', padding: 0 }}>
                            <li style={{ padding: '4px 0', fontSize: 13, color: 'var(--text-secondary)' }}>✓ Financial Ratios & Benchmarks</li>
                            <li style={{ padding: '4px 0', fontSize: 13, color: 'var(--text-secondary)' }}>✓ AI CFO Commentary</li>
                            <li style={{ padding: '4px 0', fontSize: 13, color: 'var(--text-secondary)' }}>✓ Risk Flags & Warnings</li>
                        </ul>
                    </div>
                </div>
            </div>
        </>
    );
}
