sec-edgar
=========

|Tests Status| |Docs Status|

Getting filings of various companies at once is really a pain, but
SEC-Edgar does that for you. You can download all of a company’s
periodic reports, filings and forms from the EDGAR database with a
single command.

Installation
------------

You can install the package using pip:

.. code:: bash

   $ pip install secedgar

OR

You can clone the project:

.. code:: bash

   $ git clone https://github.com/sec-edgar/sec-edgar.git
   $ cd sec-edgar
   $ python install .

Running
-------

Company Filings
~~~~~~~~~~~~~~~

Single Company
^^^^^^^^^^^^^^

.. code:: python

    from secedgar import filings, FilingType

    # 10Q filings for Apple (ticker "aapl")
    my_filings = filings(cik_lookup="aapl",
                         filing_type=FilingType.FILING_10Q,
                         user_agent="Your name (your email)")
    my_filings.save('/path/to/dir')


Multiple Companies
^^^^^^^^^^^^^^^^^^

.. code:: python

    from secedgar import filings, FilingType

    # 10Q filings for Apple and Facebook (tickers "aapl" and "fb")
    my_filings = filings(cik_lookup=["aapl", "fb"],
                         filing_type=FilingType.FILING_10Q,
                         user_agent="Your name (your email)")
    my_filings.save('/path/to/dir')


Daily Filings
~~~~~~~~~~~~~


.. code:: python

    from secedgar import filings
    from datetime import date

    daily_filings = filings(start_date=date(2021, 6, 30),
                            user_agent="Your name (your email)")
    daily_urls = daily_filings.get_urls()



Supported Methods
-----------------

Currently this crawler supports many different filing types. To see the full list, please refer to the docs. If you don't see a filing type you would like
to be supported, please create an issue on GitHub.

Documentation
--------------
To learn more about the APIs and latest changes in the project, read the `official documentation <https://sec-edgar.github.io/sec-edgar>`_.


.. |Tests Status| image:: https://github.com/sec-edgar/sec-edgar/actions/workflows/test.yml/badge.svg
   :target: https://github.com/sec-edgar/sec-edgar/actions/workflows/test.yml
.. |Docs Status| image:: https://github.com/sec-edgar/sec-edgar/actions/workflows/docs.yml/badge.svg
   :target: https://github.com/sec-edgar/sec-edgar/actions/workflows/docs.yml
