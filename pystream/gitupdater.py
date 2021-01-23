import git 
import subprocess
import sys

class GitUpdater:
    def update(path):
        g = git.cmd.Git(path)
        result = g.pull()
        if len(result) > 0:
            subprocess.Popen(args=["python", path + "/media_display_server.py"], cwd = path)
            sys.exit()