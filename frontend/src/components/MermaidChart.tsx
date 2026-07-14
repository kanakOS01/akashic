import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

mermaid.initialize({ startOnLoad: false, theme: "default" });

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
    return <pre className="text-red-600 text-sm whitespace-pre-wrap">{error}</pre>;
  }
  return <div ref={ref} className="my-4 flex justify-center" />;
}
