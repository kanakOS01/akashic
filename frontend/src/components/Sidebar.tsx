import { Link, useParams } from "react-router-dom";
import { NavSection } from "../lib/types";

interface Props {
  home: string;
  sections: NavSection[];
}

export function Sidebar({ home, sections }: Props) {
  const params = useParams();
  const current = params["*"];

  return (
    <nav className="space-y-4 text-sm">
      <Link
        to="/doc/README.md"
        className={`block rounded px-2 py-1 ${current === "README.md" ? "bg-slate-200 dark:bg-slate-700 font-medium" : "hover:bg-slate-100 dark:hover:bg-slate-800"}`}
      >
        Home
      </Link>
      {sections.map((section) => (
        <div key={section.id}>
          <div className="px-2 pb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
            {section.title}
          </div>
          <ul className="space-y-0.5">
            {section.items.map((item) => {
              const active = current === item.path;
              return (
                <li key={item.path}>
                  <Link
                    to={`/doc/${item.path}`}
                    className={`block truncate rounded px-2 py-1 ${active ? "bg-slate-200 dark:bg-slate-700 font-medium" : "hover:bg-slate-100 dark:hover:bg-slate-800"}`}
                    title={item.title}
                  >
                    {item.title}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
      {home === "" && sections.length === 0 && (
        <p className="px-2 text-slate-400">No documents yet.</p>
      )}
    </nav>
  );
}
