import functools
import os
import sys

import imageio

def diffstat(dirs):
    if len(dirs) < 2:
        print("Less than 2 homepaths given - nothing to compare")
        return
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
        nums = []
        for d in sdirs[1:]:
            icmp = imageio.imread(os.path.join(d, p)).astype(float)
            assert icmp.shape == ibase.shape
            nums.append(abs(icmp - ibase).sum() / ibase.size)
        print("%-*s" % (l, p), *("%20.3g" % x for x in nums))

if "__main__" == __name__:
    diffstat(sys.argv[1:])
