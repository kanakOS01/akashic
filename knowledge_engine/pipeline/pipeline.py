import datetime
from pathlib import Path
from knowledge_engine.models.project import Project
from knowledge_engine.models.service import Service
from knowledge_engine.models.knowledge_page import KnowledgePage
from knowledge_engine.repository.manager import prepare, discover_files
from knowledge_engine.extraction.readme import ReadmeExtractor
from knowledge_engine.extraction.package import PackageExtractor
from knowledge_engine.compiler.markdown import compile_page
from knowledge_engine.git.sync import commit, ensure_repo

def run(project: Project, workspace_dir: Path, knowledge_dir: Path) -> KnowledgePage:
    """
    Run the extraction and compilation pipeline for a project:
    0. Ensure the knowledge git repository is initialized
    1. Prepare/checkout repository
    2. Discover files
    3. Run extractors and merge partial facts
    4. Compile page while preserving human annotations
    5. Write compiled page to target directory
    6. Git commit changes in the knowledge directory
    """
    # 0. Ensure git repo exists before writing files
    ensure_repo(knowledge_dir)

    # 1. Prepare
    repo_path = prepare(project, workspace_dir)
    
    # 2. Discover files
    files = discover_files(repo_path)
    
    # 3. Extract and merge facts
    readme_extractor = ReadmeExtractor()
    package_extractor = PackageExtractor()
    
    readme_facts = readme_extractor.extract(repo_path)
    package_facts = package_extractor.extract(repo_path)
    
    # Prioritize extracted name, default to project configured name
    name = readme_facts.get("name") or package_facts.get("name") or project.name
    description = readme_facts.get("description") or "No description provided."
    depends_on = package_facts.get("depends_on") or []
    
    # Convert source files to relative paths for serialization in frontmatter
    source_files = []
    for f in files:
        try:
            source_files.append(str(f.relative_to(repo_path)))
        except ValueError:
            source_files.append(str(f))
            
    service = Service(
        name=name,
        description=description,
        depends_on=depends_on,
        emits_events=[],
        consumes_events=[],
        apis=[],
        source_files=source_files
    )

    # 4. Check for existing file to preserve human notes
    target_path = knowledge_dir / "services" / f"{project.name}.md"
    existing_content = None
    if target_path.exists():
        try:
            existing_content = target_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: could not read existing page {target_path} to preserve human notes: {e}")

    # 5. Compile
    updated_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    page = compile_page(
        service=service,
        updated=updated_str,
        repo_path_or_url=project.repo,
        source_files=source_files,
        existing_content=existing_content
    )

    # 6. Save target page
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(page.body, encoding="utf-8")

    # 7. Commit changes to git knowledge base
    commit(knowledge_dir, f"Sync project: {project.name}")

    return page
