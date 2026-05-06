from pathlib import Path

def update_head(data_dir, new_commit_oid):
    head_path = get_head_path(data_dir)
    head_content = None
    try:
        head_content = head_path.read_text().strip()
    except:
        pass

    if head_content:
        # ref: symbolic ref like a refs/heads/main 
        if head_content.startswith("ref: "):
            ref_path = head_content[5:]  # "refs/heads/main"
            full_ref_path = Path(data_dir) / ref_path

            full_ref_path.parent.mkdir(parents=True, exist_ok=True)

            full_ref_path.write_text(new_commit_oid + "\n")
        else:
            # detached HEAD
            head_path.write_text(new_commit_oid + "\n")
    else:
        head_path.write_text(new_commit_oid + "\n")
         

def read_oid_from_head(data_dir):
    head_path = get_head_path(data_dir)
    oid = None
    try:
        head_content = head_path.read_text().strip()
        # ref: symbolic ref like a refs/heads/main 
        if head_content.startswith("ref: "):
            ref_path = head_content[5:]  # "refs/heads/main"
            full_ref_path = Path(data_dir) / ref_path

            full_ref_path.parent.mkdir(parents=True, exist_ok=True)

            oid = full_ref_path.read_text_strip()
        else:
            oid = head_content
    except:
        pass 
    return oid

def get_head_path(data_dir):
    return Path(data_dir) / "HEAD"

# vi: se ts=4 sw=4 et:
