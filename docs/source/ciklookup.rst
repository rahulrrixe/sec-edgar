.. _ciklookup:

CIK Lookup
==========
The ``CIKLookup`` class allows users to get company filings using company tickers and/or company names.

.. note::
   By default, the ``CompanyFilings`` class wraps any given string or an iterable with string objects (e.g. a list of strings or a tuple
   of strings). You will probably not need to use this class. However, it can be useful if you wish to save the CIKs for lookup terms.

Below is an example of how you can retrieve lookup CIKs by using the ``CIKLookup`` class.

.. code-block:: python

   from secedgar.core.cik_lookup import CIKLookup

   lookups = CIKLookup(['aapl', 'msft', 'Facebook'])


Accessing ``lookups.lookup_dict`` would then return

::

   {'aapl': '320193', 'msft': '789019', 'Facebook': '0001326801'}

Another alternative to using the ``CIKLookup`` class directly is to use the provided :meth:`secedgar.cik_lookup.get_cik_map` function.

.. autoclass:: secedgar.cik_lookup.CIKLookup
   :members:
