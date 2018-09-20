import tarfile
from zipfile import ZipFile
import os


class Extractor(object):
    """ Base class for all extractors. """

    def __init__(self, fileobj, extractedPrefix):
        """ Initializes an instance of the class.

            :param fileobj: an open file handle to the file that
                needs to be extracted
            :param extractedPrefix: an absolute path prefix to the
                directory where the files should be extracted to.
        """
        self._extractedPrefix = extractedPrefix
        self._fileobj = fileobj

    def extract(self):
        pass


class TarGzExtractor(Extractor):
    """ Extracts a tar.gz file utilizing pythons tarfile module. """

    def __init__(self, fileobj, extractedPrefix=""):
        """ Forwards all parameters to :class:`Extractor`."""
        super(TarGzExtractor, self).__init__(fileobj, extractedPrefix)

    def extract(self):
        """ Extracts a tar.gz file. """
        extractedName = ""
        if self._fileobj is not None:
            instance = tarfile.open(fileobj=self._fileobj)
            if instance:
                extractedName = instance.getmembers()[0].name
                if not os.path.exists(
                        self._extractedPrefix + "\\" + extractedName):
                    instance.extractall(self._extractedPrefix)
                    instance.close()
        return extractedName


class ZipExtractor(Extractor):
    """ Extracts a zip file utilizing pythons zipfile module. """

    def __init__(self, fileobj, extractedPrefix=""):
        """ Forwards all parameters to :class:`Extractor`."""
        super(ZipExtractor, self).__init__(fileobj, extractedPrefix)

    def extract(self):
        """ Extracts a zip file. """
        extractedName = ""
        if self._fileobj is not None:
            instance = ZipFile(self._fileobj.name)
            if instance:
                instance.extractall(path=self._extractedPrefix)
                extractedName = instance.namelist()[0].filename
                instance.close()
        return extractedName


class PlainExtractor(Extractor):
    """ Dummy PlainExtractor. Does nothing. """
    def __init__(self, fileobj, extractedPrefix=""):
        super(PlainExtractor, self).__init__(fileobj, extractedPrefix)

""" Declare the list of extractors so that it can be easily imported
    into other modules."""
EXTRACTORS = {
    "tar.gz": TarGzExtractor,
    "zip": ZipExtractor,
    "plain": PlainExtractor,
}
