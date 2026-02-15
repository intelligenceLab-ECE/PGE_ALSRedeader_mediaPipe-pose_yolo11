import { ReactNode } from "react";

import { Button } from "./button";

export function Dialog({
  open,
  title,
  description,
  onClose,
  actions,
}: {
  open: boolean;
  title: string;
  description: string;
  onClose?: () => void;
  actions?: ReactNode;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="glass w-full max-w-md p-5">
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="mt-2 text-sm text-slate-300">{description}</p>
        <div className="mt-4 flex flex-wrap gap-2">{actions}</div>
        {onClose ? (
          <Button variant="outline" className="mt-2 w-full" onClick={onClose}>
            Fermer
          </Button>
        ) : null}
      </div>
    </div>
  );
}
