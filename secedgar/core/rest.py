from typing import List, Union

import requests

from secedgar.cik_lookup import CIKLookup

API_BASE = "https://data.sec.gov/api/"
XBRL_BASE = "{0}xbrl/".format(API_BASE)


def _get_lookup_dict(lookups: List[str], user_agent: str):
    """Utility function to get CIKs for lookups.

    Args:
        lookups (list of str): List of tickers or company names to get CIKs for.
        user_agent (str): User agent to give to SEC.

    Returns:
        dict: Dictionary with lookup and CIK key-value pairs.
    """
    cik_lookup = CIKLookup(lookups=lookups,
                           user_agent=user_agent,
                           client=None)
    return cik_lookup.lookup_dict


def _combine_dicts(*dicts):
    """Utility function to combine dictionary values when values are lists.

    Returns:
        dict: Dictionaries combined into one.

    Examples:
        >>> a = {"A": [1, 2, 3], "B": [4, 5, 6]}
        >>> b = {"A": [7, 8], "B": [0, 1, 2]}
        >>> _combine_dicts(a, b)
        {'A': [1, 2, 3, 7, 8], 'B': [4, 5, 6, 0, 1, 2]}
        >>> _combine_dicts(a)
        {'A': [1, 2, 3], 'B': [4, 5, 6]}
    """
    final = {}
    for d in dicts:
        for k, v in d.items():
            if k in final:
                final[k] += v
            else:
                final[k] = v
    return final


def get_submissions(lookups: Union[List[str], str],
                    user_agent: str,
                    recent: bool = True) -> dict:
    """Get information about submissions for entities.

    Args:
        lookups (list of str or str): Tickers or CIKs to get submission data for.
        user_agent (str): User agent to provide the SEC.
        recent (bool, optional): Whether or not to only get the most recent.
            Setting ``recent`` to True will give at least one year of filings or 1000 filings
            (whichever is more). Setting ``recent`` to False will return all filings.
            Defaults to True.

    Returns:
        dict: Dictionary with keys being the lookups and values being the responses from the API.
    """
    lookup_dict = _get_lookup_dict(lookups=lookups, user_agent=user_agent)
    submissions_dict = dict()
    url_base = "https://data.sec.gov/submissions/"
    for lookup, cik in lookup_dict.items():
        resp = requests.get("{0}CIK{1}.json".format(url_base, cik.zfill(10)),
                            headers={"user-agent": user_agent})
        resp_json = resp.json()
        if not recent:
            try:
                older_submission_files = resp_json["filings"]["files"]
            except KeyError:
                pass

            # Get data for older submission files and add to recent
            older_submissions = [requests.get("{0}{1}".format(url_base, f["name"]),
                                              headers={"user-agent": user_agent}).json()
                                 for f in older_submission_files]

            resp_json["filings"]["recent"] = _combine_dicts(resp_json["filings"]["recent"],
                                                            *older_submissions)
        submissions_dict[lookup] = resp_json
    return submissions_dict


def get_company_concepts(lookups: Union[List[str], str],
                         user_agent: str,
                         concept_name: str) -> dict:
    """Get company concepts using SEC's REST API.

    Args:
        lookups (list of str or str): Tickers or CIKs to get concepts for.
        user_agent (str): User agent to send to SEC.
        concept_name (str): Name of the concept to get data for.

    Returns:
        dict: Dictionary with concept data for given lookups.

    Example:
        .. code::

            concept = "AccountsPayableCurrent"
            get_company_concepts(lookups=["AAPL"],
                                 user_agent="Name (email@example.com)",
                                 concept_name=concept)
    """
    lookup_dict = _get_lookup_dict(lookups=lookups, user_agent=user_agent)
    company_concepts = dict()
    for lookup, cik in lookup_dict.items():
        url = "{0}companyconcept/CIK{1}/us-gaap/{2}.json".format(
            XBRL_BASE,
            cik.zfill(10),
            concept_name
        )
        resp = requests.get(url,
                            headers={"user-agent": user_agent})
        company_concepts[lookup] = resp.json()
    return company_concepts


def get_company_facts(lookups: Union[List[str], str], user_agent: str) -> dict:
    """Get company facts for lookups.

    Args:
        lookups (list of str or str): Tickers or CIKs to get company facts for.
        user_agent (str): User agent to send to SEC.

    Returns:
        dict: Dictionary with lookups as keys and company fact dictionaries as values.

    Examples:
        >>> facts = get_company_facts(["aapl"], "Name (email@example.com)")
        >>> single_fact = facts["aapl"]["facts"]["us-gaap"]["Assets"]["units"]["USD"][0]
        >>> single_fact["val"]
        39572000000
        >>> single_fact["fy"]
        2009
        >>> single_fact["fp"]
        Q3
        >>> single_fact["form"]
        '10-Q'
        >>> single_fact["filed"]
        '2009-07-22'
    """
    lookup_dict = _get_lookup_dict(lookups=lookups, user_agent=user_agent)
    company_facts = dict()
    for lookup, cik in lookup_dict.items():
        url = "{0}companyfacts/CIK{1}.json".format(XBRL_BASE, cik.zfill(10))
        resp = requests.get(url, headers={"user-agent": user_agent})
        company_facts[lookup] = resp.json()
    return company_facts


def get_xbrl_frames(user_agent: str,
                    concept_name: str,
                    year: int,
                    quarter: Union[None, int] = None,
                    currency: str = "USD",
                    instantaneous: bool = False) -> dict:
    """Get data for concept name in year (and quarter, if given).

    Args:
        user_agent (str): User agent to send to the SEC.
        concept_name (str): Concept name to get. For example, "Assets".
        year (int): Year to get concept data for.
        quarter (Union[int, NoneType], optional): Quarter to get data for. If given None,
            will look for data for the entire year. Defaults to None.
        instantaneous (bool, optional): Whether to look for instantaneous data.
            See `SEC website for more <https://www.sec.gov/edgar/sec-api-documentation>`_.
            Defaults to False.

    Returns:
        dict: Dictionary with information about concept_name.
            Dig into the data key for all period data.

    Examples:
        .. code::

            frames = get_xbrl_frames(user_agent="Name (email@example.com)",
                                     concept_name="Assets",
                                     year=2020,
                                     quarter=3,
                                     instantaneous=True)
            print(frames["data"][-1]["entityName"])
            # Prints "MOXIAN (BVI) INC"
            print(frames["data"][-1]["val"])
            # Prints 2295657
            print(frames["data"][-1]["accn"])
            # Prints "0001493152-22-013323"
    """
    # Create URL
    period = "CY{0}".format(year) if quarter is None else "CY{0}Q{1}".format(year, quarter)
    if instantaneous:
        period += "I"
    url = "{0}frames/us-gaap/{1}/{2}/{3}.json".format(XBRL_BASE, concept_name, currency, period)
    # Request and add to dictionary
    resp = requests.get(url, headers={"user-agent": user_agent})
    xbrl_frames = resp.json()
    return xbrl_frames
