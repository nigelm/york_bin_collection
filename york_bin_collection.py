#!/usr/bin/env python3
#
"""
york_bin_collection.py - Retrieve data on the next bin collection

Summary:
    york_bin_collection.py UPRN

Parameters:
    UPRN - The Unique Property Reference Number for the address

Retrieves information on the next York bin collection, and outputs a a JSON
dictionary with data rearranged to make it more convenient for use as a Home
Assistant sensor.

"""
__author__ = ["[Nigel Metheringham](https://blog.dotdot.cloud/)"]
__date__ = "2020-04-20"

import json
import re
import sys
from datetime import date, datetime, timezone

import requests

YORK_BIN_API = (
    "https://doitonline.york.gov.uk/BinsApi/EXOR/getWasteCollectionDatabyUprn"
)
YORK_BIN_ATTRIBUTES = (
    "BinType",
    "BinTypeDescription",
    "CollectionDay",
    "CollectionDayFull",
    "CollectionDayOfWeek",
    "CollectionFrequency",
    "CollectionFrequencyShort",
    "CollectionPoint",
    "CollectionPointDescription",
    "CollectionPointLocation",
    "CollectionType",
    "CollectionTypeDescription",
    "ImageName",
    "Locality",
    "MaterialsCollected",
    "NumberOfBins",
    "WasteType",
    "WasteTypeDescription",
)


def retrieve_collection_data(uprn):
    """Retrieve the Bin collection data for a UPRN."""
    payload = {"uprn": uprn}
    try:
        r = requests.get(YORK_BIN_API, params=payload)
        json = r.json()
    except ConnectionError:
        sys.exit("Unable to connect to the York bin collection API")
    except ValueError:
        sys.exit("Unable to decode result from York bin collection API")

    return json


def extract_date(datestr):
    """Extract a date from the JSON date info."""
    match = re.search(r"Date\((\d+)\)", datestr)
    if match:
        epoch = int(match.group(1)) / 1000
        result = date.fromtimestamp(epoch)
        return result
    return None


def munge_data(data):
    """Rearrange bin collection data to be more useful."""
    result = {}
    next_collection = None
    next_collection_types = None
    for chunk in data:
        section = chunk["ImageName"]
        section_data = {
            "last": extract_date(chunk["LastCollection"]),
            "next": extract_date(chunk["NextCollection"]),
        }

        # copy all the attributes across
        for item in YORK_BIN_ATTRIBUTES:
            section_data[item] = chunk[item]

        # package this into the result
        result[section] = section_data

        # note down the actual next collection
        if not next_collection:
            next_collection = section_data["next"]
            next_collection_types = [section]
        elif section_data["next"] and section_data["next"] < next_collection:
            next_collection = section_data["next"]
            next_collection_types = [section]
        elif section_data["next"] and section_data["next"] == next_collection:
            next_collection_types.append(section)
    # add the overall infomration items
    result["next_collection"] = next_collection
    result["next_collection_types"] = next_collection_types
    result["next_collection_types"] = next_collection_types
    result["updated"] = datetime.now(timezone.utc)
    return result


def json_convert(thing):
    """Handle the date/datetime objects in JSON encoding."""
    if isinstance(thing, date):
        return thing.isoformat()
    elif isinstance(thing, datetime):
        return thing.isoformat()


if __name__ == "__main__":
    data = retrieve_collection_data(sys.argv[1])
    munged_data = munge_data(data)
    print(json.dumps(munged_data, sort_keys=True, indent=2, default=json_convert))

# Copyright 2020 Nigel Metheringham
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
