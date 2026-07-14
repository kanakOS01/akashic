import { Pencil, Save, GitCommitHorizontal, Upload, Eye } from "lucide-react";

interface Props {
  editable: boolean;
  dirty: boolean;
  editing: boolean;
  onToggleEdit: () => void;
  onSave: () => void;
  onOpenCommit: () => void;
  onPush: () => void;
  committing: boolean;
  pushing: boolean;
}

export function Toolbar({ editable, dirty, editing, onToggleEdit, onSave, onOpenCommit, onPush, committing, pushing }: Props) {
  if (!editable) {
    return (
      <span className="text-xs text-[#525252] font-medium">Static site — editing disabled</span>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {!editing ? (
        <>
          <button
            onClick={onToggleEdit}
            className="flex items-center gap-1.5 rounded-lg border border-[#1a1a1a] bg-[#080808] hover:bg-[#151515] text-xs font-semibold text-[#d4d4d8] hover:text-white px-3 py-1.5 transition-all duration-150 active:scale-95"
          >
            <Pencil size={13} className="text-[#525252]" /> Edit
          </button>
          <button
            onClick={onPush}
            disabled={pushing}
            className="flex items-center gap-1.5 rounded-lg border border-[#1a1a1a] bg-[#080808] hover:bg-[#151515] text-xs font-semibold text-[#d4d4d8] hover:text-white px-3 py-1.5 disabled:opacity-40 transition-all duration-150 active:scale-95"
          >
            <Upload size={13} className="text-[#525252]" /> {pushing ? "Pushing…" : "Push"}
          </button>
        </>
      ) : (
        <>
          {/* <button
            onClick={() => {}}
            disabled={!dirty}
            className="flex items-center gap-1.5 rounded-lg border border-emerald-500/20 bg-emerald-500/10 hover:bg-emerald-500/20 text-xs font-semibold text-emerald-400 disabled:opacity-40 disabled:hover:bg-emerald-500/10 px-3 py-1.5 transition-all duration-150 active:scale-95 "
          >
            <Save size={13} /> Save
          </button> */}
          <button
            onClick={onToggleEdit}
            className="flex items-center gap-1.5 rounded-lg border border-[#1a1a1a] bg-[#080808] hover:bg-[#151515] text-xs font-semibold text-[#d4d4d8] hover:text-white px-3 py-1.5 transition-all duration-150 active:scale-95"
          >
            <Eye size={13} className="text-[#525252]" /> View
          </button>
          <button
            onClick={onOpenCommit}
            disabled={!dirty || committing}
            className="flex items-center gap-1.5 rounded-lg border border-[#1a1a1a] bg-[#080808] hover:bg-[#151515] text-xs font-semibold text-[#d4d4d8] hover:text-white px-3 py-1.5 disabled:opacity-40 transition-all duration-150 active:scale-95"
          >
            <GitCommitHorizontal size={13} className="text-[#525252]" /> {committing ? "Committing…" : "Commit"}
          </button>
          <button
            onClick={onPush}
            disabled={pushing}
            className="flex items-center gap-1.5 rounded-lg border border-[#1a1a1a] bg-[#080808] hover:bg-[#151515] text-xs font-semibold text-[#d4d4d8] hover:text-white px-3 py-1.5 disabled:opacity-40 transition-all duration-150 active:scale-95"
          >
            <Upload size={13} className="text-[#525252]" /> {pushing ? "Pushing…" : "Push"}
          </button>
        </>
      )}
    </div>
  );
}

