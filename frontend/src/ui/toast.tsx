import { createContext, ReactNode, useCallback, useContext, useMemo, useState } from "react";

type ToastState = { id: number; text: string };

type ToastCtx = {
  pushToast: (text: string) => void;
};

const Ctx = createContext<ToastCtx | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastState[]>([]);

  const pushToast = useCallback((text: string) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, text }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 2600);
  }, []);

  const value = useMemo(() => ({ pushToast }), [pushToast]);

  return (
    <Ctx.Provider value={value}>
      {children}
      <div className="fixed right-3 top-3 z-[60] space-y-2">
        {toasts.map((t) => (
          <div key={t.id} className="glass px-3 py-2 text-sm">{t.text}</div>
        ))}
      </div>
    </Ctx.Provider>
  );
}

export function useToast() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useToast must be used inside ToastProvider");
  return ctx;
}
