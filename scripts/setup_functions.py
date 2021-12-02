"""Setup helpers for setup.py."""
import fnmatch
import os
from distutils.command.clean import clean as _clean
from os.path import exists
from pathlib import Path
from shutil import rmtree

from setuptools_scm import get_version


def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    try:
        lineiter = Path(filename).read_text(encoding="utf8").splitlines()
        return [line for line in lineiter if line and not line.startswith("#")]
    except OSError:
        return []


# ======================================================================================
# Overriding and extending setup commands; here "clean"
# ======================================================================================


class CleanUp(_clean):
    """Custom implementation of ``clean`` command.

    Overriding clean in order to get rid if "dist" folder and etc, see setup.py.
    """

    CLEANFOLDERS = (
        "__pycache__",
        "pip-wheel-metadata",
        ".eggs",
        "dist",
        "build",
        "sdist",
        "wheel",
        ".pytest_cache",
        "docs/apiref",
        "docs/_build",
        "result_images",
        "TMP",
    )

    CLEANFOLDERSRECURSIVE = ["__pycache__", "_tmp_*", "*.egg-info"]
    CLEANFILESRECURSIVE = ["*.pyc", "*.pyo"]

    @staticmethod
    def ffind(pattern, path):
        """Find files."""
        result = []
        for root, _, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result

    @staticmethod
    def dfind(pattern, path):
        """Find folders."""
        result = []
        for root, dirs, _ in os.walk(path):
            for name in dirs:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result

    def run(self):
        """Execute run.

        After calling the super class implementation, this function removes
        the directories specific to scikit-build ++.
        """
        super(CleanUp, self).run()

        for dir_ in CleanUp.CLEANFOLDERS:
            if exists(dir_):
                print(f"Removing: {dir_}")
            if not self.dry_run and exists(dir_):
                rmtree(dir_)

        for dir_ in CleanUp.CLEANFOLDERSRECURSIVE:
            for pdir in self.dfind(dir_, "."):
                print(f"Remove folder {pdir}")
                rmtree(pdir)

        for fil_ in CleanUp.CLEANFILESRECURSIVE:
            for pfil in self.ffind(fil_, "."):
                print(f"Remove file {pfil}")
                os.unlink(pfil)


# ======================================================================================
# Sphinx
# ======================================================================================

CMDSPHINX = {
    "build_sphinx": {
        "project": ("setup.py", "xtgeoapp-grd3dapp"),
        "version": ("setup.py", get_version()),
        "release": ("setup.py", ""),
        "source_dir": ("setup.py", "docs"),
    }
}
