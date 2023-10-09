# York Bin Collection Data

York Council (in the UK) has an API which can tell you when bins (refuse,
garbage or your regional variant) wil be collected - and what type of collection
it will be.

This is documented at
[York Waste Collection Lookup](https://data.yorkopendata.org/dataset/waste-collection-lookup)

The previous version stopped working at the point where python was no longer
available within the HA container. So it has (finally) been ported to AppDaemon.

## Usage

- Set up AppDaemon - see the
  [documentation](https://community.home-assistant.io/t/home-assistant-community-add-on-appdaemon-4/163259)
- Put the script into the AppDaemon `apps` directory
- Edit the `apps/apps.yaml` file - see example below
- Ensure AppDaemon is running (if it was already it should restart when the
  above edits are made)
- Check for a `sensor.bin_collection` entity - check the attributes

The `apps/apps.yaml` file looks like this for me (with the UPRN set for your own
household)

```yaml
---
## comment out the original hello_world app
#hello_world:
#  module: hello
#  class: HelloWorld
york_bin_collection:
  module: york_bin_collection
  class: YorkBinCollection
  uprn: 100050567115
  entity: sensor.bin_collection
# end
```

You can obtain your UPRN from the links at
[York Waste Collection Lookup](https://data.yorkopendata.org/dataset/waste-collection-lookup)

To use your collection info you could add a card to the dashboard - an example
template would look like this:-

```jinja
Next collection on {{ strptime(states('sensor.bin_collection'),'%Y-%m-%d').strftime("%A (%-d %B, %Y) ") }}

Items collected:-

{% for set in state_attr('sensor.bin_collection', 'next_collection_types') %}
- <ha-icon icon="{{ set.icon }}"></ha-icon> {{ set.wasteType }}
{% endfor %}
```

If you are working with automations, the two boolean attributes `is_today` and
`is_tomorrow` can assist you in making sure it runs on the right day.

---
