import { useState } from "react";

interface Props {
  open: boolean;
  onClose: () => void;
  onSubmit: (message: string) => void;
}

export function CommitDialog({ open, onClose, onSubmit }: Props) {
  const [message, setMessage] = useState("");

  if (!open) return null;

  const handleSubmit = () => {
    onSubmit(message || `docs: update via Akashic site`);
    setMessage("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-[#0c0c0c] border border-[#1a1a1a] rounded-xl shadow-2xl w-full max-w-md p-6">
        <h2 className="text-sm font-semibold text-white mb-1">Commit changes</h2>
        <p className="text-xs text-[#525252] mb-4">Write a commit message describing your changes.</p>
        <input
          autoFocus
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") handleSubmit(); if (e.key === "Escape") onClose(); }}
          placeholder="docs: update ..."
          className="w-full bg-[#050505] border border-[#1a1a1a] rounded-lg px-3 py-2 text-sm text-white placeholder-[#525252] outline-none focus:border-emerald-500/40 transition-colors mb-5"
        />
        <div className="flex items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="text-xs font-semibold text-[#525252] hover:text-white px-3 py-1.5 rounded-lg hover:bg-[#151515] transition-all duration-150"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            className="text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 px-4 py-1.5 rounded-lg transition-all duration-150 active:scale-95"
          >
            Commit
          </button>
        </div>
      </div>
    </div>
  );
}
