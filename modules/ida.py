import subprocess
import os
import re
import hashlib
from urllib.request import Request, urlopen
from base64 import b64encode

REGEX = re.compile(r".*[/\\](.*?)-([^/\\]*)_(.*?)[/\\]bin[/\\](.*?)\.dll")


class IDAHelper(object):
    """ Helper class that provides an easy-to-use interface to IDA Pro. """

    def __init__(self, dll, pdb, idaq, idaq64, artifactoryPath, auth):
        """ Initializes an instance of this class.

            :param dll: the path of the dll to be analyzed with IDA Pro
            :param pdb: the path of the PDB file that should be applied
            :param idaq: the full path to idaq.exe
            :param idaq64: the full path to idaq64.exe
            :param artifactortPath: the URL base path for the artifactory
            :param auth: HTTP basic auth tokens for the artifactory
        """
        super(IDAHelper, self).__init__()
        self._dll = (os.getcwd() + "/" + dll).replace("\\", "/")
        self._pdb = (os.getcwd() + "/" + pdb).replace("\\", "/")
        self._idaq = idaq if "x64" not in dll else idaq64
        self._idb = (self._dll.replace(".dll", ".idb") if "x64" not in self._dll
                     else self._dll.replace(".dll", ".i64"))
        self._cwd = os.getcwd() + "/" + "/".join(dll.split("/")[:-1])
        self._cwd = self._cwd.replace("\\", "/")
        self._artifactoryPath = artifactoryPath
        self._auth = auth

    def makeidb(self):
        """ Runs IDA Pro with command line flags to output an IDB file. """
        args = [self._idaq,
                # overwrite existing
                "-c",
                # batch mode (create IDB and ASM file automatically and exit)
                "-B",
                # autonomous mode (no dialog boxes etc; remove on IDA crash)
                "-A",
                # pass arguments to our script
                "-Obindifflib:{}".format(self._pdb),
                # tell IDA to execute the bindifflib_exporter script
                "-S\"{}/bindifflib_exporter.py\"".format(os.getcwd()),
                # pack database
                "-P+",
                self._dll]
        # run IDA
        subprocess.run(args, cwd=self._cwd)

    def storeresult(self):
        """ Stores the IDB, DLL, and PDB file in the artifactory. """

        # well, storing into void is not that useful
        if self._artifactoryPath is None:
            return

        m = REGEX.search(self._dll)
        if m:
            # extract some information from the path where the DLL is
            name = m.group(1)
            version = m.group(2)
            compiler = m.group(3)
            filename = m.group(4)

            # send each file separately
            names = [self._dll, self._pdb, self._idb]
            for file in names:
                # construct the PUT header, e.g. MD5 and SHA-1 hashes
                # of the file and, most importantly, setup HTTP basic auth
                headers = {
                    "Content-Type": "application/octet-stream",
                    "X-Checksum-md5": hashlib.md5(
                        open(file, "rb").read()).hexdigest(),
                    "X-Checksum-sha1": hashlib.sha1(
                        open(file, "rb").read()).hexdigest(),
                    "Authorization": "Basic {}".format(
                        b64encode(
                            ":".join(self._auth).encode()).decode("ascii")),
                }

                # construct the urllib request
                r = Request(self._artifactoryPath +
                            "bin/{name}/{version}/{compiler}/{fname}".format(
                                name=name, version=version, compiler=compiler,
                                fname=file.replace("\\", "/").split("/")[-1]),
                            headers=headers, data=open(file, "rb").read(),
                            method="PUT")

                # send the request and upload the file
                urlopen(r)

    @property
    def dll(self):
        return self._dll
