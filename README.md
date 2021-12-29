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


## Update 2021

At some point in 2021 the API I was using stopped working - in general it
failed to return any data. Later the API documentation was updated although
the datestamps did not appear to have been modified.  The new API is similar,
but less detailed, and of course most of the JSON keys have changed (there is
now a preference for the first character of a key to be lower case unlike
previously).

The code has been updated to work with the new API, including some partial
remapping of service types to the old version.


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

```yaml
blackbin:
  ImageName: blackbin
  binDescription: 180L GREY RUBBISH BIN x1
  collectedBy: City of York Council
  frequency: Every alternate Fri
  last: '2021-12-17'
  lastCollected: '2021-12-17T00:00:00'
  next: '2021-12-31'
  nextCollection: '2021-12-31T00:00:00'
  service: REFUSE
  wasteType: General domestic
box:
  ImageName: box
  binDescription: 55L BLACK RECYCLING BOX x3
  collectedBy: City of York Council
  frequency: Every alternate Fri
  last: '2021-12-24'
  lastCollected: '2021-12-24T00:00:00'
  next: '2022-01-07'
  nextCollection: '2022-01-07T00:00:00'
  service: RECYCLING
  wasteType: Paper/card, plastic/cans, glass
greenbin:
  ImageName: greenbin
  binDescription: 180L GREEN GARDEN BIN x1
  collectedBy: City of York Council
  frequency: ''
  last: '2021-11-26'
  lastCollected: '2021-11-26T00:00:00'
  next: '2022-03-18'
  nextCollection: '2022-03-18T00:00:00'
  service: GARDEN
  wasteType: Garden waste
next_collection: '2021-12-31'
next_collection_types:
- blackbin
updated: '2021-12-29T17:59:29.010803+00:00'
```

This data can then be used in other automations.

----
