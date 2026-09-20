import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Home, FileSearch, Search, Microscope, Fingerprint, BarChart2, ShieldCheck, Info } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export const MainNavigation: React.FC = () => {
  const location = useLocation();
  const { t } = useLanguage();

  const navItems = [
    { to: '/home', labelKey: 'nav.home', icon: Home, end: true },
    { to: '/screening', labelKey: 'nav.screening', icon: FileSearch },
    { to: '/investigations', labelKey: 'nav.investigations', icon: Search },
    { to: '/forensics', labelKey: 'nav.forensics', icon: Microscope },
    { to: '/identity', labelKey: 'nav.identity', icon: Fingerprint },
    { to: '/analytics', labelKey: 'nav.analytics', icon: BarChart2 },
    { to: '/audit', labelKey: 'nav.audit', icon: ShieldCheck },
    { to: '/about', labelKey: 'nav.about', icon: Info },
  ];

  return (
    <nav className="main-nav" role="navigation" aria-label="Main navigation">
      <div className="container">
        {navItems.map(({ to, labelKey, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            aria-current={location.pathname === to ? 'page' : undefined}
          >
            <Icon size={15} aria-hidden="true" />
            {t(labelKey)}
          </NavLink>
        ))}
      </div>
    </nav>
  );
};


export default MainNavigation;
