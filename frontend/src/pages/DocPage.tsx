import { useState } from "react";
import { useParams } from "react-router-dom";
import { useDoc } from "../hooks/useDoc";
import { useMeta } from "../hooks/useMeta";
import { DocViewer } from "../components/DocViewer";
import { DocEditor } from "../components/Editor";
import { Toolbar } from "../components/Toolbar";

export function DocPage() {
  const params = useParams();
  const slug = params["*"] ?? "";
  const path = slug.endsWith(".md") ? slug : `${slug}.md`;
  const { doc, loading, error, save, commit } = useDoc(slug ? path : undefined);
  const meta = useMeta();
  const editable = meta?.editable ?? false;
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  if (loading) return <p className="text-slate-400">Loading…</p>;
  if (error) return <p className="text-red-600">Failed to load: {error}</p>;
  if (!doc) return <p className="text-slate-400">Select a document.</p>;

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

  const handleCommit = async () => {
    await commit();
    setStatus("Committed to Git.");
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">{doc.title}</h1>
          <p className="text-xs text-slate-400">
            {doc.type} · {doc.path}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {status && <span className="text-xs text-green-600">{status}</span>}
          <Toolbar
            editable={editable}
            dirty={draft !== doc.raw}
            editing={editing}
            onToggleEdit={() => (editing ? setEditing(false) : startEdit())}
            onSave={handleSave}
            onCommit={handleCommit}
          />
        </div>
      </div>
      {editing ? <DocEditor value={draft} onChange={setDraft} /> : <DocViewer content={doc.content} />}
    </div>
  );
}
