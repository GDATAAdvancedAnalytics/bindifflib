import requests
from ftplib import FTP
from tempfile import TemporaryFile


class Downloader(object):
    """ Downloader class that provides an interface for downloading
        from different sources.
    """

    def __init__(self, url):
        """ Initializes an instance of this class.

            :param url: the url of the file to download
        """
        self._url = url

    def getData(self):
        """ Parses the protocol which is required to download the file
            and returns a binary blob with the contents of the file."""
        if self._url.startswith("http"):
            return self._httpGet()
        elif self._url.startswith("ftp"):
            return self._ftpGet()
        else:
            print("Unsupported url format: {}".format(
                    self._url.split("://")[0]))
            return None

    def _httpGet(self):
        """ Performs a HTTP GET request to get the file. """
        response = requests.get(self._url, stream=True)
        if response.status_code is not 200:
            return None
        else:
            return response.raw.read(decode_content=True)

    def _ftpGet(self):
        """ Applies FTP commands to get the file. """
        _, path = self._url.split("://")
        _split = path.split("/")

        host = _split[0]
        path = "/".join(_split[1:-1])
        file = _split[-1]

        try:
            ftp = FTP(host, timeout=60)
            ftp.login()
            ftp.cwd(path)

            tmpfile = TemporaryFile()
            ftp.retrbinary("RETR " + file, tmpfile.write)

            tmpfile.seek(0)
            data = tmpfile.read()
            tmpfile.close()

            return data

        except TimeoutError:
            print("Timeout while fetching {}".format(self._url))
            return None
