import { Link } from "react-router-dom";

import { Card } from "../ui/card";
import { Button } from "../ui/button";

const tools = [
  { title: "ASL Recognition", desc: "Reconnais des lettres de la langue des signes en direct.", to: "/asl", emoji: "✋" },
  { title: "Segmentation Pose + Face", desc: "Observe les points du corps et du visage detectes par IA.", to: "/segmentation", emoji: "🧍" },
];

export default function HomePage() {
  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-8">
      <section className="mb-8">
        <h1 className="text-3xl font-bold text-white">Bienvenue dans AI Playground</h1>
        <p className="mt-2 max-w-3xl text-slate-300">Explore des outils d'IA en direct avec ta webcam. Teste la reconnaissance ASL et la pose/face MediaPipe.</p>
      </section>
      <section className="grid gap-4 sm:grid-cols-2">
        {tools.map((tool) => (
          <Card key={tool.title} className="flex flex-col justify-between">
            <div>
              <p className="text-2xl">{tool.emoji}</p>
              <h2 className="mt-3 text-lg font-semibold">{tool.title}</h2>
              <p className="mt-2 text-sm text-slate-300">{tool.desc}</p>
            </div>
            <Link className="mt-4" to={tool.to}><Button className="w-full">Essayer</Button></Link>
          </Card>
        ))}
      </section>
    </main>
  );
}
