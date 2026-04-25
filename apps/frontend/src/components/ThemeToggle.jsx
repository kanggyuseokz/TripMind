import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from './ThemeContext';

export default function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="fixed bottom-6 right-6 z-50 w-12 h-12 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:scale-110 hover:shadow-xl"
      title={isDark ? '라이트 모드로 전환' : '다크 모드로 전환'}
    >
      {isDark
        ? <Sun size={20} className="text-yellow-400" />
        : <Moon size={20} className="text-gray-600" />
      }
    </button>
  );
}
