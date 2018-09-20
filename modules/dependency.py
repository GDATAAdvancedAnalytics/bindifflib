

class Internal(object):
    """ Helper class to provide an interface to the underlying
        dictionary of meta data."""
    def __init__(self, lib, name, version, dependencies=None):
        """ Initializes the class.

            :param lib: the metadata of the library as provided
                is libs.yml
            :param name: the name of the library
            :param version: the current version of the library
            :param dependencies: (optional) list of dependecies
        """
        self._lib = lib
        self._name = name
        self._version = version
        if not dependencies:
            self._dependencies = lib["dependencies"]
        else:
            self._dependencies = dependencies

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def name(self):
        return self._name

    @property
    def lib(self):
        return self._lib

    @property
    def version(self):
        return self._version

    def __str__(self):
        return "{}-{}".format(self._name, self._version)

    def __repr__(self):
        return "<class Internal(name={}, version={}, dependencies={})>".format(
                    self._name, self._version, self._dependencies)


class DependencyHelper(object):
    """ Helper class for dependecy "resolution". It ensures that the dependencies
        of the library are set in the metadata.
    """
    def __init__(self, libs):
        """ Initializes an instancen of DependecyHelper.

            :param libs: global list of libraries
        """
        self._libs = libs

    def resolve(self):
        """ Performs the dependncy resolution and returns a list with the results."""
        ret = []

        # iterate over all libraries
        for name in self._libs:
            # consider all version separately
            for version, lib in self._libs[name].items():
                libdeps = lib["dependencies"]
                dependencies = []

                # apply dependencies if there are some
                if libdeps is not None:
                    for depname, depversion in libdeps.items():
                        dependencies.append(
                            Internal(lib=self._libs[depname][depversion],
                                     name=depname, version=depversion))
                # append the current library to the resultset
                ret.append(Internal(lib=lib, name=name, version=version,
                                    dependencies=dependencies))

        return ret
