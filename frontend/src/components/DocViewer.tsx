import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import type { Components } from "react-markdown";
import { MermaidChart } from "./MermaidChart";

// Helper to extract plain text recursively from React children
function getChildrenText(children: any): string {
  if (!children) return "";
  if (typeof children === "string") return children;
  if (typeof children === "number") return String(children);
  if (Array.isArray(children)) return children.map(getChildrenText).join("");
  if (children.props && children.props.children) return getChildrenText(children.props.children);
  return "";
}

// Generate a valid HTML ID from a string
function makeId(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-");
}

const components: Components = {
  h1({ children }) {
    const text = getChildrenText(children);
    return <h1 id={makeId(text)} className="scroll-mt-24 text-white font-bold tracking-tight">{children}</h1>;
  },
  h2({ children }) {
    const text = getChildrenText(children);
    return <h2 id={makeId(text)} className="scroll-mt-24 text-white font-bold tracking-tight">{children}</h2>;
  },
  h3({ children }) {
    const text = getChildrenText(children);
    return <h3 id={makeId(text)} className="scroll-mt-24 text-white font-semibold tracking-tight">{children}</h3>;
  },
  h4({ children }) {
    const text = getChildrenText(children);
    return <h4 id={makeId(text)} className="scroll-mt-24 text-white font-semibold tracking-tight">{children}</h4>;
  },
  code({ className, children, ...props }) {
    const match = /language-(\w+)/.exec(className ?? "");
    const text = String(children).replace(/\n$/, "");
    if (match && match[1] === "mermaid") {
      return <MermaidChart code={text} />;
    }
    if (match) {
      return (
        <div className="my-5 overflow-hidden rounded-lg border border-[#1a1a1a] bg-[#0a0a0a]">
          <SyntaxHighlighter
            language={match[1]}
            style={oneDark}
            customStyle={{
              margin: 0,
              padding: "1.25rem",
              background: "transparent",
              fontSize: "0.875rem",
            }}
            PreTag="div"
          >
            {text}
          </SyntaxHighlighter>
        </div>
      );
    }
    return (
      <code className="rounded bg-[#0d0d0d] px-1.5 py-0.5 font-mono text-sm border border-[#1a1a1a] text-[#e4e4e7]" {...props}>
        {children}
      </code>
    );
  },
  table({ children }) {
    return (
      <div className="my-6 overflow-x-auto rounded-lg border border-[#1a1a1a] bg-black">
        <table className="w-full border-collapse text-left text-sm text-[#a1a1aa]">
          {children}
        </table>
      </div>
    );
  },
  thead({ children }) {
    return <thead className="border-b border-[#1a1a1a] bg-[#0a0a0a] text-white font-semibold">{children}</thead>;
  },
  tbody({ children }) {
    return <tbody className="divide-y divide-[#1a1a1a]">{children}</tbody>;
  },
  tr({ children }) {
    return <tr className="hover:bg-[#0a0a0a] transition-colors">{children}</tr>;
  },
  th({ children }) {
    return <th className="px-4 py-3 font-semibold">{children}</th>;
  },
  td({ children }) {
    return <td className="px-4 py-3 font-normal text-[#d4d4d8]">{children}</td>;
  },
  blockquote({ children }) {
    return (
      <blockquote className="my-6 border-l-4 border-emerald-500 bg-emerald-500/5 px-5 py-4 rounded-r-lg text-[#a1a1aa] italic">
        {children}
      </blockquote>
    );
  },
};

export function DocViewer({ content }: { content: string }) {
  return (
    <article className="prose max-w-none">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </article>
  );
}
