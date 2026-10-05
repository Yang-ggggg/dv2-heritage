"""Readable titles for tooltips: short forms in official National Archives series titles are spelled out.

The official title stays in the data as `series_title_official`; the edited one is shown on the page.
"""
SERIES_TITLE_EDITS = {
    "RAAF Officers Personnel files, 1921-1948":
        "Royal Australian Air Force officers' personnel files, 1921–1948",
    "RAAF Personnel files of Non-Commissioned Officers (NCOs) and other ranks, 1921-1948":
        "Royal Australian Air Force personnel files of non-commissioned officers and other ranks, 1921–1948",
    "ABC Talk Scripts - General":
        "Australian Broadcasting Commission radio talk scripts, general",
    "Property correspondence files, single number series with or without 'QL' prefix":
        "Property correspondence files, single number series",
    "Colour photographic (kodachrome) slides illustrating the life and career of Sir Keith Charles Owen Shann CBE":
        "Colour slides of the life and career of Sir Keith Charles Owen Shann",
    "Photographic colour negatives, chronological series with 'KN' or 'RKN' prefix and a single number suffix":
        "Photographic colour negatives, chronological series",
    "Stanley Fowler photographs showing the Australian fishing industry and coastline, numerical series with ‘LA’prefix":
        "Stanley Fowler photographs of the Australian fishing industry and coastline",
}

SERIES_TITLE_EDITS["Photographs (black and white, colour) of buildings, installations, sites, etc"] = (
    "Photographs (black and white, colour) of buildings, installations and sites")

PLACE_TITLE_EDITS = {
    "Western NSW, New South Wales": "Western New South Wales",
}


def readable_series_title(official_title):
    return SERIES_TITLE_EDITS.get(official_title, official_title)


def readable_place_title(place_title):
    return PLACE_TITLE_EDITS.get(place_title, place_title)
