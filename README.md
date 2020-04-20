# York Bin Collection Data

York Council (in the UK) has an API which can tell you when bins (refuse,
garbage or your regional variant) wil be collected - and what type of
collection it will be.

This is documented at [York Waste Collection
Lookup](https://data.yorkopendata.org/dataset/waste-collection-lookup)

This script is intended to work as a shim between the York Bin Collection data
and [Home Assistant](https://www.home-assistant.io/).  It is made available
under the Apache 2.0 License

Currently this is the first attempt and needs a little polish and error
checking.

## Usage

    $ york_bin_collection.py UPRN

You can obtain your UPRN from the links at [York Waste Collection
Lookup](https://data.yorkopendata.org/dataset/waste-collection-lookup)

The output is a JSON dictionary, with the following keys:-

- `next_collection` - The ISO8601 date string for the next bin collection
- `next_collection_types` - an array of strings giving the type(s) of the next bin collection
- `updated` - the datetime that the data was last updated

Additionally there is one entry for each bin collection type for the property,
which is keyed on the value of `ImageName` within the API data (which is a
short lowercase string).  For a typical residential properly this would be
something like:-

- `blackbin` - The standard non-recyclable refuse
- `greenbin` - The garden waste bin
- `box` - The recycling boxes (typically three boxes)

## Use With Home Assistant

Install the script into /config (or other accessible directory), and ensure
its executable - eg `chmod 755 york_bin_collection.py`

In `configuration.yaml` add the following stanza:-

    sensor:
      # York Bins Collection API - 3 sets, 1 for each bin
      - platform: command_line
        command: /config/york_bin_collection.py 100050567115
        name: Bin Collection
        scan_interval: 86400
        value_template: '{{ value_json.next_collection }}'
        json_attributes:
          - next_collection
          - next_collection_types
          - blackbin
          - greenbin
          - box
          - updated

Put your own UPRN onto the `command:` stanza (the one there is the one
supplied in the York Council API documentation).

You will need to reload/restart Home Assistant for the sensor to start picking
up.

You can then use the `Developer Tools` section to see the sensor data - go to
`States` and enter `sensor.bin_collection` in the entity field.  You will then
see something along the lines of state being `2020-04-24` and the State
attributes in YAML looking like:-

    next_collection: '2020-04-24'
    next_collection_types:
      - blackbin
    blackbin:
      BinType: GREY 180
      BinTypeDescription: Grey Bin 180L
      CollectionDay: FRI
      CollectionDayFull: Friday
      CollectionDayOfWeek: 5
      CollectionFrequency: Alternate Weeks
      CollectionFrequencyShort: WEEK 2
      CollectionPoint: FRONT
      CollectionPointDescription: Edge of Property at Front
      CollectionPointLocation: null
      CollectionType: GREY BIN/SACK
      CollectionTypeDescription: Grey Bin/Black Sack Collection
      ImageName: blackbin
      Locality: null
      MaterialsCollected: General Domestic
      NumberOfBins: '1'
      WasteType: GREY BIN/SACK
      WasteTypeDescription: Grey Bin/Black Sack Collection
      last: '2020-04-10'
      next: '2020-04-24'
    greenbin:
      BinType: GREEN 180
      BinTypeDescription: Green Bin 180L
      CollectionDay: FRI
      CollectionDayFull: Friday
      CollectionDayOfWeek: 5
      CollectionFrequency: Alternate Weeks
      CollectionFrequencyShort: WEEK 1
      CollectionPoint: FRONT
      CollectionPointDescription: Edge of Property at Front
      CollectionPointLocation: null
      CollectionType: GREEN
      CollectionTypeDescription: Green Collection
      ImageName: greenbin
      Locality: null
      MaterialsCollected: Garden Waste
      NumberOfBins: '1'
      WasteType: GREEN
      WasteTypeDescription: Green Collection
      last: '2019-11-29'
      next: null
    box:
      BinType: BOX 55
      BinTypeDescription: Box 55L
      CollectionDay: FRI
      CollectionDayFull: Friday
      CollectionDayOfWeek: 5
      CollectionFrequency: Alternate Weeks
      CollectionFrequencyShort: WEEK 1
      CollectionPoint: FRONT
      CollectionPointDescription: Edge of Property at Front
      CollectionPointLocation: null
      CollectionType: KERBSIDE
      CollectionTypeDescription: Kerbside Collection
      ImageName: box
      Locality: null
      MaterialsCollected: 'Paper/Card : Plastic/Cans : Glass'
      NumberOfBins: '3'
      WasteType: KERBSIDE
      WasteTypeDescription: Kerbside Collection
      last: '2020-04-17'
      next: '2020-05-01'
    updated: '2020-04-20 16:25:55.918518'
    friendly_name: Bin Collection

This data can then be used in other automations.

----
