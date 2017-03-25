import json
import os

from git import Repo

from django.conf import settings


def open_answers(filename):
    with open(filename) as data_file:
        data = json.load(data_file)
    return data


def get_repo_from_git(url=None, path=None, filename=None):
    if not url:
        url = settings.DATA_REPOSITORY_URL
    if not path:
        path = settings.REPOSITORY_PATH
    if not filename:
        filename = settings.DATA_FILENAME

    if os.path.exists(path):
        Repo(path).remotes.origin.pull()
    else:
        Repo.clone_from(url, path)

    for root, dirs, files in os.walk(path):
        print(files)
        if filename in files:
            result = os.path.join(root, filename)

            with open(result) as data_file:
                data = json.load(data_file)
            return data

