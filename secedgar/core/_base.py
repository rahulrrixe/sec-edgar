import os
import string
from abc import ABC, abstractmethod

from secedgar.exceptions import NoFilingsError
from secedgar.parser import MetaParser


class AbstractFiling(ABC):
    """Abstract base class for all SEC EDGAR filings.

    .. versionadded:: 0.1.5
    """

    def extract_meta(self,
                     directory,
                     out_dir=None,
                     create_subdir=True,
                     rm_infile=False):
        """Extract meta data from filings in directory."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.txt'):
                    MetaParser().process(os.path.join(root, file),
                                         out_dir=out_dir,
                                         create_subdir=create_subdir,
                                         rm_infile=rm_infile)

    @property
    @abstractmethod
    def client(self):
        """``secedgar.client._base``: Client to use to make requests."""
        pass  # pragma: no cover

    @property
    @abstractmethod
    def params(self):
        """:obj:`dict`: Parameters to include in requests."""
        pass  # pragma: no cover

    @property
    @abstractmethod
    def path(self):
        """str: Path added to client base."""
        pass  # pragma: no cover

    @abstractmethod
    def get_urls(self, **kwargs):
        """Get all URLs for filings.

        Args:
            kwargs: Anything to be passed to requests when making GET request.

        Returns:
            urls (dict): Dictionary of urls for txt files to download.
                Keys are lookup terms and values are list of URLs.
        """
        pass  # pragma: no cover

    @abstractmethod
    def save(self, directory):
        """Save filings in directory.

        Args:
            directory (str): Path to directory where files should be saved.

        Returns:
            None
        """
        pass  # pragma: no cover

    @staticmethod
    def get_accession_number(url):
        """Get accession number from filing URL.

        .. note::
           All URLs are expected to end with /{accession number}.txt
        """
        return url.split("/")[-1]

    @staticmethod
    def clean_directory_path(path):
        """Clean string to use as directory name.

        Args:
            path (str): Directory name to clean.
        """
        allowed = string.digits + string.ascii_letters + string.whitespace
        stripped = "".join(c for c in path if c in allowed)
        return stripped.replace(" ", "_")

    def get_urls_safely(self, **kwargs):
        """Wrapper around `get_urls` to check if there is a positive number of URLs, and warn if they don't.

        .. note:: This method will not check if the URLs are valid. Simply if they exist.

        Raises:
            NoFilingsError: If no URLs exist, then NoFilingsError is raised.

        Returns:
            urls (dict): Result of `get_urls` method.
        """
        urls = self.get_urls(**kwargs)
        if all(len(urls[cik]) == 0 for cik in urls.keys()):
            raise NoFilingsError("No filings available.")
        return urls
