import { ButtonHTMLAttributes } from "react";

import { cn } from "../lib/cn";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "secondary" | "outline";
};

export function Button({ className, variant = "default", ...props }: Props) {
  return (
    <button
      className={cn(
        "inline-flex min-h-10 items-center justify-center rounded-md px-4 text-sm font-medium transition",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 disabled:opacity-50",
        variant === "default" && "bg-sky-500 text-white hover:bg-sky-400",
        variant === "secondary" && "bg-white/10 text-white hover:bg-white/20",
        variant === "outline" && "border border-white/20 bg-transparent text-white hover:bg-white/10",
        className
      )}
      {...props}
    />
  );
}
