import os
import git

def splitall(path):
    allparts = []

    path, suffix = os.path.splitext(path)
    if suffix:
        allparts.append(suffix)

    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])

    return allparts


def get_commit_by_sha(repo, sha):
    for c in repo.iter_commits():
        if c.hexsha == sha:
            return c

    return None