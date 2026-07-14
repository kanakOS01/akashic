import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

mermaid.initialize({ 
  startOnLoad: false, 
  theme: "dark",
  themeVariables: {
    background: "#000000",
    primaryColor: "#111111",
    primaryTextColor: "#ffffff",
    lineColor: "#333333",
  }
});

let counter = 0;

export function MermaidChart({ code }: { code: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const id = `akashic-mermaid-${counter++}`;
    mermaid
      .render(id, code)
      .then(({ svg }) => {
        if (active && ref.current) ref.current.innerHTML = svg;
      })
      .catch((e) => {
        if (active) setError(String(e));
      });
    return () => {
      active = false;
    };
  }, [code]);

  if (error) {
    return <pre className="text-red-500 bg-red-500/10 border border-red-500/20 px-4 py-3 rounded-lg text-xs font-mono whitespace-pre-wrap">{error}</pre>;
  }
  return (
    <div className="my-6 p-6 rounded-xl border border-[#1a1a1a] bg-[#0a0a0a] flex justify-center overflow-x-auto">
      <div ref={ref} className="w-full max-w-full" />
    </div>
  );
}
