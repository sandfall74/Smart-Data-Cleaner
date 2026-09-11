import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sparkles, FileSpreadsheet, Home as HomeIcon, Sun, Moon } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { Button } from '../ui/button';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-white/80 dark:bg-[var(--color-neon-dark)]/80 border-b border-slate-200 dark:border-[var(--color-neon-border)] transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-2">
          <Sparkles className="w-6 h-6 text-sky-500 dark:text-[var(--color-neon-blue)] animate-pulse" />
          <span className="font-bold text-xl tracking-wider text-slate-900 dark:text-white">
            SmartData<span className="text-sky-500 dark:text-[var(--color-neon-blue)]">Cleaner</span>
          </span>
        </Link>

        <nav className="flex items-center space-x-4">
          <Link to="/">
            <Button variant={location.pathname === '/' ? 'default' : 'ghost'} className="flex items-center gap-2">
              <HomeIcon className="w-4 h-4" />
              <span>Inicio</span>
            </Button>
          </Link>

          <Link to="/app">
            <Button variant={location.pathname === '/app' ? 'default' : 'ghost'} className="flex items-center gap-2">
              <FileSpreadsheet className="w-4 h-4" />
              <span>Limpiar Datos</span>
            </Button>
          </Link>

          <Button variant="outline" size="icon" onClick={toggleTheme} className="ml-2">
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-700" />}
          </Button>
        </nav>
      </div>
    </header>
  );
};