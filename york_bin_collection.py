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
__date__ = "2023-10-09"

import datetime
from typing import Any
import re
import hassapi as hass
from string import Template
from typing import Optional
import requests

# -----------------------------------------------------------------------
YORK_BIN_API = "https://waste-api.york.gov.uk/api/Collections/GetBinCollectionDataForUprn/$uprn"
YORK_BIN_ICON_MAPPING = {"GARDEN": "mdi:pine-tree", "RECYCLING": "mdi:recycle", "REFUSE": "mdi:delete"}


# -----------------------------------------------------------------------
class YorkBinCollection(hass.Hass):
    # -----------------------------------------------------------------------
    def initialize(self):
        self.log("Initialising")
        # run this daily between 03:00 and 04:00
        self.run_daily(self.fetch_and_store_collection_data, start="03:00:00", random_start=0, random_end=3600)
        # initially load up the data
        self.fetch_and_store_collection_data()
        self.log("Done initialising")

    # -----------------------------------------------------------------------
    def fetch_and_store_collection_data(self, kwargs: Optional[dict] = None):
        self.log("Starting collection")
        data = self.retrieve_collection_data(self.args["uprn"])
        self.update_sensors(self.args["entity"], data)

    # -----------------------------------------------------------------------
    def update_sensors(self, sort_name: str, data: dict[str, Any]):
        # first find the types that will be collected next
        today = self.get_state("sensor.date")
        attributes = self.build_attributes(data, today)
        self.set_state(
            sort_name,
            state=attributes["next_collection"].isoformat(),
            attributes=attributes,
        )
        self.log("Updated sensor values")

    # -----------------------------------------------------------------------
    def retrieve_collection_data(self, uprn):
        """Retrieve the Bin collection data for a UPRN."""
        url = Template(YORK_BIN_API).substitute(uprn=uprn)
        try:
            r = requests.get(url, timeout=10.0)
            data = r.json()
        except ConnectionError as e:
            self.error("Unable to connect to the York bin collection API")
            raise (e)
        except ValueError as e:
            self.error("Unable to decode result from York bin collection API")
            raise (e)
        self.log("Successfully fetched bin collection data")

        self.collected_data = data
        return data

    # -----------------------------------------------------------------------
    def extract_date(self, datestr):
        """Extract a date from the JSON date info."""
        match = re.search(r"Date\((\d+)\)", datestr)
        altmatch = re.search(r"2\d{3}-\d{2}-\d{2}", datestr)
        if match:
            epoch = int(match.group(1)) / 1000
            result = datetime.date.fromtimestamp(epoch)
            return result
        elif altmatch:
            result = datetime.date.fromisoformat(datestr[:10])
            return result

        return None

    # -----------------------------------------------------------------------
    def build_attributes(self, data, today):
        """Rearrange bin collection data to be more useful."""
        service_data = sorted(self.collected_data["services"], key=lambda x: x["nextCollection"])
        today_date = self.extract_date(today)
        next_collection = self.extract_date(service_data[0]["nextCollection"])
        next_collection_types = []
        result = dict(
            services=[],
            next_collection=next_collection,
            next_collection_types=next_collection_types,
            friendly_name="Bin Collection",
            is_today=True if next_collection == today_date else False,
            is_tomorrow=True if next_collection == (today_date + datetime.timedelta(days=1)) else False,
        )
        for chunk in service_data:
            chunk["lastCollected"] = self.extract_date(chunk["lastCollected"])
            chunk["nextCollection"] = self.extract_date(chunk["nextCollection"])
            chunk["icon"] = YORK_BIN_ICON_MAPPING[chunk["service"]]

            if next_collection == chunk["nextCollection"]:
                next_collection_types.append(chunk)

            result[chunk["service"]] = chunk

        return result

    # -----------------------------------------------------------------------


# -----------------------------------------------------------------------
# Copyright 2020-2023 Nigel Metheringham
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
