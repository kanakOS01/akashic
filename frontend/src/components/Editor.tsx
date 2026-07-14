import Editor from "@monaco-editor/react";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export function DocEditor({ value, onChange }: Props) {
  return (
    <div className="h-[70vh] border rounded">
      <Editor
        height="100%"
        defaultLanguage="markdown"
        theme="vs-dark"
        value={value}
        onChange={(v) => onChange(v ?? "")}
        options={{ minimap: { enabled: false }, wordWrap: "on", lineNumbers: "on" }}
      />
    </div>
  );
}
