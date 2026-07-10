from knowledge_engine.models.service import Service
from knowledge_engine.models.knowledge_page import KnowledgePage
from knowledge_engine.llm.summarize import summarize
from knowledge_engine.compiler.frontmatter import to_frontmatter
from knowledge_engine.compiler.templates import TEMPLATE
from typing import List

def compile_page(
    service: Service,
    updated: str,
    repo_path_or_url: str,
    source_files: List[str],
    existing_content: str | None = None
) -> KnowledgePage:
    """
    Compile a Service IR into a KnowledgePage, preserving any human annotations.
    """
    # 1. Extract human notes from existing content
    start_tag = "<!-- HUMAN START -->"
    end_tag = "<!-- HUMAN END -->"
    
    human_notes = "\n<!-- Feel free to add manual notes or overrides below this line. They will be preserved on sync. -->\n"
    
    if existing_content:
        start_idx = existing_content.find(start_tag)
        end_idx = existing_content.find(end_tag)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            # Extract everything in between
            human_notes = existing_content[start_idx + len(start_tag) : end_idx]

    # 2. Build frontmatter
    frontmatter = {
        "generated": True,
        "repo": repo_path_or_url,
        "updated": updated,
        "sources": [str(f) for f in source_files]
    }
    frontmatter_str = to_frontmatter(frontmatter)

    # 3. Generate body via LLM stub
    generated_body = summarize(service)

    # 4. Construct page using the template
    # Since we extract human_notes including newlines, let's keep it clean
    page_content = TEMPLATE.format(
        frontmatter=frontmatter_str,
        generated_body=generated_body.strip(),
        human_notes=human_notes
    )

    # Path to the page relative to the knowledge/ directory (or absolute, handled by caller)
    # The pipeline will write it to knowledge/services/{name}.md
    path = f"services/{service.name}.md"

    return KnowledgePage(
        path=path,
        frontmatter=frontmatter,
        body=page_content
    )
