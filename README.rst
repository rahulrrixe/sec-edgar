sec-edgar
=========

|Tests Status| |Docs Status|

Getting filings of various companies at once is really a pain, but
SEC-Edgar does that for you. You can download all of a company’s
periodic reports, filings and forms from the EDGAR database with a
single command.

Installation
------------

You may have to install the package using pip:

.. code:: bash

   $ pip install secedgar

or

You can clone the project or download it as zip.

.. code:: bash

   $ git clone https://github.com/sec-edgar/sec-edgar.git
   $ cd sec-edgar
   $ python setup.py install

Running
-------

.. code:: python

    from secedgar.core import CompanyFilings, FilingType

    # 10Q filings for Apple (ticker "aapl")
    my_filings = CompanyFilings(cik_lookup='aapl', filing_type=FilingType.FILING_10Q)
    my_filings.save('/path/to/dir')

Supported Methods
-----------------

Currently this crawler supports many different filing types. To see the full list, please refer to the docs. If you don't see a filing type you would like
to be supported, please create an issue on GitHub.

Documentation
--------------
To learn more about the APIs and latest changes in the project, read the `official documentation <https://sec-edgar.github.io/sec-edgar>`_.


.. |Tests Status| image:: https://github.com/sec-edgar/sec-edgar/workflows/Tests/badge.svg
   :target: https://github.com/sec-edgar/sec-edgar/actions?query=workflow%3ATests
.. |Docs Status| image:: https://github.com/sec-edgar/sec-edgar/workflows/Build%20Docs/badge.svg
   :target: https://github.com/sec-edgar/sec-edgar/actions?query=workflow%3A%22Build+Docs%22
