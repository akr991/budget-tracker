import { useEffect, useMemo, useState } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from 'chart.js';
import { api } from '../api/client';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function NetWorthDashboard() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    api.get('/net-worth/summary').then((response) => setSummary(response.data));
  }, []);

  const chartData = useMemo(() => {
    if (!summary) return null;
    return {
      labels: summary.breakdown_chart.map((item) => item.name),
      datasets: [{
        label: 'Net Worth Split',
        data: summary.breakdown_chart.map((item) => item.value),
        backgroundColor: ['#00b894', '#00a8ff']
      }]
    };
  }, [summary]);

  if (!summary) return <div className="panel">Loading net worth summary...</div>;

  return (
    <div className="region-grid">
      <section className="panel">
        <h2>Total Net Worth</h2>
        <h3>{summary.total_net_worth.toFixed(2)}</h3>
        <p>Monthly Net Worth Change: {summary.monthly_change.toFixed(2)}</p>
        {chartData && <Doughnut data={chartData} />}
      </section>

      <section className="panel emi-summary-panel">
        <h2>Monthly EMI Summary</h2>
        <div className="emi-summary-grid">
          <div className="emi-summary-card">
            <div className="emi-summary-title-row">
              <h3>INDIA</h3>
              {summary.monthly_emi_summary?.india?.all_completed && <span className="emi-summary-tick">✓</span>}
            </div>
            <p>Month: {summary.monthly_emi_summary?.india?.month}</p>
            <p>Total EMIs Paid: {summary.monthly_emi_summary?.india?.total_emis_paid_count ?? 0}</p>
            <p>Total EMIs Remaining: {summary.monthly_emi_summary?.india?.total_emis_remaining_count ?? 0}</p>
            <p>Total EMI Amount Paid: {Number(summary.monthly_emi_summary?.india?.total_emi_amount_paid ?? 0).toFixed(2)}</p>
            <p>Total EMI Amount Remaining: {Number(summary.monthly_emi_summary?.india?.total_emi_amount_remaining ?? 0).toFixed(2)}</p>
          </div>

          <div className="emi-summary-card">
            <div className="emi-summary-title-row">
              <h3>UAE</h3>
              {summary.monthly_emi_summary?.uae?.all_completed && <span className="emi-summary-tick">✓</span>}
            </div>
            <p>Month: {summary.monthly_emi_summary?.uae?.month}</p>
            <p>Total EMIs Paid: {summary.monthly_emi_summary?.uae?.total_emis_paid_count ?? 0}</p>
            <p>Total EMIs Remaining: {summary.monthly_emi_summary?.uae?.total_emis_remaining_count ?? 0}</p>
            <p>Total EMI Amount Paid: {Number(summary.monthly_emi_summary?.uae?.total_emi_amount_paid ?? 0).toFixed(2)}</p>
            <p>Total EMI Amount Remaining: {Number(summary.monthly_emi_summary?.uae?.total_emi_amount_remaining ?? 0).toFixed(2)}</p>
          </div>
        </div>
      </section>

      <section className="panel">
        <h2>India Breakdown</h2>
        <p>Income: {summary.india.income}</p>
        <p>Expenses: {summary.india.expenses}</p>
        <p>Loans: {summary.india.loan_outstanding}</p>
        <p>Debts: {summary.india.debt_outstanding}</p>
        <p>Investments: {summary.india.investments_value}</p>
        <p>Gold: {summary.india.gold_value}</p>
        <p>Net Worth: {summary.india.net_worth}</p>
      </section>

      <section className="panel">
        <h2>UAE Breakdown</h2>
        <p>Income: {summary.uae.income}</p>
        <p>Expenses: {summary.uae.expenses}</p>
        <p>Loans: {summary.uae.loan_outstanding}</p>
        <p>Debts: {summary.uae.debt_outstanding}</p>
        <p>Investments: {summary.uae.investments_value}</p>
        <p>Gold: {summary.uae.gold_value}</p>
        <p>Net Worth: {summary.uae.net_worth}</p>
      </section>
    </div>
  );
}
