import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { SearchBar } from "./SearchBar";
import { useNav } from "../hooks/useNav";

export function Layout() {
  const { nav } = useNav();

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 shrink-0 border-r bg-slate-50 p-4 dark:bg-slate-900">
        <div className="mb-4 text-lg font-bold">Akashic</div>
        <Sidebar home={nav?.home ?? ""} sections={nav?.sections ?? []} />
      </aside>
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b px-6 py-3">
          <h1 className="text-sm font-semibold text-slate-500">Knowledge Repository</h1>
          <div className="w-72">
            <SearchBar />
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
