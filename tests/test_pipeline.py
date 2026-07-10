import git
from pathlib import Path
from knowledge_engine.pipeline import run as run_pipeline
from backend.app.config import get_projects

def test_pipeline_runs_and_preserves_human_block(setup_test_config):
    """
    Integration test asserting that the pipeline completes successfully,
    writes correct markdown pages, initializes git commits, and preserves human notes.
    """
    _, knowledge_dir, workspace_dir = setup_test_config
    projects = get_projects()
    project = projects["sample"]

    # 1. First run of the pipeline
    page = run_pipeline(project, workspace_dir, knowledge_dir)
    
    # Assert return models look correct
    assert page.frontmatter["generated"] is True
    assert page.frontmatter["repo"] == project.repo
    assert "sample-service" in page.body
    assert "express" in page.body
    
    # Verify file saved on disk
    target_file = knowledge_dir / "services" / "sample.md"
    assert target_file.exists()
    file_content_1 = target_file.read_text(encoding="utf-8")
    assert "<!-- HUMAN START -->" in file_content_1
    assert "<!-- HUMAN END -->" in file_content_1

    # Verify Git commit was triggered
    repo = git.Repo(knowledge_dir)
    assert not repo.is_dirty()
    assert "Sync project: sample" in repo.head.commit.message

    # 2. Modify the file simulating a developer writing manual annotations
    custom_notes = "\n# Extra Notes\nDeveloper note here.\n"
    start_tag = "<!-- HUMAN START -->"
    instruction_tag = "<!-- Feel free to add manual notes or overrides below this line. They will be preserved on sync. -->"
    
    # Inject custom notes inside the human block
    target_block = f"{start_tag}\n{instruction_tag}\n"
    replacement_block = f"{start_tag}{custom_notes}"
    
    modified_content = file_content_1.replace(target_block, replacement_block)
    target_file.write_text(modified_content, encoding="utf-8")

    # Commit the modification manually to clean workspace if needed, 
    # though is_dirty check is handled inside pipeline.
    
    # 3. Re-run pipeline
    page_run_2 = run_pipeline(project, workspace_dir, knowledge_dir)
    file_content_2 = target_file.read_text(encoding="utf-8")
    
    # Assert custom notes survived
    assert custom_notes in file_content_2
    # Assert generated documentation was refreshed
    assert "sample-service" in file_content_2
