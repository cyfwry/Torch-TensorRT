import os
import json
from github import Github
import subprocess

token = os.environ['GITHUB_TOKEN']
gh = Github(token)

event_file_path = os.environ['GITHUB_EVENT_PATH']
with open(event_file_path, 'r') as f:
    j = f.read()
    event = json.load(j)

repo_name = event["repository"]["full_name"]
pr_number = event["number"]
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)
commit = repo.get_commit(pr.base.sha)

output = subprocess.run(["bazel", "run", "//tools/linter:cpplint_diff", "--", "--no-color", "//..."], stdout=subprocess.PIPE)

comment = '''Code conforms to C++ style guidelines'''
approval = 'APPROVE'
if output.returncode != 0:
    comment = '''There are some changes that do not conform to C++ style guidelines:\n ```diff\n{}```'''.format(output.stdout.decode("utf-8"))
    approval = 'REQUEST_CHANGES'

pr.create_review(commit, comment, approval)


