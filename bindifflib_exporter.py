from idaapi import *
from idc import *
from idautils import *
import sys


def main():
    # Wait for auto-analysis
    Wait()

    # setup netnode values
    n = netnode("$ pdb")
    n.altset(0, get_imagebase())
    n.supset(0, get_plugin_options("bindifflib"))

    # load pdb file
    RunPlugin("pdb", 3)

    # close IDA
    Exit(0)

if __name__ == "__main__":
    main()
