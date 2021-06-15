from autohander import hander
import sys


argvs = sys.argv
print("starting with argvs:", argvs)
if len(argvs) < 2:
    print("need a json for all setting")
else:
    hander(argvs[1])
