.. _filingtypes:

Filing Types
============

This page aims to first explain briefly what information is contained in some of the most popular filing types.
The complete table of filing types is available at the bottom of this document.


Common Filing Types
-------------------

Below are some of the most frequently used types of filings with brief descriptions of what
information can be found in those filings.

Form 10-K
~~~~~~~~~

The 10-K form is an annual report submitted by public companies listed on U.S. stock exchanges.
As the `SEC explains <https://www.sec.gov/fast-answers/answers-form10khtm.html>`_,
"The annual report on Form 10-K provides a comprehensive overview of the
company's business and financial condition and includes audited financial statements."

Form 10-Q
~~~~~~~~~

`According to the SEC <https://www.sec.gov/fast-answers/answersform10qhtm.html>`_,
"The Form 10-Q includes unaudited financial statements and provides
a continuing view of the company's financial position during the year.
The report must be filed for each of the first three fiscal quarters of the company's fiscal year."
The 10-Q provides investors regular check-ins to a company's health from quarter to quarter.

Form 8-K
~~~~~~~~

The Form 8-K reports major events that shareholders should know about. The SEC defines various
events as major. A few highlights include:

- Bankruptcy
- Termination of a "Material Definitive Agreement"
- Notice of delisting
- Material impairments
- Shareholder director nominations
- Amendments to Articles of Incorporation or Bylaws

For a full list, refer to the `SEC's full list <https://www.sec.gov/fast-answers/answersform8khtm.html>`_.

Form 13-F
~~~~~~~~~

The 13-F form is a holding disclosure by institutional investors who manage at least $100 million USD (e.g. mutual funds, hedge funds, pension funds, etc.).
The form is released quarterly and provides insight into buying behavior. However, these forms can be submitted up to 45 days after
the end of the quarter. Thus, they are not guaranteed to be up to date with the current holdings by the institutional
investor. Only certain securities must be included in the Form 13-F. The `full list of securities <https://www.sec.gov/divisions/investment/13flists.htm>`_
can be found on the SEC website.

Form 4
~~~~~~

The Form 4 reports changes in ownership by insiders and must be reported to the SEC within two business days.

Form SD
~~~~~~~

The Form SD (**S**\ pecialized **D**\ isclosure) "satisfy special disclosure requirements implemented under
the Dodd-Frank Wall Street Reform and Consumer Protection Act relating to conflict minerals contained
in products that reporting companies manufacture or contract to be manufactured and necessary to the
functionality or production of those products."
(`Thompson Reuters <https://content.next.westlaw.com/Document/Icf49605def0a11e28578f7ccc38dcbee/View/FullText.html?contextData=(sc.Default)&transitionType=Default&firstPage=true&bhcp=1>`_)

Form DEF 14A
~~~~~~~~~~~~~
Definitive proxy statement. Required ahead of annual meeting when firm is soliciting shareholder votes.

All Filing Types
----------------

.. csv-table::
   :file: filingtypes.csv
   :header-rows: 1
   :widths: 10, 20, 20, 50

Using FilingType with secedgar
--------------------------------

As is shown in the table above, there are many different filing types to choose from.
Below is a complete list of all available filing types that you can choose from.

To see how filing types are used in secedgar, see :ref:`usage`.

.. autoclass:: secedgar.FilingType
   :members:
   :undoc-members:

