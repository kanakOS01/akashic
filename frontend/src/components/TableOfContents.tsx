import { useEffect, useState } from "react";

interface HeadingItem {
  id: string;
  text: string;
  level: number;
}

export function TableOfContents({ content }: { content: string }) {
  const [headings, setHeadings] = useState<HeadingItem[]>([]);
  const [activeId, setActiveId] = useState<string>("");

  useEffect(() => {
    // Parse markdown headings (lines starting with ## or ###)
    const headingRegex = /^(#{2,3})\s+(.+)$/gm;
    const items: HeadingItem[] = [];
    let match;
    while ((match = headingRegex.exec(content)) !== null) {
      const level = match[1].length;
      const text = match[2].trim();
      const id = text
        .toLowerCase()
        .replace(/[^\w\s-]/g, "")
        .replace(/\s+/g, "-");
      items.push({ id, text, level });
    }
    setHeadings(items);
  }, [content]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        // Find the element closest to the top of the viewport
        const visibleEntries = entries.filter((entry) => entry.isIntersecting);
        if (visibleEntries.length > 0) {
          // Sort by top coordinate to get the highest one in view
          visibleEntries.sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
          setActiveId(visibleEntries[0].target.id);
        }
      },
      { rootMargin: "-80px 0px -70% 0px" }
    );

    headings.forEach((heading) => {
      const element = document.getElementById(heading.id);
      if (element) observer.observe(element);
    });

    return () => {
      headings.forEach((heading) => {
        const element = document.getElementById(heading.id);
        if (element) observer.unobserve(element);
      });
    };
  }, [headings]);

  if (headings.length === 0) return null;

  return (
    <div className="space-y-4 py-2">
      <div className="text-xs font-semibold uppercase tracking-wider text-[#525252]">
        On this page
      </div>
      <ul className="space-y-3 border-l border-[#1a1a1a] pl-px">
        {headings.map((heading) => (
          <li key={heading.id} className="group">
            <a
              href={`#${heading.id}`}
              onClick={(e) => {
                e.preventDefault();
                const element = document.getElementById(heading.id);
                if (element) {
                  const offset = 90; // Header offset
                  const bodyRect = document.body.getBoundingClientRect().top;
                  const elementRect = element.getBoundingClientRect().top;
                  const elementPosition = elementRect - bodyRect;
                  const offsetPosition = elementPosition - offset;

                  window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                  });
                  setActiveId(heading.id);
                }
              }}
              className={`block -ml-px border-l pl-4 py-0.5 text-xs transition-all duration-150 ${
                activeId === heading.id
                  ? "border-emerald-500 text-emerald-400 font-medium"
                  : "border-transparent text-[#d4d4d8] group-hover:text-white group-hover:border-[#333333]"
              } ${heading.level === 3 ? "pl-8" : ""}`}
            >
              {heading.text}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
