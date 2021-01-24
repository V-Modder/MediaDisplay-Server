from git import Repo, Remote, FetchInfo
import subprocess
import sys

class GitUpdater:
    def update(path):
        try:
            repo = Repo(path)
            remote = repo.remotes[0]
            fetchInfos = remote.pull()
            if len(fetchInfos) > 0 and fetchInfos[0].flags & FetchInfo.NEW_HEAD & FetchInfo.FAST_FORWARD > 0:
                subprocess.Popen(args=["python", path + "/media_display_server.py"], cwd = path)
                sys.exit()
        except Exception as e:
            print(e)
