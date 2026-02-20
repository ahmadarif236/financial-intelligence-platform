import { useState, useEffect } from 'react';
import api from '../lib/api';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { Building2, Save } from 'lucide-react';

export default function CompanyProfile() {
    const { user, updateUser } = useAuth();
    const [form, setForm] = useState({
        name: '', country: 'UAE', industry: '', currency: 'AED',
        fiscal_year_end: 'December', tax_registration: '', address: '',
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [isNew, setIsNew] = useState(false);

    useEffect(() => {
        api.get('/api/company/')
            .then(res => {
                if (res.data) {
                    setForm(res.data);
                    setIsNew(false);
                } else {
                    setIsNew(true);
                }
            })
            .catch(() => setIsNew(true))
            .finally(() => setLoading(false));
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.name) {
            toast.error('Company name is required');
            return;
        }
        setSaving(true);
        try {
            const { id, ...formData } = form;
            const res = isNew
                ? await api.post('/api/company/', formData)
                : await api.put('/api/company/', formData);

            setForm(res.data);
            setIsNew(false);
            toast.success(isNew ? 'Company created!' : 'Company updated!');

            // Update user with company_id
            if (isNew && res.data.id) {
                updateUser({ ...user, company_id: res.data.id });
            }
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to save');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="loading-spinner"><div className="spinner" /></div>;

    return (
        <>
            <div className="page-header">
                <h1>Company Profile</h1>
                <p>{isNew ? 'Set up your company to get started' : 'Manage your company information'}</p>
            </div>

            <div className="card" style={{ maxWidth: 640 }}>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Company Name *</label>
                        <input type="text" placeholder="e.g., Al Futtaim Group"
                            value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                        <div className="form-group">
                            <label>Country</label>
                            <select value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })}>
                                <option value="UAE">UAE</option>
                                <option value="KSA">KSA</option>
                                <option value="Bahrain">Bahrain</option>
                                <option value="Qatar">Qatar</option>
                                <option value="Kuwait">Kuwait</option>
                                <option value="Oman">Oman</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Currency</label>
                            <select value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })}>
                                <option value="AED">AED (UAE Dirham)</option>
                                <option value="SAR">SAR (Saudi Riyal)</option>
                                <option value="BHD">BHD (Bahraini Dinar)</option>
                                <option value="QAR">QAR (Qatari Riyal)</option>
                                <option value="KWD">KWD (Kuwaiti Dinar)</option>
                                <option value="OMR">OMR (Omani Rial)</option>
                                <option value="USD">USD (US Dollar)</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Industry</label>
                        <select value={form.industry || ''} onChange={(e) => setForm({ ...form, industry: e.target.value })}>
                            <option value="">Select industry...</option>
                            <option value="Technology">Technology</option>
                            <option value="Real Estate">Real Estate</option>
                            <option value="Construction">Construction</option>
                            <option value="Retail">Retail</option>
                            <option value="Manufacturing">Manufacturing</option>
                            <option value="Healthcare">Healthcare</option>
                            <option value="Financial Services">Financial Services</option>
                            <option value="Oil & Gas">Oil & Gas</option>
                            <option value="Hospitality">Hospitality</option>
                            <option value="Logistics">Logistics</option>
                            <option value="Education">Education</option>
                            <option value="Professional Services">Professional Services</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                        <div className="form-group">
                            <label>Fiscal Year End</label>
                            <select value={form.fiscal_year_end} onChange={(e) => setForm({ ...form, fiscal_year_end: e.target.value })}>
                                {['January', 'February', 'March', 'April', 'May', 'June',
                                    'July', 'August', 'September', 'October', 'November', 'December'].map(m => (
                                        <option key={m} value={m}>{m}</option>
                                    ))}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Tax Registration Number</label>
                            <input type="text" placeholder="TRN / VAT Number"
                                value={form.tax_registration || ''} onChange={(e) => setForm({ ...form, tax_registration: e.target.value })} />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Address</label>
                        <textarea rows="2" placeholder="Company address"
                            value={form.address || ''} onChange={(e) => setForm({ ...form, address: e.target.value })} />
                    </div>

                    <button className="btn btn-primary btn-full" type="submit" disabled={saving}>
                        <Save size={16} /> {saving ? 'Saving...' : (isNew ? 'Create Company' : 'Update Company')}
                    </button>
                </form>
            </div>
        </>
    );
}
