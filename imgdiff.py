import math
import os
import pathlib
import re
import shutil
import subprocess
import sys


def TruncateAngle(s):
    a = float(s)
    ticks = math.trunc(a / 360 * 65536)
    return str(ticks / 65536 * 360)


def PrepareHomepath(p):
    config = os.path.join(p, "config")
    pathlib.Path(config).mkdir(parents=True, exist_ok=True)
    mydir = os.path.dirname(os.path.realpath(__file__))
    for f in os.listdir(mydir):
        if f.endswith(".cfg"):
            shutil.copy(os.path.join(mydir, f), os.path.join(config, f))
        if f.endswith(".scene"):
            with open(os.path.join(mydir, f)) as src:
                text = src.read()
            # assume comment markers won't be escaped or found in strings
            text = re.sub(r"//.*|/\*(.|\n)*?\*/", "", text)
            with open(os.path.join(config, f + ".cfg"), "w") as out:
                for line in text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    m = re.match("(\d+)\s", line)
                    delay = m.group(1)
                    cmd = line[m.end():].lstrip()
                    m = re.match("SVP\s", cmd)
                    if m:
                        x, y, z, yaw, pitch = cmd[m.end():].split()
                        yaw = TruncateAngle(yaw)
                        pitch = TruncateAngle(pitch)
                        cmd = "setviewpos %s %s %s %s %s" % (x, y, z, yaw, pitch)
                    print("exec -q schedule_cmd.cfg", delay, cmd, file=out)
                    print("exec -q schedule_cmd.cfg", file=out)


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
    nospam = os.environ.copy()
    nospam["MSYSTEM"] = "MINGW"
    for i, (path, cmd) in enumerate(zip(paths, cmds)):
        print("Running config #%d: %s" % (i, cmd))
        PrepareHomepath(path)
        subprocess.check_call(cmd, env=nospam)


if __name__ == "__main__":
    Main(sys.argv)
