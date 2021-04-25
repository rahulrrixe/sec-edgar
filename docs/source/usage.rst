.. _usage:


Common Usage Examples
=====================

secedgar provides a simple way to download multiple filings from the
`SEC Edgar database <https://www.sec.gov/edgar/searchedgar/companysearch.html>`__.

This package is useful for obtaining important financial information about public companies such as

- Financials
- Business Profile
- Letter to Shareholders
- Management's Analysis

The ``CompanyFilings`` class provides a simple API to fetch SEC filings.

.. code-block:: python

   from secedgar import CompanyFilings, FilingType

   my_filings = CompanyFilings(cik_lookup='aapl',
                       filing_type=FilingType.FILING_10Q,
                       count=15)

The ``cik_lookup`` argument can also take multiple tickers and/or company names.

.. code-block:: python

   from secedgar import CompanyFilings, FilingType

   my_filings = CompanyFilings(cik_lookup=['aapl', 'msft', 'Facebook'],
                       filing_type=FilingType.FILING_10Q,
                       count=15)


Using a User Agent
------------------

SEC requests that traffic identifies itself via a user agent string. You can
customize this according to your preference using the ``user_agent`` argument.

A note from the SEC website:

   Please declare your traffic by updating your user agent to include company specific information.
   For best practices on efficiently downloading information from SEC.gov, including the latest EDGAR
   filings, visit `sec.gov/developer <https://www.sec.gov/developer>`_. You can also
   `sign up for email updates <https://public.govdelivery.com/accounts/USSEC/subscriber/new?topic_id=USSEC_260>`_
   on the SEC open data program, including best practices that make it more efficient to download data,
   and SEC.gov enhancements that may impact scripted downloading processes.
   For more information, contact opendata@sec.gov.

.. code-block:: python

   from secedgar.filings import Filing, FilingType

   my_filings = Filing(cik_lookup=['aapl', 'msft', 'Facebook'],
                       filing_type=FilingType.FILING_10Q,
                       count=15,
                       user_agent='YOUR COMPANY NAME HERE')


Saving Filings
--------------

In order to save all fetched filings to a specific directory, use the ``save`` method.

.. code-block:: python

   my_filings.save('~/tempdir')
