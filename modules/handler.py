from .downloader import Downloader
from .extractors import EXTRACTORS
import yaml
import os
import shutil
import re


class LibHandler(object):
    """ Handles a library from libs.yml. """
    def __init__(self, cachePrefix="", extractedPrefix="",
                 buildPrefix="", binPrefix="", customCmakePrefix=""):
        """ Initializes an instance of the class. 

            :param cachePrefix: full path prefix to the cache directory
            :param extractedPrefix: full path prefix to the directory
                where all library source packages get unpacked into
            :param buildPrefix: full path prefix  to the build directory
            :param binPrefix: full path prefix to the directory where the
                binaries will be stored
            :param customCmakePrefix: prefix of the directory where the
                custom cmake files are stored
        """
        self._libs = {}
        self._cachePrefix = cachePrefix
        self._extractedPrefix = extractedPrefix
        self._buildPrefix = buildPrefix
        self._binPrefix = binPrefix
        self._customCmakePrefix = customCmakePrefix

    def getLibs(self):
        """ Returns the global list of libraries. """
        return self._libs

    def addLibrary(self, name, args):
        """ Adds a new library the global list of libraries.

            :param name: name of the library
            :param args: dictionary of meta data of the library, as
                provided in libs.yml
        """
        versions = args.get("versions", [])
        url = args.get("url", "")
        urls = args.get("urls", [])
        filetype = args.get("filetype", "")

        # add to internal cache if not yet present at all
        if name not in self._libs:
            self._libs[name] = {}

        file = None

        # if we have a list of URLs just download and use those; we do not
        # need to take care of URL formatting then.
        # otherwise, format the URL for every version in the metadata and
        # download all files that way
        if urls:
            regex = re.compile("\/{name}[-_\.](.*)\.{filetype}$".format(
                name=name, filetype=filetype))
            regex_github = re.compile(
                "\/{name}\/archive\/(.*)\.{filetype}$".format(
                    name=name, filetype=filetype))
            for _url in urls:
                # try to find the name and version of the library from the URL
                m = regex.search(_url)
                if m:
                    # download file
                    fileobj = self._downloadLib(_url)
                    # get version from regex
                    version = m.group(1)

                    # if the download was successful, store it in the local cache
                    if fileobj is not None:
                        self._addToCache(fileobj=fileobj, version=version,
                                         name=name, args=args)
                else:
                    if "github" in _url.lower():
                        m = regex_github.search(_url)
                        if m:
                            fileobj = self._downloadLib(_url)
                            version = m.group(1)
                            if fileobj is not None:
                                self._addToCache(fileobj=fileobj, version=version,
                                                 name=name, args=args)
                    else:
                        print("Could not detect version for url {}".format(_url))
        else:
            for version in versions:
                if version in self._libs[name]:
                    # skip if already in cache
                    print("""{}-{} already present in internal cache.
                             Skipping.""".format(name, version))
                    continue

                # download lib
                file = self._downloadLib(url.format(version=version))

                # if download was successful, store the library in the local cache
                if file is not None:
                    self._addToCache(fileobj=file, version=version,
                                     name=name, args=args)

    def _addToCache(self, fileobj, version, name, args):
        """ Adds a given library to the local cache. Also ensures, that 
            archives get unpacked and performs some pre-compilation steps that
            fit better in here than somewhere else.

            :param fileobj: an open file object of the downloaded source archive
            :param version: the current version of the library
            :param name: the name of the library
            :param args: a dictionary of the metadata provided in libs.yml
        """

        # get information from metadata
        url = args.get("url", "")
        urls = args.get("urls", [])
        filetype = args.get("filetype", "")
        extratcsToSubfolder = args.get("extracts_to_subfolder", False)
        subfolderNeedsRename = args.get("subfolder_needs_rename", False)
        remove_files_from = args.get("remove_files_from", [])
        dependencies = args.get("dependencies", [])
        cmakeflags = args.get("cmakeflags", [])
        custombuild = args.get("custombuild", [])
        build_64bit = args.get("64bit", True)

        # the file handle should not be closed at that point,
        # but we check it anyway to get sure
        if fileobj is not None:
            extractedName = ""
            # if the file was already extracted in a previous run, we can
            # skip the extraction for obvious reasons
            if not self._alreadyExtracted(
                    name, version):
                extractor = None
                # if the library source has no root folder in the package,
                # we need to create it manually to avoid pollution of the
                # extractedPath directory
                if (extratcsToSubfolder is not True):
                    extractor = EXTRACTORS[filetype](
                                    fileobj, self._extractedPrefix + "/" +
                                    name + "-" + version)
                else:
                    extractor = EXTRACTORS[filetype](
                                    fileobj, self._extractedPrefix)

                # extrac the files and close the handle to the source package
                extractedName = extractor.extract()
                fileobj.close()

                # if we need to rename the root directory of the source,
                # we do it now by moving it to another name; also, change
                # the internal name of the directory accordingly
                if subfolderNeedsRename:
                    new_name = "{}-{}".format(name, version)
                    shutil.move(self._extractedPrefix + extractedName,
                                self._extractedPrefix + new_name)
                    extractedName = new_name
                else:
                    extractedName = "{}-{}".format(name, version)

            else:
                extractedName = "{}-{}".format(name, version)

            # remove file that have to be removed from the source tree
            if remove_files_from and ("source" in remove_files_from):
                for f in remove_files_from["source"]:
                    path = "{}/{}/{}".format(self._extractedPrefix, extractedName, f)
                    try: # try to remove file
                        os.remove(path)
                    except OSError:
                        try: # try to remove directory
                            os.removedirs(path)
                        except OSError:
                            print("Cannot remove path \"{}\"".format(path))


            deps = None
            # parse the dependencies from the metadata
            if dependencies is not None:
                # dependencies that are flagged as "all" have to be
                # applied to all versions of the current library
                if "all" in dependencies:
                    deps = dependencies["all"]
                # if we have special dependencies for a specific version,
                # take care of that now; if there was a different version
                # of the dependency in "all", it will be overwritten
                if version in dependencies:
                    for n, v in dependencies[version].items():
                        deps[n] = dependencies[version][n]

            customcmake = ""
            # check if there is a custom cmake file present
            if "customcmake" in args and args["customcmake"] is not None:
                # custom cmake files that are flagged as "all" have to be
                # applied to all versions of the current library
                if "all" in args["customcmake"]:
                    customcmake = (self._customCmakePrefix +
                                   args["customcmake"]["all"])
                # if we have special cmake files for a specific version,
                # take care of that now; if there was a different version
                # of the cmake file in "all", it will be overwritten
                if version in args["customcmake"]:
                    customcmake = (self._customCmakePrefix +
                                   args["customcmake"][version])

            # insert a dictionary with all necessary information into
            # the internal cache
            self._libs[name][version] = {
                'extractedpath':
                    self._extractedPrefix + extractedName,
                'buildpath': self._buildPrefix + extractedName,
                'binpath': self._binPrefix + extractedName,
                'dependencies': deps,
                'built': False,
                'cmakeflags': cmakeflags,
                'customcmake': customcmake,
                'custombuild': custombuild,
                '64bit': build_64bit,
            }

    def addFile(self, name):
        """ Parses a new yml and adds all libraries from there to the cache."""
        if name is not None and name is not "":
            print("Parsing file {}".format(name))
            with open(name, "rb") as f:
                yaml_data = yaml.load(f.read())

                if "libs" in yaml_data and yaml_data["libs"] is not None:
                    libs = yaml_data["libs"]
                    for libname in libs:
                        _libname = libs[libname].get("name", libname)
                        self.addLibrary(_libname, libs[libname])

    def _downloadLib(self, url):
        """ Utilizes the :class:`Downloader` to download a file from
            the given URL.

            :param url: the URL of the file to download
        """
        filename = url.split("/")[-1]

        # github archive urls need a bit of special treatment regarding
        # version and name of the library
        if "github" in url and "archive" in url:
            _split = url.split("//")[1].split("/")
            filename = _split[2] + "-" + _split[4]


        # check cache for presence of an already downloaded copy
        # and skip if there is one. Otherwise, download it.
        tempname = self._cachePrefix + filename
        if not os.path.exists(tempname):
            print("Downloading {}".format(filename))

            data = Downloader(url).getData()
            if data is not None:
                file = open(tempname, "w+b")
                file.write(data)
                file.seek(0)
                return file
            return None
        else:
            print("Using cached {}".format(filename))
            return open(tempname, "r+b")

    def _alreadyExtracted(self, name, version):
        """ Helper function that checks if a library was already extracted.

            :param name: name of the library
            :param version: version of the library
        """
        return os.path.exists("{}{}-{}".format(
            self._extractedPrefix, name, version))
