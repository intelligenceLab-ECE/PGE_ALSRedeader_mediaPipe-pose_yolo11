import { ReactNode } from "react";
import { Link } from "react-router-dom";

import { Button } from "../ui/button";

export function ToolTopBar({ title, controls }: { title: string; controls: ReactNode }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 p-3">
      <div className="flex items-center gap-2">
        <Link to="/"><Button variant="outline">Retour menu</Button></Link>
        <h1 className="text-base font-semibold">{title}</h1>
      </div>
      <div className="flex flex-wrap gap-2">{controls}</div>
    </div>
  );
}
