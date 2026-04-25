import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, XCircle, Info, X } from 'lucide-react';

const ToastContext = createContext(null);

export const useToast = () => useContext(ToastContext);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismiss = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const toast = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => dismiss(id), 3500);
    return id;
  }, [dismiss]);

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div
        className="fixed top-20 right-4 z-[9999] flex flex-col gap-2 pointer-events-none"
        aria-live="polite"
      >
        {toasts.map(t => (
          <ToastItem key={t.id} toast={t} onDismiss={() => dismiss(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

const typeConfig = {
  success: { Icon: CheckCircle2, iconClass: 'text-green-500', bar: 'bg-green-500' },
  error:   { Icon: XCircle,      iconClass: 'text-red-500',   bar: 'bg-red-500'   },
  info:    { Icon: Info,          iconClass: 'text-blue-500',  bar: 'bg-blue-500'  },
};

function ToastItem({ toast, onDismiss }) {
  const { Icon, iconClass, bar } = typeConfig[toast.type] || typeConfig.info;
  return (
    <div className="pointer-events-auto relative flex items-start gap-3 bg-white rounded-xl shadow-lg border border-gray-200 pl-4 pr-3 py-3 min-w-[280px] max-w-sm overflow-hidden">
      <div className={`absolute left-0 inset-y-0 w-1 ${bar} rounded-l-xl`} />
      <Icon size={18} className={`${iconClass} mt-0.5 flex-shrink-0`} />
      <p className="text-sm text-gray-800 flex-1 leading-snug">{toast.message}</p>
      <button
        onClick={onDismiss}
        className="text-gray-300 hover:text-gray-500 transition-colors flex-shrink-0 mt-0.5"
        aria-label="닫기"
      >
        <X size={14} />
      </button>
    </div>
  );
}
