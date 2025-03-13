#!/usr/bin/env python3

import os
import re
import shutil
import sys


_, name, srcdir = sys.argv
files = os.listdir(srcdir)
if 'daemon' not in files and 'daemon.exe' not in files:
    raise Exception("daemon executable not found in" + srcdir)
mydir = os.path.dirname(os.path.realpath(__file__))
dstdir = os.path.join(mydir, "x", name)
os.makedirs(dstdir, exist_ok=True)

bins = re.compile(
    "((daemon|crash_server|nacl_loader.*|[cs]game-native-exe)([.]exe)?|.*(?<!-stripped)[.](dll|nexe|so|dylib)|nacl_helper_bootstrap|nacl_loader-amd64[.].nexe)$")
for f in files:
    if re.match(bins, f):
        shutil.copy2(os.path.join(srcdir, f), dstdir)
