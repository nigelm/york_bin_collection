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

import datetime
import hassapi as hass
from string import Template
from typing import Optional
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
        self.retrieve_collection_data(self.args["uprn"])
        self.update_sensors(self.args["entity"])

    # -----------------------------------------------------------------------
    def update_sensors(self, base_name: str):
        # first find the types that will be collected next
        sorted_collections = sorted(self.collected_data["services"], key=lambda x: x["nextCollection"])
        next_collection = sorted_collections[0]["nextCollection"]
        collection_types = []
        collection_description = []
        for collection in sorted_collections:
            if collection["nextCollection"] > next_collection:
                break
            collection_types.append(collection["service"])
            collection_description.append(collection["wasteType"])
        self.set_state(
            f"{base_name}_next_collection",
            state=next_collection[:10],
            attributes={"friendly_name": "Next Bin Collection Date"},
        )
        self.set_state(
            f"{base_name}_collection_types",
            state=collection_types,
            attributes={"friendly_name": "Bin Collection Types"},
        )
        self.set_state(
            f"{base_name}_collection_descriptions",
            state=collection_description,
            attributes={"friendly_name": "Bin Collection Type Descriptions"},
        )
        self.set_state(
            f"{base_name}_collection_description",
            state=", ".join(collection_description),
            attributes={"friendly_name": "Bin Collection Description"},
        )
        self.set_state(
            f"{base_name}_is_today",
            state=True if datetime.date.today().isoformat() == next_collection else False,
            attributes={"friendly_name": "Bin Collection is Today"},
        )
        self.set_state(
            f"{base_name}_is_tomorrow",
            state=True
            if (datetime.date.today() + datetime.timedelta(days=1)).isoformat() == next_collection
            else False,
            attributes={"friendly_name": "Bin Collection is Tomorrow"},
        )
        self.set_state(
            f"{base_name}_updated",
            state=datetime.date.today().isoformat(),
            attributes={"friendly_name": "Bin Collection Last Update"},
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
