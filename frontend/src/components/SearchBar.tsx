import { useState } from "react";
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

  return (
    <div className="relative">
      <div className="flex items-center gap-2 rounded border px-2 py-1">
        <Search size={16} className="text-slate-400" />
        <input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          placeholder="Search docs..."
          className="w-full bg-transparent text-sm outline-none"
        />
      </div>
      {open && results.length > 0 && (
        <ul className="absolute z-10 mt-1 max-h-80 w-full overflow-auto rounded border bg-white shadow dark:bg-slate-900">
          {results.map((r) => (
            <li key={r.path}>
              <Link
                to={`/doc/${r.path}`}
                className="block px-3 py-2 text-sm hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <span className="font-medium">{r.title}</span>
                <span className="ml-2 text-xs text-slate-400">{r.section}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
