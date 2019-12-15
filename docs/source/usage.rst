.. _usage:


Common Usage Examples
=====================

SECEdgar provides a simple way to download multiple filings from the 
`SEC Edgar database <https://www.sec.gov/edgar/searchedgar/companysearch.html>`__.

This package is useful for obtaining important financial information about public companies such as 

- Financials
- Business Profile
- Letter to Shareholders
- Management's Analysis

The ``Filing`` class provides a simple API to fetch SEC filings.

.. ipython:: python

   from SECEdgar.filings import Filing, FilingType
   my_cik = '0000320193'
   my_filings = Filing(cik=my_cik, filing_type=FilingType.FILING_10Q, count=15)

In order to save all fetched filings to a specific directory, use the ``save`` method.

.. ipython:: python

   my_filings.save('~/tempdir')
