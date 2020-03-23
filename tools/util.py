import math
import pandas as pd
import re
from word2number import w2n


def normalize_int(num):
    """Convert a string of digits or English words to a numeric int"""
    if isinstance(num, str):
        return w2n.word_to_num(num.replace(",", ""))
    return num


def normalize_whitespace(text):
    """
    Replace non-breaking spaces with regular spaces,
    collapse runs of whitespace, and strip whitespace from the ends of the string.
    """
    s = text.replace(u"\xa0", u" ").replace(u"&nbsp;", " ").replace(r"\S+", " ")
    return re.sub("\s+", " ", s).strip()


def is_blank(text):
    """Return True if the string is composed of whitespace only"""
    return len(normalize_whitespace(text)) == 0


def camel_to_hyphens(name):
    """Turn a string in camel case to one with hyphens, and lowercase (e.g. ThisName -> this-name)"""
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def format_country(name):
    return name.replace(" ", "-").lower()


def format_int(val):
    if math.isnan(val):
        return ""
    return int(val)


la_name_to_code = None


def lookup_local_authority_code(name):
    # Get upper tier local authority name to code mapping.
    # Note that this does not include Scotland, but that's OK as Scotland areas are health boards, not local authorities.
    global la_name_to_code
    if la_name_to_code is None:
        la_mapping = pd.read_csv(
            "data/raw/Lower_Tier_Local_Authority_to_Upper_Tier_Local_Authority_April_2019_Lookup_in_England_and_Wales.csv"
        )
        la_name_to_code = dict(zip(la_mapping["UTLA19NM"], la_mapping["UTLA19CD"]))
        la_name_to_code["Cornwall and Isles of Scilly"] = la_name_to_code["Cornwall"]
        la_name_to_code["Hackney and City of London"] = la_name_to_code["Hackney"]

    return la_name_to_code.get(name, "")


hb_name_to_code = None


def lookup_health_board_code(name):
    global hb_name_to_code
    if hb_name_to_code is None:
        # Scotland
        hb_mapping = pd.read_csv(
            "data/raw/geography_codes_and_labels_hb2014_01042019.csv"
        )
        hb_mapping = hb_mapping[
            hb_mapping.HB2014QF != "x"
        ]  # drop those marked with an 'x' since they are no longer in use
        hb_name_to_code_scotland = dict(
            zip(hb_mapping["HB2014Name"], hb_mapping["HB2014"])
        )
        hb_name_to_code_scotland = {
            k.replace("NHS ", ""): v for k, v in hb_name_to_code_scotland.items()
        }

        # Wales
        hb_mapping = pd.read_csv(
            "data/raw/Local_Health_Boards_April_2019_Names_and_Codes_in_Wales.csv"
        )
        hb_name_to_code_wales = dict(zip(hb_mapping["LHB19NM"], hb_mapping["LHB19CD"]))
        hb_name_to_code_wales = {
            k.replace(" Teaching Health Board", "").replace(
                " University Health Board", ""
            ): v
            for k, v in hb_name_to_code_wales.items()
        }
        hb_name_to_code_wales["Cwm Taf"] = "W11000030"

        hb_name_to_code = {**hb_name_to_code_scotland, **hb_name_to_code_wales}

    return hb_name_to_code.get(name, "")
