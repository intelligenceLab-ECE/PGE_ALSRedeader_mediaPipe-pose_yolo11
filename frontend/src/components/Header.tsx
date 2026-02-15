import { Link } from "react-router-dom";

export function Header() {
  return (
    <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-4">
      <Link to="/" className="text-lg font-semibold text-sky-300">AI Playground</Link>
      <a href="https://github.com" target="_blank" rel="noreferrer" className="text-sm text-slate-300 hover:text-white">GitHub</a>
    </header>
  );
}
