import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { SearchBar } from "./SearchBar";
import { useNav } from "../hooks/useNav";

export function Layout() {
  const { nav } = useNav();

  return (
    <div className="flex min-h-screen bg-black text-[#e4e4e7]">
      {/* Left Sidebar — slightly lifted from pure black for distinction */}
      <aside className="w-64 shrink-0 border-r border-[#1f1f1f] bg-[#0c0c0c] p-4 overflow-y-auto">
        <div className="mb-6 px-2 text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <span className="h-6 w-6 rounded bg-emerald-500 flex items-center justify-center text-black text-xs font-black">A</span>
          Akashic
        </div>
        <Sidebar home={nav?.home ?? ""} sections={nav?.sections ?? []} />
      </aside>

      {/* Main content — pure black */}
      <div className="flex flex-1 flex-col bg-black min-w-0">
        <header className="flex items-center justify-between border-b border-[#1a1a1a] px-6 py-3 bg-black/95 backdrop-blur-sm sticky top-0 z-10">
          <h1 className="text-sm font-semibold text-[#737373]">Knowledge Repository</h1>
          <div className="w-72">
            <SearchBar />
          </div>
        </header>
        <main className="flex-1 overflow-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
