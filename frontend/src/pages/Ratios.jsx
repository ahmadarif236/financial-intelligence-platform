import { useState, useEffect } from 'react';
import api from '../lib/api';
import { Bar, Doughnut, Radar } from 'react-chartjs-2';
import {
    Chart as ChartJS, CategoryScale, LinearScale, BarElement,
    Title, Tooltip, Legend, ArcElement, RadialLinearScale, PointElement, LineElement, Filler
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, RadialLinearScale, PointElement, LineElement, Filler);

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } },
    },
    scales: {
        x: { ticks: { color: '#64748b', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
        y: { ticks: { color: '#64748b', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
    },
};

export default function Ratios() {
    const [ratios, setRatios] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/ratios/')
            .then(res => setRatios(res.data))
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="loading-spinner"><div className="spinner" /></div>;
    if (!ratios) return <div className="card" style={{ textAlign: 'center', padding: 48 }}><h3>No ratio data available</h3></div>;

    // Prepare chart data for profitability
    const profitRatios = ratios.profitability?.ratios || [];
    const profitChartData = {
        labels: profitRatios.map(r => r.name),
        datasets: [{
            label: 'Value (%)',
            data: profitRatios.map(r => r.value),
            backgroundColor: profitRatios.map(r =>
                r.status === 'good' ? 'rgba(16, 185, 129, 0.7)' :
                    r.status === 'warning' ? 'rgba(245, 158, 11, 0.7)' : 'rgba(239, 68, 68, 0.7)'
            ),
            borderRadius: 6,
        }],
    };

    // Liquidity chart
    const liqRatios = ratios.liquidity?.ratios || [];
    const liqChartData = {
        labels: liqRatios.map(r => r.name),
        datasets: [{
            data: liqRatios.map(r => r.value),
            backgroundColor: ['rgba(99, 102, 241, 0.7)', 'rgba(139, 92, 246, 0.7)', 'rgba(167, 139, 250, 0.7)'],
            borderColor: ['#6366f1', '#8b5cf6', '#a78bfa'],
            borderWidth: 2,
        }],
    };

    return (
        <>
            <div className="page-header">
                <h1>Financial Ratios</h1>
                <p>Comprehensive financial health analysis with benchmark comparisons</p>
            </div>

            {/* Charts Row */}
            <div className="grid-2" style={{ marginBottom: 24 }}>
                <div className="chart-container">
                    <h3>Profitability Ratios</h3>
                    <div style={{ height: 280 }}>
                        <Bar data={profitChartData} options={{ ...chartOptions, plugins: { ...chartOptions.plugins, legend: { display: false } } }} />
                    </div>
                </div>
                <div className="chart-container">
                    <h3>Liquidity Ratios</h3>
                    <div style={{ height: 280, display: 'flex', justifyContent: 'center' }}>
                        <Doughnut data={liqChartData} options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Inter' } } } },
                            cutout: '60%',
                        }} />
                    </div>
                </div>
            </div>

            {/* Ratio Cards */}
            <div className="ratio-grid">
                {Object.entries(ratios).map(([key, category]) => (
                    <div key={key} className="ratio-category">
                        <h3>{category.title}</h3>
                        {category.ratios.map((r, idx) => (
                            <div key={idx} className="ratio-item">
                                <div>
                                    <div className="ratio-name">{r.name}</div>
                                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                                        Benchmark: {r.benchmark}
                                    </div>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center' }}>
                                    <span className="ratio-value">{r.value}{r.unit || 'x'}</span>
                                    <span className={`ratio-status status-${r.status}`} />
                                </div>
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </>
    );
}
