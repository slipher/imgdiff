import os
import pathlib
import re
import shutil
import subprocess
import sys


def PrepareHomepath(p):
    config = os.path.join(p, "config")
    pathlib.Path(config).mkdir(parents=True, exist_ok=True)
    mydir = os.path.dirname(os.path.realpath(__file__))
    for f in os.listdir(mydir):
        if f.endswith(".cfg"):
            shutil.copy(os.path.join(mydir, f), os.path.join(config, f))


# TODO: alternate version with the whole command line in 1 arg and shell=True (without -- maybe?)
def FormCommands(cmdt, paths):
    ARGSEP = "\0"
    cmdt = ARGSEP.join(cmdt)
    cmds = [""] * len(paths)
    inject_alts = ["-homepath" + ARGSEP + p for p in paths]
    injected = False
    while '{' in cmdt:
        i = cmdt.index('{')
        cmds = [c + cmdt[:i] for c in cmds]
        j = cmdt.index('}', i)
        if j == i+1:
            alts = inject_alts
            injected = True
        else:
            alts = cmdt[i+1:j].split('|')
            if len(alts) != len(paths):
                raise Exception(repr(cmdt[i:j+1]) + " has wrong number of alternatives")
        cmds = [c + a for c,a in zip(cmds, alts)]
        cmdt = cmdt[j+1:]
    if not injected:
        raise Exception("command must contain '{}' at a position suitable to inject daemon -args")
    return [(c + cmdt).split(ARGSEP) for c in cmds]


def Main(args):
    isep = args.index("--")
    paths = [os.path.abspath(p) for p in args[1:isep]]
    cmds = FormCommands(args[isep+1:], paths)
    for i, (path, cmd) in enumerate(zip(paths, cmds)):
        print("Running config #%d: %s" % (i, cmd))
        PrepareHomepath(path)
        subprocess.check_call(cmd)


if __name__ == "__main__":
    Main(sys.argv)
