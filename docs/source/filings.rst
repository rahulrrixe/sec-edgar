.. _filings:

.. warning::
   The ``SECEdgar.Filings`` class will be added in v0.1.5. If you would like to make use of this functionality, 
   please install the `latest development version <https://github.com/coyo8/sec-edgar>`_ from GitHub.

Filings
=======

Filings can be downloaded using the :class:`SECEdgar.base.Filing` class found in the ``SECEdgar.filings`` module. 
These classes inherit from the :class:`SECEdgar.base._EDGARBase` class. This class provides relevant ``**kwargs`` 
for making requests and the number of filings to fetch.

Base Class
----------

.. autoclass:: SECEdgar.base._EDGARBase

Filings
-------

Supported filing types can be found at :ref:`filingtypes`

.. autoclass:: SECEdgar.filings.Filing