from idc import RunPlugin, AskStr, Message, Warning
from idaapi import Choose, add_hotkey
import requests
import os
import yaml
import json
import re

# path settings
homedir = os.path.expanduser("~")
bindifflibhome = os.path.join(homedir, "bindifflib")

# artfactory settings
artifactoryBase = "https://artifactory.example.com/artifactory/"
repoName = "repo"
repoPath = artifactoryBase + repoName + "/"
auth = ("user", "password")

# copiler settings path
compiler_file = "C:\\your\\path\\to\\compilers.yml"


class VersionChooser(Choose):
    """ Displays a choose dialog where the user has to select
        a version for the library he wants to download.
    """
    def __init__(self, versions):
        super(VersionChooser, self).__init__(versions, "Select Version", 1)
        self.width = 30

    def enter(self, n):
        return


class NameChooser(Choose):
    """ Presents the user with a dialog to select the library
        to be download later.
    """
    def __init__(self, names):
        super(NameChooser, self).__init__(names, "Select Library", 1)
        self.width = 30

    def enter(self, n):
        return


def queryPackets():
    """ Retrieves the full list of packages from the artifactory and
        returns empty list on error.
    """
    try:
        data = json.loads(requests.post(artifactoryBase + "api/search/aql",
                          data='items.find({"repo":"{}"}).include("name", "path")'.format(repoName),
                          verify=False, auth=auth).text)
        resultset = []
        for entry in data["results"]:
            resultset.append(entry)
        return resultset
    except:
        return []


def filterPackagesByVersion(packets, version):
    """ Filters packets by version and emits a generator as the result. """
    for p in packets:
        if version in p["path"]:
            yield p


def getPacketsByName(packets, name):
    """ Return a list of packages that match the given name. """
    resultset = []
    for p in packets:
        if name in p["path"]:
            resultset.append(p)
    return resultset


def getPacketNames(packets):
    """ Return a unified list of names of the libraries from the
        list of packages sent by the artifactory server.
    """
    resultset = []
    for p in packets:
        name = p["path"].split("/")[1]
        if name not in resultset:
            resultset.append(name)
    resultset.sort()
    return resultset


def getPacketVersions(packets):
    """ Return a unified list of version for the given list of packages. """
    resultset = []
    for packet in packets:
        v = packet["path"].split("/")[2]
        if v not in resultset:
            resultset.append(v)
    resultset.sort()
    return resultset


def main():
    # get all packages from server and extracts the names
    packets = queryPackets()
    names = getPacketNames(packets)

    # ask for the library to download
    chooser = NameChooser(names)
    choice = chooser.choose()
    if not choice:
        Warning("You need to select a library")
        return

    name = names[choice - 1]

    # filter out all packets that don't match the name
    filtered_packets = getPacketsByName(packets, name)
    if not filtered_packets:
        return

    # get list of available versions and ask the user
    # which one to use
    versions = getPacketVersions(filtered_packets)
    chooser = VersionChooser(versions)
    selection = chooser.choose()
    if not selection:
        Warning("You need to select a version")
        return

    version = versions[selection - 1]

    # construct the local path of the library
    libpath = os.path.join(bindifflibhome, name, version)
    try:
        os.makedirs(libpath)
    except:
        # folder already exists
        pass

    # parse list of compilers
    compilers = yaml.load(open(compiler_file, "rb").read())

    # iterate through list of packages (filtered by version)
    for p in filterPackagesByVersion(filtered_packets, versions[selection - 1]):
        # we only need i64/idb files
        if os.path.splitext(p["name"])[1] in [".i64", ".idb"]:
            # construct remote path
            remote_file = p["path"] + "/" + p["name"]

            # we need to download a library for all given compilers
            for _, c in compilers.items():
                if c["short"] not in p["path"]:
                    # skip if there's no remote library for the compiler
                    continue

                # construct local paths
                path, ext = os.path.splitext(p["name"])
                local_filename = "{}_{}{}".format(path, c["short"], ext)
                local_path = os.path.join(libpath, local_filename)

                # skip if library was already downloaded
                if (os.path.exists(local_path) and
                        os.path.getsize(local_path) is not 0):
                    print("{} already present".format(local_filename))
                    continue

                # initiate download from artifactory
                print("Downloading {}...".format(local_filename))
                resp = requests.get(
                    repoPath + "/" + p["path"] + "/" + p["name"],
                    stream=True, verify=False)

                # handle the response
                try:
                    if resp.status_code is not 200:
                        Warning("Server did not respond with status 200. Message:\n" + data)
                    else:
                        with open(local_path, "wb") as f:
                            f.write(resp.raw.read())
                except:
                    Warning("Error!")

    Message("Done. Files saved to folder {}".format(libpath))

if __name__ == "__main__":
    # we try to setup a hotkey to make re-running the script easier
    if add_hotkey("Ctrl-Shift-B", main) is None:
        Message("Failed to set hotkey, please re-run this script to download other IDBs")
    else:
        Message("Hotkey registered, press Ctrl-Shift-B to download another library")

    main()
