import { useState } from "react";
import { Pencil, Save, GitCommitHorizontal, Eye } from "lucide-react";

interface Props {
  editable: boolean;
  dirty: boolean;
  editing: boolean;
  onToggleEdit: () => void;
  onSave: () => void;
  onCommit: () => void;
}

export function Toolbar({ editable, dirty, editing, onToggleEdit, onSave, onCommit }: Props) {
  const [committing, setCommitting] = useState(false);

  if (!editable) {
    return (
      <span className="text-xs text-slate-400">Static site — editing disabled</span>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {!editing ? (
        <button
          onClick={onToggleEdit}
          className="flex items-center gap-1 rounded border px-2 py-1 text-sm hover:bg-slate-100 dark:hover:bg-slate-800"
        >
          <Pencil size={14} /> Edit
        </button>
      ) : (
        <>
          <button
            onClick={onSave}
            disabled={!dirty}
            className="flex items-center gap-1 rounded border px-2 py-1 text-sm hover:bg-slate-100 disabled:opacity-40 dark:hover:bg-slate-800"
          >
            <Save size={14} /> Save
          </button>
          <button
            onClick={onToggleEdit}
            className="flex items-center gap-1 rounded border px-2 py-1 text-sm hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <Eye size={14} /> Preview
          </button>
          <button
            onClick={async () => {
              setCommitting(true);
              try {
                await onCommit();
              } finally {
                setCommitting(false);
              }
            }}
            disabled={committing}
            className="flex items-center gap-1 rounded border px-2 py-1 text-sm hover:bg-slate-100 disabled:opacity-40 dark:hover:bg-slate-800"
          >
            <GitCommitHorizontal size={14} /> {committing ? "Committing…" : "Commit"}
          </button>
        </>
      )}
    </div>
  );
}
