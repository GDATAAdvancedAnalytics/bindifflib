import subprocess
import os
import shutil
from glob import glob
from tempfile import mkstemp
from .dependency import Internal


class BuildWrapper(object):
    """
    Encapsulates the build process to provide an easy-to-use
    interface for the whole compilation.
    """

    def __init__(self, internals=[], isDependencyWrapper=False,
                 dependencyList=None, libs=None):
        super(BuildWrapper, self).__init__()
        self._internals = internals
        self._libs_orig = libs
        self._isDependencyWrapper = isDependencyWrapper

        if isDependencyWrapper:
            tmp = []
            for name, version in dependencyList.items():
                tmp.append(
                    Internal(lib=libs[name][version],
                             name=name, version=version))
            self._internals = tmp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def binPaths(self):
        return self._binPaths

    def compileFor(self, compiler, cmake):
        self._binPaths = []

        libs = dict(self._libs_orig)
        for item in self._internals:
            Task(item, compiler, libs).compile(
                cmake=cmake, isDep=self._isDependencyWrapper)
            self._binPaths.append(item.lib["binpath"])


class Task(object):
    """ Encapsulates the compile process of a single library. """

    def __init__(self, meta, compiler, libs):
        """
        Initializes a compile task.

        :param meta: all meta information of the library, as provided in libs.yml
        :param compiler: information about the compiler, as provided in compilers.yml
        :param libs: the global dictionary of libraries for the given compiler,
            used to determine which library has already been built to skip possible
            dependency compilation.
        """
        super(Task, self).__init__()
        self._meta = meta
        self._basepath = os.getcwd() + "/"
        self._compiler = compiler
        self._libs = libs

    @property
    def name(self):
        """ Returns the name of the library."""
        return self._meta.name

    @property
    def version(self):
        """ Returns the version of the library."""
        return self._meta.version

    @property
    def compiler(self):
        """ Returns the current compiler."""
        return self._compiler

    @property
    def lib(self):
        """ Returns the metadata of the library."""
        return self._meta.lib

    def _updateLibList(self, buildpath, binpath):
        """ Updates the realtive paths in the global library list to
            absolute paths so that we are immune against wrong
            working directories.

            :param buildpath: path to the directory where the build
                process will happen
            :param binpath: path to the directory where the binaries
                will be stored
        """
        self._libs[self.name][self.version]["buildpath"] = buildpath
        self._libs[self.name][self.version]["binpath"] = binpath

    def _setSuccessfulBuild(self, success):
        """ Set the build status of the current library."""
        self._libs[self.name][self.version]["built"] = success

    def _checkBuildFolderPopulated(self):
        """ Checks whether there are already some DLLs present in the
            binpath. This allows for skipping the build process if it
            already happened before the current instance of the script
            was run.
        """
        binpath = self._libs[self.name][self.version]["binpath"]
        if os.path.exists(binpath):
            dlls = glob(binpath + "/bin/*.dll")
            if dlls is not None:
                return True
            else:
                return False

    def _formatCommand(self, cmd, binpath, extractedpath, buildpath):
        """ Formats a given command so that we can apply
            dynamic paths and variables at compile time.
            Allowed format specifiers:
            - vcvarsall:     absolute path of the vcvarsall.bat file
                             of the current compiler
            - compiler:      the short name of the current compiler
            - name:          the name of the current library
            - version:       the current version of the library
            - binpath:       the full path to the directory where the
                             built binaries will be stored
            - extractedpath: the full path to the source files
            - buldpath:      the full path to the build directory

            :param cmd: the command that is to be formatted
            :param binpath: the full path to the doirectory where the binaries
                will be stored
            :param extractedpath: the full path to the source files
            :param buildpath: the full path to the build directory
        """
        return cmd.format(
            vcvarsall=self.compiler["vcvarsall"],
            compiler=self.compiler["short"],
            compiler_version=self.compiler["version"],
            name=self.name,
            version=self.version,
            binpath=binpath,
            extractedpath=extractedpath,
            buildpath=buildpath
        )

    def compile(self, cmake="", isDep=False):
        """ Launches the actual compilation. Depending on if a custom
            build script was put into the libs.yml file it either executes
            those steps in a batch file or launches CMake.
            Also, if the current library has dependencies, this will be taken
            into consideration and the dependencies will be built first. The
            dependency resolution is transitive - if a dependency has another
            dependency, it we be built first

        :param cmake: the absolute path to the CMake executable. Works around
            a possible crash if the CMake executable is not in %PATH%.
        :param isDep: (optional) denotes of the current library is a dependency
            build of another library. Only used for console output.
            Default: False
        """

        # construct abolsute paths for all needed directories
        buildpath = (self._basepath + self.lib["buildpath"] +
                     "_" + self.compiler["short"])
        extractedpath = self._basepath + self.lib["extractedpath"]
        binpath = (self._basepath + self.lib["binpath"] +
                   "_" + self.compiler["short"])

        # skip if it was marked as already built
        if self._libs[self.name][self.version]["built"]:
            return

        # skip if we have a 64bit compiler and 64bit builds are not allowed
        if self.lib["64bit"] is False and "x64" in self.compiler["short"]:
            return

        # apply absolute paths to the global list
        self._updateLibList(buildpath, binpath)

        # check, whether the library was built outside or before the execution
        # of this instance of the script; if so: skip
        if self._checkBuildFolderPopulated() is True:
            print("{}-{}_{} already built.".format(
                self.name, self.version, self.compiler["short"]))
            self._setSuccessfulBuild(success=True)
            return

        # check for possible dependencies, they need to be built first
        dependencyBinPaths = []
        if self.lib["dependencies"] is not None:
            # build all dependencies
            with BuildWrapper(
                    dependencyList=self.lib["dependencies"],
                    isDependencyWrapper=True, libs=self._libs) as wrapper:
                wrapper.compileFor(self.compiler, cmake)
                # apply the binary paths of all dependencies so that
                # we can set proper include  and lib directories
                dependencyBinPaths = wrapper.binPaths

        print("Compiling {}{}-{}_{}".format(
            "dependency " if isDep else "", self.name,
            self.version, self.compiler["short"]))

        # make sure all directories exist
        if not os.path.exists(buildpath):
            os.mkdir(buildpath)
        if not os.path.exists(binpath):
            os.mkdir(binpath)

        # create a temporary batch file
        _, name = mkstemp(suffix=".bat")
        os.close(_)
        # open it writable
        with open(name, "w") as f:
            # check if we have a custom build script in the libs.yml
            if self.lib["custombuild"]:
                # write all commands to the batch file
                for cmd in self.lib["custombuild"]:
                    f.write(self._formatCommand(
                        cmd, binpath, extractedpath, buildpath
                    ) + "\n")
            elif "cmakeflags" in self.lib or "customcmake" in self.lib:
                # copy over a custom CMake file id there is one present
                if self.lib["customcmake"]:
                    shutil.copyfile(self.lib["customcmake"],
                                    extractedpath + "/CMakeLists.txt")

                # construct the call to CMake; also applies the install prefix
                # and specifies the output directory for the PDB file
                args = [cmake,
                        "-G", self.compiler["generator"],
                        "-DCMAKE_INSTALL_PREFIX={}".format(binpath),
                        "-DCMAKE_PDB_OUTPUT_DIRECTORY_RELWITHDEBINFO={}/bin".format(
                            binpath),
                        ]

                # append custom CMake flags if provided
                if "cmakeflags" in self.lib and self.lib["cmakeflags"] is not None:
                    for flag in self.lib["cmakeflags"]:
                        args.append("-D{}".format(flag))

                # if there are dependencies, we need to hint cmake some paths
                # so that the include and lib folder can be found by the
                # Find*.cmake files
                if dependencyBinPaths:
                    args.append("-DCMAKE_PREFIX_PATH={}".format(
                        ';'.join(dependencyBinPaths)))

                # append the source path
                args.append(extractedpath)

                # create cmake configuration command
                cmake_compile = " ".join(
                        map(lambda x: "\"" + x + "\"", args)
                    ) + "\n"

                # create cmake install command
                cmake_install = ("\"{}\" --build . --target install " +
                                 "--config RelWithDebInfo\n").format(cmake)

                # write commands to file
                f.write(cmake_compile)
                f.write(cmake_install)

        # call the batch file so that the compilation can start
        subprocess.run(name, cwd=buildpath, stdout=subprocess.DEVNULL)
        # remove the temporary batch file
        os.unlink(name)

        # if we reached this point, compilation was successful
        # so, set the build status to True
        self._setSuccessfulBuild(success=True)
