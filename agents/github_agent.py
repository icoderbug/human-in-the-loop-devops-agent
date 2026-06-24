from github import Github

import os
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

g = Github(GITHUB_TOKEN)

def get_repo_readme(repo_name):

    repo = g.get_repo(repo_name)

    file = repo.get_contents("README.md")

    content = file.decoded_content.decode()

    return content