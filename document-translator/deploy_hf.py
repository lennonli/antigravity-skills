import os
import sys
from huggingface_hub import HfApi

TOKEN = "hf_token_removed_for_security"
api = HfApi(token=TOKEN)

SPACE_NAME = "doc-translator"
ZHIPU_API_KEY = "774e1727547445519776afe760130fd5.SjqEECRFt3unPPsR"
ACCESS_CODE = "668899"
FOLDER_PATH = "/Users/licheng/.gemini/antigravity/skills/document-translator"

try:
    print("Authenticating...")
    user_info = api.whoami()
    username = user_info["name"]
    repo_id = f"{username}/{SPACE_NAME}"
    
    print(f"Creating Space: {repo_id}")
    api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker", private=False, exist_ok=True)
    
    print("Configuring Secrets...")
    api.add_space_secret(repo_id, "ZHIPU_API_KEY", ZHIPU_API_KEY)
    if ACCESS_CODE:
        api.add_space_secret(repo_id, "ACCESS_CODE", ACCESS_CODE)
        
    print(f"Uploading files from {FOLDER_PATH}...")
    api.upload_folder(
        folder_path=FOLDER_PATH,
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=["temp_uploads/*", "__pycache__/*", "*.zip", ".git/*", "deploy_hf.py", "test_numbering.py*"]
    )
    
    print("Deployment successful!")
    print(f"Your app will be live at: https://huggingface.co/spaces/{repo_id}")
    
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
