# About secedgar

## Introduction

secedgar is a powerful tool designed to simplify the process of retrieving financial filings from the SEC EDGAR database. It addresses a common challenge faced by investors, researchers, and financial analysts: obtaining multiple company filings efficiently. With secedgar, you can download various periodic reports, filings, and forms from multiple companies simultaneously, saving time and effort in your financial research and analysis.

## What is EDGAR?

EDGAR, which stands for Electronic Data Gathering, Analysis, and Retrieval system, is the primary system for companies and others submitting documents under the Securities Act of 1933, the Securities Exchange Act of 1934, the Trust Indenture Act of 1939, and the Investment Company Act of 1940. Developed by the U.S. Securities and Exchange Commission (SEC), EDGAR performs automated collection, validation, indexing, acceptance, and forwarding of submissions by companies and others who are required by law to file forms with the SEC.

Key points about EDGAR:

1. **Purpose**: To increase the efficiency and fairness of the securities market for the benefit of investors, corporations, and the economy by accelerating the receipt, acceptance, dissemination, and analysis of time-sensitive corporate information filed with the SEC.

2. **Accessibility**: EDGAR makes corporate filings available to the public within minutes of filing, allowing for rapid dissemination of financial information.

3. **Types of Filings**: EDGAR contains registration statements, periodic reports, and other forms filed by companies. Common filings include:
   - 10-K (Annual reports)
   - 10-Q (Quarterly reports)
   - 8-K (Current reports)
   - S-1 (Initial public offering registration statements)
   - 13F (Institutional investment manager holdings reports)
   - And many more

4. **Historical Data**: The system provides access to filings dating back to 1994, offering a vast repository of historical financial data.

## How secedgar Helps

secedgar streamlines the process of interacting with the EDGAR database by providing:

1. **Batch Downloads**: Retrieve filings from multiple companies in a single operation.
2. **Customizable Queries**: Specify date ranges, filing types, and other parameters to get exactly the data you need.
3. **Automated Parsing**: secedgar can parse the retrieved filings, making it easier to extract specific information.
4. **Programmable Interface**: Integrate SEC filing retrieval into your Python scripts and applications.

## Getting Started with secedgar

To begin using secedgar, you'll typically follow these steps:

1. Install the package: `pip install secedgar`
2. Import the necessary modules in your Python script
3. Create a `CompanyFilings` or `FilingType` object
4. Specify the companies, date range, and filing types you're interested in
5. Use the `get_filings()` method to retrieve the desired documents

Here's a basic example:

```python
from secedgar import CompanyFilings, FilingType
from datetime import date

# Create a CompanyFilings object
my_filings = CompanyFilings(cik_lookup=['AAPL', 'MSFT', 'GOOG'],
                            filing_type=FilingType.FILING_10K,
                            start_date=date(2019, 1, 1),
                            end_date=date(2021, 12, 31))

# Get the filings
my_filings.save('/path/to/save/directory')
```

This script will download all 10-K filings for Apple, Microsoft, and Google between January 1, 2019, and December 31, 2021.

## Conclusion

secedgar simplifies the often complex task of retrieving SEC filings, making it an invaluable tool for anyone working with financial data. By automating the retrieval process and providing a user-friendly interface to the EDGAR database, secedgar allows users to focus on analyzing the data rather than collecting it.
