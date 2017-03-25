import json
import os
from git import Repo


def open_answers(filename):
    with open(filename) as data_file:
        data = json.load(data_file)
    return data

def get_repo_from_git(url, path, filename):

    if os.path.exists(path):
        repo = Repo(path).remotes.origin.pull()
    else:
        Repo.clone_from(url, path)
    for root, dirs, files in os.walk(path):
        print(files)
        if filename in files:
            result = os.path.join(root, filename)

            with open(result) as data_file:
                data = json.load(data_file)
            return data

