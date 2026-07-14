import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { useSearch } from "../lib/search";
import { useNav } from "../hooks/useNav";
import { Link } from "react-router-dom";

export function SearchBar() {
  const { nav } = useNav();
  const { search } = useSearch(nav?.index ?? [], {});
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const results = query ? search(query) : [];

  const [isMac, setIsMac] = useState(true);
  useEffect(() => {
    setIsMac(navigator.platform.toUpperCase().indexOf("MAC") >= 0);
  }, []);

  return (
    <div className="relative w-full">
      <div className="flex items-center gap-2.5 rounded-lg border border-[#1a1a1a] bg-[#080808] px-3 py-1.5 transition-all duration-150 focus-within:border-emerald-500/50 focus-within:ring-1 focus-within:ring-emerald-500/20">
        <Search size={14} className="text-[#525252] shrink-0" />
        <input
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          placeholder="Search docs..."
          className="w-full bg-transparent text-xs text-white placeholder-[#737373] outline-none"
        />
        <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-0.5 rounded border border-[#1a1a1a] bg-black px-1.5 font-mono text-[10px] font-medium text-[#525252] shrink-0">
          {isMac ? "⌘" : "Ctrl+"}K
        </kbd>
      </div>
      {open && results.length > 0 && (
        <ul className="absolute z-10 mt-2 max-h-80 w-full overflow-auto rounded-lg border border-[#1a1a1a] bg-[#080808] shadow-2xl shadow-black p-1.5 space-y-0.5">
          {results.map((r) => (
            <li key={r.path}>
              <Link
                to={`/doc/${r.path}`}
                className="block px-3 py-2 rounded-md text-xs transition-colors hover:bg-[#111111]"
              >
                <span className="font-semibold text-white block mb-0.5">{r.title}</span>
                <span className="text-[10px] text-[#525252] uppercase tracking-wider">{r.section}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
