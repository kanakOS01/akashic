export interface Frontmatter {
  title?: string;
  type?: string;
  summary?: string;
  description?: string;
  source_repositories?: string[];
  generated_at?: string;
  [key: string]: unknown;
}

export interface NavItem {
  path: string;
  title: string;
  type: string;
}

export interface NavSection {
  id: string;
  title: string;
  items: NavItem[];
}

export interface IndexEntry {
  path: string;
  title: string;
  section: string;
  type: string;
  summary: string;
  tags: string[];
  updated: string;
}

export interface NavTree {
  home: string;
  sections: NavSection[];
  index: IndexEntry[];
}

export interface DocRecord {
  path: string;
  title: string;
  type: string;
  frontmatter: Frontmatter;
  content: string;
  raw: string;
}

export interface Meta {
  mode: "live" | "static";
  editable: boolean;
  gitAvailable: boolean;
  kbRoot: string;
  port: number;
}

export interface Snapshot {
  mode: "static";
  home: string;
  sections: NavSection[];
  index: IndexEntry[];
  docs: Record<string, DocRecord>;
}
