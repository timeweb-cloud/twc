"""
This module defines variables that depend on Timeweb Cloud products.
They are subject to change at any time as cloud computing capabilities
expand or other infrastructure or product changes occur.
"""

# Service URLs
CONTROL_PANEL_URL = "https://timeweb.cloud/my"

# Location specific parameters. May change later.
REGIONS_WITH_IPV6 = ["ru-1", "ru-3", "pl-1", "nl-1", "kz-1"]
REGIONS_WITH_IMAGES = ["ru-1", "ru-3", "kz-1", "pl-1", "nl-1"]
REGIONS_WITH_LAN = ["ru-1", "ru-3", "nl-1", "pl-1", "de-1"]
ZONES_WITH_LAN = [
    "spb-1",
    "spb-3",
    "spb-4",
    "msk-1",
    "ams-1",
    "gdn-1",
    "fra-1",
]
# The default availability zones per regions.
REGION_ZONE_MAP = {
    "ru-1": "spb-3",
    "ru-2": "nsk-1",
    "ru-3": "msk-1",
    "kz-1": "ala-1",
    "pl-1": "gdn-1",
    "nl-1": "ams-1",
    "de-1": "fra-1",
}
