import { useEffect, useMemo, useRef, useState } from 'react';
import { Bar, Line } from 'react-chartjs-2';
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  BarElement,
  PointElement,
  Tooltip
} from 'chart.js';
import { api } from '../api/client';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend, Filler);

const incomeCategories = ['salary', 'business', 'rental', 'other'];
const investmentTypes = ['mutual_fund', 'stocks', 'sip', 'fd', 'nps', 'crypto', 'other'];
const goldUnits = ['grams', 'sovereigns'];

const moduleConfig = [
  { id: 'income', title: 'Income Tracking' },
  { id: 'expense', title: 'Expenses & Cash Flow' },
  { id: 'loan', title: 'Loan and EMI Tracking' },
  { id: 'subscription', title: 'Subscriptions' },
  { id: 'debt', title: 'Debt Tracking' },
  { id: 'investment', title: 'Investments' },
  { id: 'gold', title: 'Gold Tracking' }
];

const moduleTitleMap = Object.fromEntries(moduleConfig.map((module) => [module.id, module.title]));

export default function RegionDashboard({ region }) {
  const [incomes, setIncomes] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [loans, setLoans] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [debts, setDebts] = useState([]);
  const [investments, setInvestments] = useState([]);
  const [gold, setGold] = useState([]);
  const [incomeTrend, setIncomeTrend] = useState([]);
  const [investmentTrend, setInvestmentTrend] = useState([]);
  const [loanAlerts, setLoanAlerts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [goldLivePrice, setGoldLivePrice] = useState(null);
  const [activeModule, setActiveModule] = useState(null);
  const [moduleStage, setModuleStage] = useState('idle');
  const [selectedLoanId, setSelectedLoanId] = useState(null);
  const [loanDetails, setLoanDetails] = useState(null);
  const [loanDetailsLoading, setLoanDetailsLoading] = useState(false);
  const [loanActionMessage, setLoanActionMessage] = useState('');
  const [selectedSubscriptionId, setSelectedSubscriptionId] = useState(null);
  const [subscriptionDetails, setSubscriptionDetails] = useState(null);
  const [subscriptionDetailsLoading, setSubscriptionDetailsLoading] = useState(false);
  const [subscriptionActionMessage, setSubscriptionActionMessage] = useState('');

  const [incomeForm, setIncomeForm] = useState({ category: 'salary', amount: '', entry_date: new Date().toISOString().slice(0, 10), notes: '' });
  const [expenseForm, setExpenseForm] = useState({ category: 'household', amount: '', entry_date: new Date().toISOString().slice(0, 10), notes: '' });
  const [loanForm, setLoanForm] = useState({ loan_name: '', emi_amount: '', emi_date: '', remaining_months: '', interest_rate: '', start_date: new Date().toISOString().slice(0, 10) });
  const [subscriptionForm, setSubscriptionForm] = useState({ subscription_name: '', monthly_cost: '', billing_date: '', category: '', notes: '' });
  const [debtForm, setDebtForm] = useState({ lender_name: '', amount: '', due_date: new Date().toISOString().slice(0, 10), notes: '' });
  const [investmentForm, setInvestmentForm] = useState({ name: '', investment_type: 'mutual_fund', invested_value: '', current_value: '', entry_date: new Date().toISOString().slice(0, 10) });
  const [goldForm, setGoldForm] = useState({ quantity: '', unit: 'grams', price_per_gram: '', entry_date: new Date().toISOString().slice(0, 10) });
  const [repayments, setRepayments] = useState({});
  const moduleTimeoutRef = useRef(null);

  const loadAll = async () => {
    const [incomeRes, expenseRes, loanRes, subscriptionRes, debtRes, investmentRes, goldRes, incomeTrendRes, investmentTrendRes, alertRes, summaryRes] = await Promise.all([
      api.get(`/regions/${region}/incomes`),
      api.get(`/regions/${region}/expenses`),
      api.get(`/regions/${region}/loans`),
      api.get(`/regions/${region}/subscriptions`),
      api.get(`/regions/${region}/debts`),
      api.get(`/regions/${region}/investments`),
      api.get(`/regions/${region}/gold`),
      api.get(`/regions/${region}/incomes/summary/monthly`),
      api.get(`/regions/${region}/investments/trends`),
      api.get(`/regions/${region}/loans/alerts`),
      api.get(`/regions/${region}/monthly-summary`)
    ]);

    setIncomes(incomeRes.data);
    setExpenses(expenseRes.data);
    setLoans(loanRes.data);
    setSubscriptions(subscriptionRes.data);
    setDebts(debtRes.data);
    setInvestments(investmentRes.data);
    setGold(goldRes.data);
    setIncomeTrend(incomeTrendRes.data);
    setInvestmentTrend(investmentTrendRes.data);
    setLoanAlerts(alertRes.data);
    setSummary(summaryRes.data);
  };

  useEffect(() => {
    loadAll();
    setActiveModule(null);
    setModuleStage('idle');
    setSelectedLoanId(null);
    setLoanDetails(null);
    setLoanActionMessage('');
    setSelectedSubscriptionId(null);
    setSubscriptionDetails(null);
    setSubscriptionActionMessage('');
  }, [region]);

  useEffect(() => () => {
    if (moduleTimeoutRef.current) {
      clearTimeout(moduleTimeoutRef.current);
    }
  }, []);

  const openModule = (moduleId) => {
    if (moduleId === activeModule) {
      return;
    }

    setModuleStage('exit');
    if (moduleTimeoutRef.current) {
      clearTimeout(moduleTimeoutRef.current);
    }

    moduleTimeoutRef.current = window.setTimeout(() => {
      setActiveModule(moduleId);
      setModuleStage('enter');
      moduleTimeoutRef.current = window.setTimeout(() => {
        setModuleStage('idle');
      }, 220);
    }, 190);
  };

  const closeModule = () => {
    setModuleStage('exit');
    if (moduleTimeoutRef.current) {
      clearTimeout(moduleTimeoutRef.current);
    }

    moduleTimeoutRef.current = window.setTimeout(() => {
      setActiveModule(null);
      setSelectedLoanId(null);
      setLoanDetails(null);
      setLoanActionMessage('');
      setSelectedSubscriptionId(null);
      setSubscriptionDetails(null);
      setSubscriptionActionMessage('');
      setModuleStage('enter');
      moduleTimeoutRef.current = window.setTimeout(() => {
        setModuleStage('idle');
      }, 220);
    }, 190);
  };

  const loadLoanDetails = async (loanId) => {
    setLoanDetailsLoading(true);
    try {
      const detailsRes = await api.get(`/regions/${region}/loans/${loanId}/details`);
      setLoanDetails(detailsRes.data);
    } finally {
      setLoanDetailsLoading(false);
    }
  };

  const openLoanDetails = async (loanId) => {
    setSelectedLoanId(loanId);
    setLoanActionMessage('');
    await loadLoanDetails(loanId);
  };

  const markEmiCompleted = async () => {
    if (!selectedLoanId) return;
    try {
      const response = await api.post(`/regions/${region}/loans/${selectedLoanId}/mark-emi-completed`);
      setLoanActionMessage(`EMI marked completed for ${response.data.month_name} ${response.data.year}.`);
      await loadAll();
      await loadLoanDetails(selectedLoanId);
    } catch (err) {
      setLoanActionMessage(err.response?.data?.detail || 'Unable to mark EMI completed');
    }
  };

  const loadSubscriptionDetails = async (subscriptionId) => {
    setSubscriptionDetailsLoading(true);
    try {
      const [detailsRes, historyRes] = await Promise.all([
        api.get(`/regions/${region}/subscriptions/${subscriptionId}/details`),
        api.get(`/regions/${region}/subscriptions/${subscriptionId}/history`)
      ]);

      const history = detailsRes.data.current_month_status === 'pending'
        ? [{ month: new Date().getMonth() + 1, year: new Date().getFullYear(), status: 'pending', paid_at: null }, ...historyRes.data]
        : historyRes.data;

      setSubscriptionDetails({ ...detailsRes.data, history });
    } finally {
      setSubscriptionDetailsLoading(false);
    }
  };

  const openSubscriptionDetails = async (subscriptionId) => {
    setSelectedSubscriptionId(subscriptionId);
    setSubscriptionActionMessage('');
    await loadSubscriptionDetails(subscriptionId);
  };

  const markSubscriptionPaid = async () => {
    if (!selectedSubscriptionId) return;
    try {
      const response = await api.post(`/regions/${region}/subscriptions/${selectedSubscriptionId}/mark-paid`);
      setSubscriptionActionMessage(`Subscription marked paid for ${response.data.month}/${response.data.year}.`);
      await loadAll();
      await loadSubscriptionDetails(selectedSubscriptionId);
    } catch (err) {
      setSubscriptionActionMessage(err.response?.data?.detail || 'Unable to mark subscription as paid');
    }
  };

  const incomeChart = useMemo(() => ({
    labels: incomeTrend.map((d) => d.month),
    datasets: [
      {
        label: `${region.toUpperCase()} Income Trend`,
        data: incomeTrend.map((d) => d.value),
        borderColor: '#00b894',
        backgroundColor: 'rgba(0,184,148,0.15)',
        fill: true
      }
    ]
  }), [incomeTrend, region]);

  const investmentChart = useMemo(() => ({
    labels: investmentTrend.map((d) => d.month),
    datasets: [
      {
        label: `${region.toUpperCase()} Investment Growth`,
        data: investmentTrend.map((d) => d.value),
        backgroundColor: '#ff6f00'
      }
    ]
  }), [investmentTrend, region]);

  const tileSummary = useMemo(() => {
    const incomeTotal = incomes.reduce((acc, item) => acc + Number(item.amount || 0), 0);
    const expenseTotal = expenses.reduce((acc, item) => acc + Number(item.amount || 0), 0);
    const loanOutstanding = loans.reduce((acc, loan) => acc + Number(loan.outstanding_amount || 0), 0);
    const subscriptionMonthly = subscriptions.reduce((acc, item) => acc + Number(item.monthly_cost || 0), 0);
    const debtOutstanding = debts.reduce((acc, debt) => acc + Number(debt.outstanding_amount || 0), 0);
    const investmentValue = investments.reduce((acc, item) => acc + Number(item.current_value || 0), 0);
    const goldValue = gold.reduce((acc, item) => acc + Number(item.current_value || 0), 0);

    return {
      income: `Total ${incomeTotal.toFixed(2)} | ${incomes.length} entries`,
      expense: summary ? `Cash Flow ${Number(summary.net_cash_flow || 0).toFixed(2)} | Expenses ${expenseTotal.toFixed(2)}` : `Expenses ${expenseTotal.toFixed(2)}`,
      loan: `Outstanding ${loanOutstanding.toFixed(2)} | ${loans.length} loans`,
      subscription: `Monthly ${subscriptionMonthly.toFixed(2)} | ${subscriptions.length} subscriptions`,
      debt: `Outstanding ${debtOutstanding.toFixed(2)} | ${debts.length} debts`,
      investment: `Current ${investmentValue.toFixed(2)} | ${investments.length} holdings`,
      gold: `Current ${goldValue.toFixed(2)} | ${gold.length} holdings`
    };
  }, [incomes, expenses, loans, subscriptions, debts, investments, gold, summary]);

  const postAndReload = async (url, payload, resetForm) => {
    await api.post(url, payload);
    if (resetForm) {
      resetForm();
    }
    await loadAll();
  };

  const deleteItem = async (url) => {
    await api.delete(url);
    await loadAll();
  };

  const exportCSV = async (module) => {
    const response = await api.get(`/export/csv?region=${region}&module=${module}`, {
      responseType: 'blob'
    });

    const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = blobUrl;
    link.setAttribute('download', `${region}_${module}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(blobUrl);
  };

  const fetchLivePrice = async () => {
    const response = await api.get(`/regions/${region}/gold/live-price`);
    setGoldLivePrice(response.data.price_per_gram);
    if (response.data.price_per_gram) {
      setGoldForm((prev) => ({ ...prev, price_per_gram: response.data.price_per_gram }));
    }
  };

  const renderIncomeModule = () => (
    <section className="panel">
      <form onSubmit={(e) => { e.preventDefault(); postAndReload(`/regions/${region}/incomes`, { ...incomeForm, amount: Number(incomeForm.amount) }, () => setIncomeForm({ ...incomeForm, amount: '', notes: '' })); }}>
        <select value={incomeForm.category} onChange={(e) => setIncomeForm({ ...incomeForm, category: e.target.value })}>{incomeCategories.map((c) => <option key={c}>{c}</option>)}</select>
        <input type="number" placeholder="Amount" value={incomeForm.amount} onChange={(e) => setIncomeForm({ ...incomeForm, amount: e.target.value })} required />
        <input type="date" value={incomeForm.entry_date} onChange={(e) => setIncomeForm({ ...incomeForm, entry_date: e.target.value })} required />
        <input placeholder="Notes" value={incomeForm.notes} onChange={(e) => setIncomeForm({ ...incomeForm, notes: e.target.value })} />
        <button type="submit" className="primary-btn">Add Income</button>
      </form>
      <Line data={incomeChart} />
      <ul>{incomes.map((item) => <li key={item.id} className="action-row"><div className="action-row-copy">{item.category}: {item.amount}</div><div className="action-chip-row"><button type="button" className="action-chip action-chip-delete" onClick={() => deleteItem(`/regions/${region}/incomes/${item.id}`)}><span className="action-chip-icon">X</span><span className="action-chip-label">Delete</span></button></div></li>)}</ul>
      <button className="ghost-btn" onClick={() => exportCSV('incomes')}>Export Income CSV</button>
    </section>
  );

  const renderExpenseModule = () => (
    <section className="panel">
      <form onSubmit={(e) => { e.preventDefault(); postAndReload(`/regions/${region}/expenses`, { ...expenseForm, amount: Number(expenseForm.amount) }, () => setExpenseForm({ ...expenseForm, amount: '', notes: '' })); }}>
        <input placeholder="Category" value={expenseForm.category} onChange={(e) => setExpenseForm({ ...expenseForm, category: e.target.value })} required />
        <input type="number" placeholder="Amount" value={expenseForm.amount} onChange={(e) => setExpenseForm({ ...expenseForm, amount: e.target.value })} required />
        <input type="date" value={expenseForm.entry_date} onChange={(e) => setExpenseForm({ ...expenseForm, entry_date: e.target.value })} required />
        <button type="submit" className="primary-btn">Add Expense</button>
      </form>
      <ul>{expenses.map((item) => <li key={item.id} className="action-row"><div className="action-row-copy">{item.category}: {item.amount}</div><div className="action-chip-row"><button type="button" className="action-chip action-chip-delete" onClick={() => deleteItem(`/regions/${region}/expenses/${item.id}`)}><span className="action-chip-icon">X</span><span className="action-chip-label">Delete</span></button></div></li>)}</ul>
      {summary && (
        <div className="summary-box">
          <p>Month: {summary.month}</p>
          <p>Income: {summary.income}</p>
          <p>Expenses: {summary.expenses}</p>
          <p>EMI: {summary.monthly_emi_total}</p>
            <p>Subscriptions: {summary.monthly_subscription_total || 0}</p>
          <p>Net Cash Flow: {summary.net_cash_flow}</p>
        </div>
      )}
    </section>
  );

  const renderLoanModule = () => (
    <section className="panel">
      <form onSubmit={(e) => { e.preventDefault(); postAndReload(`/regions/${region}/loans`, { ...loanForm, emi_amount: Number(loanForm.emi_amount), emi_date: Number(loanForm.emi_date), remaining_months: Number(loanForm.remaining_months), interest_rate: loanForm.interest_rate ? Number(loanForm.interest_rate) : null }, () => setLoanForm({ ...loanForm, loan_name: '', emi_amount: '', emi_date: '', remaining_months: '', interest_rate: '' })); }}>
        <input placeholder="Loan Name" value={loanForm.loan_name} onChange={(e) => setLoanForm({ ...loanForm, loan_name: e.target.value })} required />
        <input type="number" placeholder="EMI/month" value={loanForm.emi_amount} onChange={(e) => setLoanForm({ ...loanForm, emi_amount: e.target.value })} required />
        <input type="number" min="1" max="31" placeholder="EMI Date (day of month)" value={loanForm.emi_date} onChange={(e) => setLoanForm({ ...loanForm, emi_date: e.target.value })} required />
        <input type="number" placeholder="Remaining Months" value={loanForm.remaining_months} onChange={(e) => setLoanForm({ ...loanForm, remaining_months: e.target.value })} required />
        <input type="number" placeholder="Interest Rate" value={loanForm.interest_rate} onChange={(e) => setLoanForm({ ...loanForm, interest_rate: e.target.value })} />
        <button type="submit" className="primary-btn">Add Loan</button>
      </form>

      {selectedLoanId && loanDetails ? (
        <div className="loan-detail-card">
          <div className="loan-detail-header">
            <h3>{loanDetails.loan_name}</h3>
            <button type="button" className="action-chip action-chip-view" onClick={() => { setSelectedLoanId(null); setLoanDetails(null); setLoanActionMessage(''); }}><span className="action-chip-icon">&lt;</span><span className="action-chip-label">Back to Loan List</span></button>
          </div>
          {loanDetailsLoading ? (
            <p>Loading loan details...</p>
          ) : (
            <>
              <p>EMI Amount: {loanDetails.emi_amount}</p>
              <p>EMI Date: {loanDetails.emi_date} of every month</p>
              <p>Remaining Months: {loanDetails.remaining_months}</p>
              <p>Total Outstanding Amount: {loanDetails.outstanding_amount}</p>
              <p>Interest Rate: {loanDetails.interest_rate || 'N/A'}</p>
              {loanDetails.mark_emi_enabled && <button className="primary-btn emi-mark-btn" onClick={markEmiCompleted}>{loanDetails.next_action_label}</button>}
              {!loanDetails.mark_emi_enabled && <p>Current EMI status: {loanDetails.current_month_status}</p>}
              {loanActionMessage && <p className="alert">{loanActionMessage}</p>}

              <div className="emi-history-block">
                <h4>EMI History</h4>
                <ul className="emi-history-list">
                  {loanDetails.emi_history.map((entry, index) => (
                    <li key={`${entry.year}-${entry.month}-${index}`} className={entry.status === 'completed' ? 'emi-completed' : 'emi-pending'}>
                      <span>{new Date(entry.year, entry.month - 1, 1).toLocaleString('en-US', { month: 'long', year: 'numeric' })}</span>
                      <span>{entry.status}</span>
                      <span>{entry.completed_at ? new Date(entry.completed_at).toLocaleString() : 'Not completed yet'}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </div>
      ) : (
        <ul>
          {loans.map((loan) => (
            <li key={loan.id} className="action-row">
              <div className="action-row-copy">
                {loan.loan_name}: {loan.remaining_months} months left | Outstanding {loan.outstanding_amount} | EMI date {loan.emi_date}
              </div>
              <div className="action-chip-row">
                <button type="button" className="action-chip action-chip-view" onClick={() => openLoanDetails(loan.id)}>
                  <span className="action-chip-icon">[]</span>
                  <span className="action-chip-label">Open Details</span>
                </button>
                <button type="button" className="action-chip action-chip-delete" onClick={() => deleteItem(`/regions/${region}/loans/${loan.id}`)}>
                  <span className="action-chip-icon">X</span>
                  <span className="action-chip-label">Delete</span>
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {loanAlerts.length > 0 && <p className="alert">Alerts: {loanAlerts.map((a) => a.loan_name).join(', ')}</p>}
    </section>
  );

  const renderDebtModule = () => (
    <section className="panel">
      <form onSubmit={(e) => { e.preventDefault(); postAndReload(`/regions/${region}/debts`, { ...debtForm, amount: Number(debtForm.amount) }, () => setDebtForm({ ...debtForm, lender_name: '', amount: '' })); }}>
        <input placeholder="Lender" value={debtForm.lender_name} onChange={(e) => setDebtForm({ ...debtForm, lender_name: e.target.value })} required />
        <input type="number" placeholder="Amount" value={debtForm.amount} onChange={(e) => setDebtForm({ ...debtForm, amount: e.target.value })} required />
        <input type="date" value={debtForm.due_date} onChange={(e) => setDebtForm({ ...debtForm, due_date: e.target.value })} required />
        <button type="submit" className="primary-btn">Add Debt</button>
      </form>
      <ul>
        {debts.map((debt) => (
          <li key={debt.id} className="action-row">
            <div className="action-row-copy">{debt.lender_name}: Outstanding {debt.outstanding_amount}</div>
            <form onSubmit={async (e) => {
              e.preventDefault();
              const repayment = repayments[debt.id];
              if (!repayment?.amount || !repayment?.payment_date) return;
              await api.post(`/regions/${region}/debts/${debt.id}/repayments`, { amount: Number(repayment.amount), payment_date: repayment.payment_date });
              setRepayments({ ...repayments, [debt.id]: { amount: '', payment_date: '' } });
              await loadAll();
            }}>
              <input type="number" placeholder="Repayment" value={repayments[debt.id]?.amount || ''} onChange={(e) => setRepayments({ ...repayments, [debt.id]: { ...(repayments[debt.id] || {}), amount: e.target.value } })} />
              <input type="date" value={repayments[debt.id]?.payment_date || ''} onChange={(e) => setRepayments({ ...repayments, [debt.id]: { ...(repayments[debt.id] || {}), payment_date: e.target.value } })} />
              <div className="action-chip-row">
                <button type="submit" className="action-chip action-chip-view"><span className="action-chip-icon">+</span><span className="action-chip-label">Track Repayment</span></button>
                <button type="button" className="action-chip action-chip-delete" onClick={() => deleteItem(`/regions/${region}/debts/${debt.id}`)}><span className="action-chip-icon">X</span><span className="action-chip-label">Delete</span></button>
              </div>
            </form>
          </li>
        ))}
      </ul>
    </section>
  );

  const renderSubscriptionModule = () => (
    <section className="panel">
      <form onSubmit={(e) => {
        e.preventDefault();
        postAndReload(
          `/regions/${region}/subscriptions`,
          {
            ...subscriptionForm,
            monthly_cost: Number(subscriptionForm.monthly_cost),
            billing_date: Number(subscriptionForm.billing_date)
          },
          () => setSubscriptionForm({ subscription_name: '', monthly_cost: '', billing_date: '', category: '', notes: '' })
        );
      }}>
        <input placeholder="Subscription Name" value={subscriptionForm.subscription_name} onChange={(e) => setSubscriptionForm({ ...subscriptionForm, subscription_name: e.target.value })} required />
        <input type="number" placeholder="Monthly Cost" value={subscriptionForm.monthly_cost} onChange={(e) => setSubscriptionForm({ ...subscriptionForm, monthly_cost: e.target.value })} required />
        <input type="number" min="1" max="31" placeholder="Billing Date (day of month)" value={subscriptionForm.billing_date} onChange={(e) => setSubscriptionForm({ ...subscriptionForm, billing_date: e.target.value })} required />
        <input placeholder="Category" value={subscriptionForm.category} onChange={(e) => setSubscriptionForm({ ...subscriptionForm, category: e.target.value })} required />
        <input placeholder="Notes" value={subscriptionForm.notes} onChange={(e) => setSubscriptionForm({ ...subscriptionForm, notes: e.target.value })} />
        <button type="submit" className="primary-btn">Add Subscription</button>
      </form>

      {selectedSubscriptionId && subscriptionDetails ? (
        <div className="loan-detail-card">
          <div className="loan-detail-header">
            <h3>{subscriptionDetails.subscription_name}</h3>
            <button type="button" className="action-chip action-chip-view" onClick={() => { setSelectedSubscriptionId(null); setSubscriptionDetails(null); setSubscriptionActionMessage(''); }}><span className="action-chip-icon">&lt;</span><span className="action-chip-label">Back to Subscription List</span></button>
          </div>
          {subscriptionDetailsLoading ? (
            <p>Loading subscription details...</p>
          ) : (
            <>
              <p>Monthly Cost: {subscriptionDetails.monthly_cost}</p>
              <p>Billing Date: {subscriptionDetails.billing_date} of every month</p>
              <p>Category: {subscriptionDetails.category}</p>
              <p>Notes: {subscriptionDetails.notes || 'N/A'}</p>
              {subscriptionDetails.mark_paid_enabled && <button className="primary-btn emi-mark-btn" onClick={markSubscriptionPaid}>Mark as Paid</button>}
              {!subscriptionDetails.mark_paid_enabled && <p>Current month status: {subscriptionDetails.current_month_status}</p>}
              {subscriptionActionMessage && <p className="alert">{subscriptionActionMessage}</p>}

              <div className="emi-history-block">
                <h4>Payment History</h4>
                <ul className="emi-history-list">
                  {subscriptionDetails.history.map((entry, index) => (
                    <li key={`${entry.year}-${entry.month}-${index}`} className={entry.status === 'paid' ? 'emi-completed' : 'emi-pending'}>
                      <span>{entry.month}/{entry.year}</span>
                      <span>{entry.status}</span>
                      <span>{entry.paid_at ? new Date(entry.paid_at).toLocaleString() : 'Not paid yet'}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </div>
      ) : (
        <ul>
          {subscriptions.map((item) => (
            <li key={item.id} className="action-row">
              <div className="action-row-copy">
                {item.subscription_name}: {item.monthly_cost}/month | Billing date {item.billing_date} | {item.category}
              </div>
              <div className="action-chip-row">
                <button type="button" className="action-chip action-chip-view" onClick={() => openSubscriptionDetails(item.id)}>
                  <span className="action-chip-icon">[]</span>
                  <span className="action-chip-label">Open Details</span>
                </button>
                <button type="button" className="action-chip action-chip-delete" onClick={() => deleteItem(`/regions/${region}/subscriptions/${item.id}`)}>
                  <span className="action-chip-icon">X</span>
                  <span className="action-chip-label">Delete</span>
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );

  const renderInvestmentModule = () => (
    <section className="panel">
      <form onSubmit={(e) => { e.preventDefault(); postAndReload(`/regions/${region}/investments`, { ...investmentForm, invested_value: Number(investmentForm.invested_value), current_value: Number(investmentForm.current_value) }, () => setInvestmentForm({ ...investmentForm, name: '', invested_value: '', current_value: '' })); }}>
        <input placeholder="Investment Name" value={investmentForm.name} onChange={(e) => setInvestmentForm({ ...investmentForm, name: e.target.value })} required />
        <select value={investmentForm.investment_type} onChange={(e) => setInvestmentForm({ ...investmentForm, investment_type: e.target.value })}>{investmentTypes.map((t) => <option key={t}>{t}</option>)}</select>
        <input type="number" placeholder="Invested Value" value={investmentForm.invested_value} onChange={(e) => setInvestmentForm({ ...investmentForm, invested_value: e.target.value })} required />
        <input type="number" placeholder="Current Value" value={investmentForm.current_value} onChange={(e) => setInvestmentForm({ ...investmentForm, current_value: e.target.value })} required />
        <button type="submit" className="primary-btn">Add Investment</button>
      </form>
      <Bar data={investmentChart} />
      <ul>{investments.map((i) => <li key={i.id} className="action-row"><div className="action-row-copy">{i.name}: P/L {i.profit_or_loss}</div><div className="action-chip-row"><button type="button" className="action-chip action-chip-delete" onClick={() => deleteItem(`/regions/${region}/investments/${i.id}`)}><span className="action-chip-icon">X</span><span className="action-chip-label">Delete</span></button></div></li>)}</ul>
    </section>
  );

  const renderGoldModule = () => (
    <section className="panel">
      <button className="ghost-btn" onClick={fetchLivePrice}>Fetch Live Gold Price</button>
      {goldLivePrice && <p>Live Price Per Gram: {goldLivePrice}</p>}
      <form onSubmit={(e) => { e.preventDefault(); postAndReload(`/regions/${region}/gold`, { ...goldForm, quantity: Number(goldForm.quantity), price_per_gram: Number(goldForm.price_per_gram) }, () => setGoldForm({ ...goldForm, quantity: '' })); }}>
        <input type="number" placeholder="Quantity" value={goldForm.quantity} onChange={(e) => setGoldForm({ ...goldForm, quantity: e.target.value })} required />
        <select value={goldForm.unit} onChange={(e) => setGoldForm({ ...goldForm, unit: e.target.value })}>{goldUnits.map((u) => <option key={u}>{u}</option>)}</select>
        <input type="number" placeholder="Price/gram" value={goldForm.price_per_gram} onChange={(e) => setGoldForm({ ...goldForm, price_per_gram: e.target.value })} required />
        <button type="submit" className="primary-btn">Add Gold</button>
      </form>
      <ul>{gold.map((item) => <li key={item.id} className="action-row"><div className="action-row-copy">{item.grams_total}g value {item.current_value}</div><div className="action-chip-row"><button type="button" className="action-chip action-chip-delete" onClick={() => deleteItem(`/regions/${region}/gold/${item.id}`)}><span className="action-chip-icon">X</span><span className="action-chip-label">Delete</span></button></div></li>)}</ul>
    </section>
  );

  const renderDetailModule = () => {
    if (activeModule === 'income') return renderIncomeModule();
    if (activeModule === 'expense') return renderExpenseModule();
    if (activeModule === 'loan') return renderLoanModule();
    if (activeModule === 'subscription') return renderSubscriptionModule();
    if (activeModule === 'debt') return renderDebtModule();
    if (activeModule === 'investment') return renderInvestmentModule();
    if (activeModule === 'gold') return renderGoldModule();
    return null;
  };

  if (!activeModule) {
    return (
      <div className={`tile-grid tile-motion-${moduleStage}`}>
        {moduleConfig.map((module) => (
          <button key={module.id} className="tile-card" onClick={() => openModule(module.id)}>
            <h2>{module.title}</h2>
            <p>{tileSummary[module.id]}</p>
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className={`detail-view tile-motion-${moduleStage}`}>
      <div className="detail-header">
        <h2>{moduleTitleMap[activeModule]}</h2>
        <button type="button" className="action-chip action-chip-view" onClick={closeModule}><span className="action-chip-icon">&lt;</span><span className="action-chip-label">Back to {region.toUpperCase()} Tiles</span></button>
      </div>
      {renderDetailModule()}
    </div>
  );
}
