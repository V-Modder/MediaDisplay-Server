import git 
import subprocess

class GitUpdater:
    def update(path):
        g = git.cmd.Git(path)
        result = g.pull()
        if len(result) > 0:
            subprocess.run(args=[(path / "media_display_server.py")])