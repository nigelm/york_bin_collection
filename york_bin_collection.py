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
__date__ = "2021-12-29"

import hassapi as hass
import re
from datetime import date, time, datetime, timezone
from string import Template
import json

import requests

# -----------------------------------------------------------------------
YORK_BIN_API = "https://waste-api.york.gov.uk/api/Collections/GetBinCollectionDataForUprn/$uprn"
YORK_BIN_ATTRIBUTES = (
    "binDescription",
    "collectedBy",
    "frequency",
    "lastCollected",
    "nextCollection",
    "service",
    "wasteType",
)
YORK_BIN_MAPPING = {"GARDEN": "greenbin", "RECYCLING": "box", "REFUSE": "blackbin"}


# -----------------------------------------------------------------------
def json_convert(thing):
    """Handle the date/datetime objects in JSON encoding."""
    if isinstance(thing, date):
        return thing.isoformat()
    elif isinstance(thing, datetime):
        return thing.isoformat()


# -----------------------------------------------------------------------
class YorkBinCollection(hass.Hass):
    # -----------------------------------------------------------------------
    def initialize(self):
        self.log("york_bin_collection: Initialising")
        self.run_minutely(self.fetch_and_store_collection_data, start=time(hour=0, minute=0, second=0))
        self.log("york_bin_collection: Done initialising")

    # -----------------------------------------------------------------------
    def fetch_and_store_collection_data(self, kwargs):
        self.log("Starting collection")
        data = self.retrieve_collection_data(self.args["uprn"])
        result = self.munge_data(data)
        self.log("Fetched and munged bin collection data")
        self.set_state(
            self.args["entity"],
            state=json.dumps(result, sort_keys=True, indent=2, default=json_convert),
            attributes={"friendly_name": "Bin Collection"},
        )
        self.log("Data written into sensor")

    # -----------------------------------------------------------------------
    def retrieve_collection_data(self, uprn):
        """Retrieve the Bin collection data for a UPRN."""
        url = Template(YORK_BIN_API).substitute(uprn=uprn)
        try:
            r = requests.get(url, timeout=10.0)
            json = r.json()
        except ConnectionError as e:
            self.error("Unable to connect to the York bin collection API")
            raise (e)
        except ValueError as e:
            self.error("Unable to decode result from York bin collection API")
            raise (e)
        self.log("Successfully fetched bin collection data")

        return json

    # -----------------------------------------------------------------------
    def extract_date(self, datestr):
        """Extract a date from the JSON date info."""
        match = re.search(r"Date\((\d+)\)", datestr)
        altmatch = re.search(r"2\d{3}-\d{2}-\d{2}", datestr)
        if match:
            epoch = int(match.group(1)) / 1000
            result = date.fromtimestamp(epoch)
            return result
        elif altmatch:
            result = date.fromisoformat(datestr[:10])
            return result

        return None

    # -----------------------------------------------------------------------
    def munge_data(self, data):
        """Rearrange bin collection data to be more useful."""
        result = {}
        next_collection = None
        next_collection_types = None
        for chunk in data["services"]:
            section = YORK_BIN_MAPPING[chunk["service"]]
            section_data = {
                "last": self.extract_date(chunk["lastCollected"]).isoformat(),
                "next": self.extract_date(chunk["nextCollection"]).isoformat(),
                "ImageName": section,
            }

            # copy all the attributes across
            for item in YORK_BIN_ATTRIBUTES:
                if item in chunk:
                    if isinstance(chunk, datetime):
                        section_data[item] = chunk[item].isoformat()
                    else:
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
        result["updated"] = datetime.now(timezone.utc).isoformat()
        return result

    # -----------------------------------------------------------------------


# -----------------------------------------------------------------------
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
