from pathlib import Path

def update_ref_HEAD(data_dir, new_commit_oid):
    head_path = Path(data_dir) / "HEAD"
    head_content = head_path.read_text().strip()

    # ref: symbolic ref like a refs/heads/main 
    if head_content.startswith("ref: "):
        ref_path = head_content[5:]  # "refs/heads/main"
        full_ref_path = Path(data_dir) / ref_path

        full_ref_path.parent.mkdir(parents=True, exist_ok=True)

        full_ref_path.write_text(new_commit_oid + "\n")
    else:
        # detached HEAD
        head_path.write_text(new_commit_oid + "\n")
# vi: se ts=4 sw=4 et:
