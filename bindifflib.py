import yaml
import argparse
import os
from glob import glob
from concurrent.futures import ProcessPoolExecutor, as_completed

from modules.handler import LibHandler
from modules.buildwrapper import BuildWrapper
from modules.dependency import DependencyHelper
from modules.ida import IDAHelper


def main():
    """ main function """

    # find necessary executable files
    cmakePath = find(["C:\\Program Files\\CMake\\bin\\cmake.exe",
                      "C:\\Program Files (x86)\\CMake\\bin\\cmake.exe"])
    idaq = find(["C:\\Program Files (x86)\\IDA 6.95\\idaq.exe"])
    idaq64 = find(["C:\\Program Files (x86)\\IDA 6.95\\idaq64.exe"])

    # setup argsparse
    parser = argparse.ArgumentParser(description="""Load libraries from internet
        and compile them with as much different VS versions as you can find on
        the system.""")
    parser.add_argument("cmake", metavar="<path to cmake executable>", type=str,
                        help="path to cmake executable", nargs="?" if cmakePath else 1,
                        default=cmakePath if cmakePath else None)
    parser.add_argument("idaq", metavar="<path to idaq executable>", type=str,
                        help="path to idaq executable", nargs="?" if idaq else 1,
                        default=idaq if idaq else None)
    parser.add_argument("idaq64", metavar="<path to idaq64 executable>", type=str,
                        help="path to idaq64 executable", nargs="?" if idaq64 else 1,
                        default=idaq64 if idaq64 else None)
    parser.add_argument("compilers", metavar="<compilers.yml>", type=str, nargs="?",
                        help="yml file containing a list of compilers to use",
                        default="compilers.yml")
    parser.add_argument("lists", metavar="<libs.yml>", type=str, nargs="*",
                        help="yml file containing a list of libraries",
                        default=["libs.yml"])
    args = parser.parse_args()

    # building without CMake is not supported
    if not args.cmake:
        print("No CMake executable found. Exitting.")
        return

    # analyzing without IDA does not make sense
    if not args.idaq:
        print("No idaq.exe found. Exitting.")
        return

    # setup the path prefixes
    tmpPrefix = "tmp/"
    cachePrefix = tmpPrefix + "cache/"
    extractedPrefix = tmpPrefix + "extracted/"
    buildPrefix = tmpPrefix + "build/"
    binPrefix = tmpPrefix + "bin/"
    customCmakePrefix = "cmake/"

    # create all needed directories
    if not os.path.exists(tmpPrefix):
        os.mkdir(tmpPrefix)
    if not os.path.exists(cachePrefix):
        os.mkdir(cachePrefix)
    if not os.path.exists(extractedPrefix):
        os.mkdir(extractedPrefix)
    if not os.path.exists(buildPrefix):
        os.mkdir(buildPrefix)
    if not os.path.exists(binPrefix):
        os.mkdir(binPrefix)

    # instanciate the library handler
    libHandler = LibHandler(cachePrefix=cachePrefix,
                            extractedPrefix=extractedPrefix,
                            buildPrefix=buildPrefix,
                            binPrefix=binPrefix,
                            customCmakePrefix=customCmakePrefix)

    # load the compiler config
    compilers = yaml.load(open(args.compilers, "rb").read())

    # load artifactory settings
    artifactoryData = yaml.load(
        open("settings.yml", "rb").read())
    artifactoryPath = artifactoryData.get("artifactory_path", None)
    artifactoryUser = artifactoryData.get("artifactory_user", "")
    artifactoryPass = artifactoryData.get("artifactory_pass", "")

    # iterate over all input files and parse the libraries into the cache
    for file in args.lists:
        libHandler.addFile(file)

    # get the library cache from the handler and resolve the dependencies
    libs = libHandler.getLibs()
    resolved = DependencyHelper(libs).resolve()

    print("Compiling all libraries...")

    # because of the dependencies, we only allow the build processes to use
    # one core per compiler so that we have linear execution
    with BuildWrapper(internals=resolved, libs=libs) as wrapper:
        with ProcessPoolExecutor(max_workers=len(compilers)) as executor:
            tasks = list()
            for name, compiler in compilers.items():
                # emit compile task to pool
                t = executor.submit(wrapper.compileFor, compiler, args.cmake)
                tasks.append(t)

            for future in as_completed(tasks):
                if future.exception() is not None:
                    print("exception: {}".format(future.exception()))

    print("Compilation done, starting export for all dlls.")

    # finally, we need to hand all files over to IDA so that it can
    # analyze them for us; this time, we fire off all tasks at once
    # because IDA does not depend on anything and we need to get
    # things done
    with ProcessPoolExecutor() as executor:
        d = dict()

        for dll, pdb in globfiles(binPrefix):
            idahelper = IDAHelper(dll=dll, pdb=pdb,
                                  idaq=idaq, idaq64=idaq64,
                                  artifactoryPath=artifactoryPath,
                                  auth=(artifactoryUser, artifactoryPass))
            # emit analysis task to pool
            t = executor.submit(idaPoolExecutionHelper, idahelper)
            d[t] = idahelper

        for future in as_completed(d):
            idahelper = d[future]
            if future.exception() is not None:
                print("error creating idb for {}: {}".format(
                    idahelper.dll, future.exception()))

    print("Export done.")

    return


def globfiles(path):
    """ Scans the binary directory for any DLL that have not
        yet been anaylized by IDA.
    """
    pdbs = glob(path + "/*/bin/*.pdb")
    idbs = glob(path + "/*/bin/*.idb")
    i64s = glob(path + "/*/bin/*.i64")
    dlls = glob(path + "/*/bin/*.dll")

    for dll in dlls:
        idb = dll.replace(".dll", ".idb")
        i64 = dll.replace(".dll", ".i64")
        pdb = dll.replace(".dll", ".pdb")

        if (idb not in idbs) and (i64 not in i64s) and (pdb in pdbs):
            yield (dll, pdb)


def find(where):
    """ Checks if any of the given paths exists and returns the first finding. """
    for path in where:
        if os.path.exists(path):
            return path
    else:
        return None


def idaPoolExecutionHelper(ida):
    """ Helper function to avoid crashing the whole pool execution
        if any of the tasks fails.
    """
    try:
        print("Creating IDB file for {}...".format(ida.dll))
        ida.makeidb()
        ida.storeresult()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
