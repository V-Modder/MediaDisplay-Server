import git 


def update():
    g = git.cmd.Git("E:\workspace\MediaDisplay")
    result = g.pull()

    x = 0
    