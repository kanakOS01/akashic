import { useState } from "react";
import { useParams } from "react-router-dom";
import { useDoc } from "../hooks/useDoc";
import { useMeta } from "../hooks/useMeta";
import { DocViewer } from "../components/DocViewer";
import { DocEditor } from "../components/Editor";
import { Toolbar } from "../components/Toolbar";
import { CommitDialog } from "../components/CommitDialog";
import { TableOfContents } from "../components/TableOfContents";

export function DocPage() {
  const params = useParams();
  const slug = params["*"] ?? "";
  const path = slug.endsWith(".md") ? slug : `${slug}.md`;
  const { doc, loading, error, save, commit, push } = useDoc(slug ? path : undefined);
  const meta = useMeta();
  const editable = meta?.editable ?? false;
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [committing, setCommitting] = useState(false);
  const [pushing, setPushing] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);

  if (loading) return <p className="text-[#525252] animate-pulse">Loading…</p>;
  if (error) return <p className="text-red-500 bg-red-500/10 border border-red-500/20 px-4 py-3 rounded-lg text-sm">Failed to load: {error}</p>;
  if (!doc) return <p className="text-[#525252]">Select a document.</p>;

  const startEdit = () => {
    setDraft(doc.raw);
    setEditing(true);
    setStatus(null);
  };

  const handleSave = async () => {
    await save(draft);
    setEditing(false);
    setStatus("Saved.");
  };

  const handleCommit = async (message: string) => {
    setDialogOpen(false);
    if (draft !== doc.raw) {
      await save(draft);
      setEditing(false);
    }
    setCommitting(true);
    try {
      await commit(message);
      setStatus("Committed.");
    } catch (e) {
      setStatus(String(e));
    } finally {
      setCommitting(false);
    }
  };

  const handlePush = async () => {
    setPushing(true);
    try {
      await push();
      setStatus("Pushed.");
    } catch (e) {
      setStatus(String(e));
    } finally {
      setPushing(false);
    }
  };

  return (
    <div className="flex gap-16 max-w-6xl mx-auto">
      {/* Main Content Area */}
      <div className="flex-1 min-w-0">
        <div className="mb-8 flex items-start justify-between gap-4">
          <div>
            <div className="text-xs font-semibold text-emerald-500 uppercase tracking-wider mb-1">
              {doc.type || "Page"}
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight leading-none mb-2">
              {doc.title}
            </h1>
            <p className="text-xs text-[#525252] font-mono">
              {doc.path}
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            {status && (
              <span className="text-xs bg-[#0c0c0c] border border-[#1a1a1a] text-[#d4d4d8] px-2 py-0.5 rounded font-mono">
                {status}
              </span>
            )}
            <Toolbar
              editable={editable}
              dirty={draft !== doc.raw}
              editing={editing}
              onToggleEdit={() => (editing ? setEditing(false) : startEdit())}
              onSave={handleSave}
              onOpenCommit={() => setDialogOpen(true)}
              onPush={handlePush}
              committing={committing}
              pushing={pushing}
            />
          </div>
        </div>

        <div className="min-h-[500px]">
          {editing ? (
            <DocEditor value={draft} onChange={setDraft} />
          ) : (
            <DocViewer content={doc.content} />
          )}
        </div>
      </div>

      {/* Right Sidebar (TOC) - only when reading */}
      {!editing && (
        <aside className="w-60 shrink-0 hidden xl:block sticky top-24 self-start max-h-[calc(100vh-8rem)] overflow-y-auto pr-2">
          <TableOfContents content={doc.content} />
        </aside>
      )}

      <CommitDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSubmit={handleCommit}
      />
    </div>
  );
}
