#!/usr/bin/env python3

import argparse
import functools
import os

import imageio

def diffstat(dirs, grid, diffout):
    if len(dirs) < 2:
        print("Less than 2 homepaths given - nothing to compare")
        return
    if grid or diffout:
        assert len(dirs) == 2
    if diffout:
        os.makedirs(diffout, exist_ok=True)
    sdirs = [os.path.join(d, "screenshots") for d in dirs]
    paths = [set(os.listdir(d)) for d in sdirs]
    allpaths = functools.reduce(set.__and__, paths)
    anypaths = functools.reduce(set.__or__, paths)
    for p in sorted(anypaths - allpaths):
        print(p, "not found in all directories")
    print("DIFFS VS.", dirs[0])
    l = max(map(len, allpaths))
    print("%-*s" %(l, "FILENAME"), *("%20s" % d for d in dirs[1:]))
    print("-" * (l + 1 + 20 * (len(dirs) - 1)))
    for p in sorted(allpaths):
        ibase = imageio.imread(os.path.join(sdirs[0], p)).astype(float)
        print("%-*s" % (l, p), end="")
        for idir, d in enumerate(sdirs[1:]):
            icmp = imageio.imread(os.path.join(d, p)).astype(float)
            assert icmp.shape == ibase.shape
            diff = abs(icmp - ibase)
            print(" %20.3g" % (diff.sum() / diff.size), end="")
            if idir + 2 == len(dirs):
                print()
            if diffout:
                imageio.imwrite(os.path.join(diffout, p), diff.astype('uint8'))
            if grid:
                h, w, _ = diff.shape
                rows = max(1, h // 100)
                cols = max(1, w // 100)
                for i in range(rows):
                    i0 = h * i // rows
                    i1 = h * (i+1) // rows
                    for j in range(cols):
                        j0 = w * j // cols
                        j1 = w * (j+1) // cols
                        slice = diff[i0:i1, j0:j1]
                        print(' %8.2f' % (slice.sum() / slice.size), end='')
                    print()
                print()

if "__main__" == __name__:
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--diff-image-out-dir", type=str)
    ap.add_argument("-g", "--grid", action="store_true")
    ap.add_argument("homepath", nargs="*")
    pa = ap.parse_args()
    diffstat(pa.homepath, grid=pa.grid, diffout=pa.diff_image_out_dir)
