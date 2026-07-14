import { Link, useParams } from "react-router-dom";
import { NavSection } from "../lib/types";
import { 
  Server, Workflow, Settings, Database, FileText, BookOpen, Folder, Home
} from "lucide-react";

interface Props {
  home: string;
  sections: NavSection[];
}

function getSectionIcon(title: string) {
  const t = title.toUpperCase();
  if (t.includes("SERVICE")) return <Server size={13} className="text-[#525252]" />;
  if (t.includes("FLOW")) return <Workflow size={13} className="text-[#525252]" />;
  if (t.includes("SYSTEM")) return <Settings size={13} className="text-[#525252]" />;
  if (t.includes("ENTITY") || t.includes("ENTITIES")) return <Database size={13} className="text-[#525252]" />;
  if (t.includes("ADR")) return <FileText size={13} className="text-[#525252]" />;
  if (t.includes("GLOSSARY")) return <BookOpen size={13} className="text-[#525252]" />;
  return <Folder size={13} className="text-[#525252]" />;
}

export function Sidebar({ home, sections }: Props) {
  const params = useParams();
  const current = params["*"];

  return (
    <nav className="space-y-6 text-sm">
      <div className="space-y-1">
        <Link
          to="/doc/README.md"
          className={`flex items-center gap-2.5 rounded-lg px-3 py-2 transition-all duration-150 ${
            current === "README.md"
              ? "text-emerald-400 bg-emerald-500/5 border border-emerald-500/20 font-semibold"
              : "text-[#d4d4d8] hover:text-white hover:bg-[#151515]"
          }`}
        >
          <Home size={13} className={current === "README.md" ? "text-emerald-400" : "text-[#737373]"} />
          Home
        </Link>
      </div>

      {sections.map((section) => (
        <div key={section.id} className="space-y-2">
          <div className="flex items-center gap-2 px-3 text-[10px] font-bold uppercase tracking-widest text-[#525252]">
            {getSectionIcon(section.title)}
            <span>{section.title}</span>
          </div>
          <ul className="space-y-0.5 border-l border-[#1f1f1f] ml-[18px] pl-3">
            {section.items.map((item) => {
              const active = current === item.path;
              return (
                <li key={item.path}>
                  <Link
                    to={`/doc/${item.path}`}
                    className={`block truncate rounded-md px-3 py-1.5 text-xs transition-all duration-150 ${
                      active
                        ? "text-emerald-400 font-semibold bg-emerald-500/5 border-l-2 border-emerald-500 pl-2.5 -ml-3.5"
                        : "text-[#d4d4d8] hover:text-white hover:bg-[#151515]"
                    }`}
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
        <p className="px-3 text-xs text-[#525252]">No documents yet.</p>
      )}
    </nav>
  );
}
