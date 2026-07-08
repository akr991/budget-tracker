import { useEffect, useRef, useState } from 'react';
import LoginForm from './components/LoginForm';
import NetWorthDashboard from './components/NetWorthDashboard';
import RegionDashboard from './components/RegionDashboard';
import { api, setAuthToken } from './api/client';

const tabs = [
  { id: 'india', label: 'India' },
  { id: 'uae', label: 'UAE' },
  { id: 'total', label: 'Summary' }
];

export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem('token')));
  const [profile, setProfile] = useState(null);
  const [settings, setSettings] = useState({ dark_mode: false, monthly_summary_notifications: true });
  const [activeTab, setActiveTab] = useState('india');
  const [displayTab, setDisplayTab] = useState('india');
  const [tabStage, setTabStage] = useState('idle');
  const [tabDirection, setTabDirection] = useState('right');
  const tabTimeoutRef = useRef(null);

  const loadProfile = async () => {
    const [profileRes, settingsRes] = await Promise.all([
      api.get('/profile'),
      api.get('/profile/settings')
    ]);

    setProfile(profileRes.data);
    setSettings(settingsRes.data);
    document.documentElement.dataset.theme = settingsRes.data.dark_mode ? 'dark' : 'light';
  };

  useEffect(() => {
    if (authenticated) {
      loadProfile().catch(() => {
        setAuthToken(null);
        setAuthenticated(false);
      });
    }
  }, [authenticated]);

  const toggleDarkMode = async () => {
    const response = await api.put('/profile/settings', { dark_mode: !settings.dark_mode });
    setSettings(response.data);
    document.documentElement.dataset.theme = response.data.dark_mode ? 'dark' : 'light';
  };

  const toggleNotifications = async () => {
    const response = await api.put('/profile/settings', { monthly_summary_notifications: !settings.monthly_summary_notifications });
    setSettings(response.data);
  };

  const logout = () => {
    setAuthToken(null);
    setAuthenticated(false);
    setProfile(null);
  };

  useEffect(() => () => {
    if (tabTimeoutRef.current) {
      clearTimeout(tabTimeoutRef.current);
    }
  }, []);

  const handleTabChange = (nextTab) => {
    if (nextTab === displayTab) {
      return;
    }

    const currentIndex = tabs.findIndex((tab) => tab.id === displayTab);
    const nextIndex = tabs.findIndex((tab) => tab.id === nextTab);
    setActiveTab(nextTab);
    setTabDirection(nextIndex > currentIndex ? 'left' : 'right');
    setTabStage('exit');

    if (tabTimeoutRef.current) {
      clearTimeout(tabTimeoutRef.current);
    }

    tabTimeoutRef.current = window.setTimeout(() => {
      setDisplayTab(nextTab);
      setTabStage('enter');
      tabTimeoutRef.current = window.setTimeout(() => {
        setTabStage('idle');
      }, 220);
    }, 190);
  };

  if (!authenticated) {
    return <LoginForm onAuth={() => setAuthenticated(true)} />;
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>Personal Budget Cloud Tracker</h1>
          <p>{profile ? `${profile.full_name} (${profile.email})` : 'Loading profile...'}</p>
        </div>
        <div className="header-actions">
          <button className="ghost-btn" onClick={toggleDarkMode}>{settings.dark_mode ? 'Light Mode' : 'Dark Mode'}</button>
          <button className="ghost-btn" onClick={toggleNotifications}>{settings.monthly_summary_notifications ? 'Disable Monthly Alerts' : 'Enable Monthly Alerts'}</button>
          <button className="primary-btn" onClick={logout}>Logout</button>
        </div>
      </header>

      <nav className="tab-row">
        {tabs.map((tab) => (
          <button key={tab.id} className={activeTab === tab.id ? 'tab-btn active' : 'tab-btn'} onClick={() => handleTabChange(tab.id)}>
            {tab.label}
          </button>
        ))}
      </nav>

      <main className={`motion-shell tab-motion-${tabStage} tab-direction-${tabDirection}`}>
        {displayTab === 'india' && <RegionDashboard region="india" />}
        {displayTab === 'uae' && <RegionDashboard region="uae" />}
        {displayTab === 'total' && <NetWorthDashboard />}
      </main>
    </div>
  );
}
