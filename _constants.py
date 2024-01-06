import os
import yaml

VERSION_MAJOR = 2
VERSION_MINOR = 0
VERSION_REVISION = "0 RC1"

RESOURCES_FILE = os.path.join(os.path.split(__file__)[0], "resources.rcc")
SETTINGS_FILE = 'settings.dat'
PLATFORMS_CACHE_FILENAME = "database_cache.dat"

ARCHIVE_PLATFORMS_DATA = [
    {
        'name': 'Nintendo - NES',
        'format': '7z',
        'short_link': 'nointro.nes-headered',
        'sub_dir': 'nes',
    },
    {
        'name': 'Nintendo - SNES',
        'format': '7z',
        'short_link': 'nointro.snes',
        'sub_dir': 'snes',
    },
    {
        'name': 'Nintendo - 64',
        'format': '7z',
        'short_link': 'nointro.n64',
        'sub_dir':'n64',
    },
    {
        'name': 'Nintendo - 64DD',
        'format': '7z',
        'short_link': 'nointro.n64dd',
        'sub_dir': 'n64dd',
    },
    {
        'name': 'Sega - Master System / Mark III',
        'format': '7z',
        'short_link': 'nointro.ms-mkiii',
        'sub_dir': 'mastersystem',
    },
    {
        'name': 'Sega - Megadrive / Genesis',
        'format': '7z',
        'short_link': 'nointro.md',
        'sub_dir': 'genesis',
    },
    {
        'name': 'Sega - 32X',
        'format': '7z',
        'short_link': 'nointro.32x',
        'sub_dir': 'sega32x',
    },
    {
        'name': 'Sega - Game Gear',
        'format': '7z',
        'short_link': 'nointro.gg',
        'sub_dir': 'gamegear',
    },
    {
        'name': 'Sony - Playstation',
        'format': 'zip',
        'short_link': 'non-redump_sony_playstation',
        'sub_dir': 'psx',
    },
    {
        'name': 'Sony - Playstation',
        'format': '7z',
        'short_link': 'redump-sony-playstation-pal',
        'sub_dir': 'psx',
    },
    {
        'name': 'Sony - Playstation',
        'format': '7z',
        'short_link': 'rr-sony-playstation',
        'sub_dir': 'psx',
    },
    {
        'name': 'Sony - PSP',
        'format': '7z',
        'short_link': 'rr-sony-playstation-portable',
        'sub_dir': 'psp',
    },
    {
        'name': 'Sony - PSP',
        'format': 'zip',
        'short_link': 'redump.psp',
        'sub_dir': 'psp',
    },
    {
        'name': 'Sony - PSP',
        'format': 'zip',
        'short_link': 'redump.psp.p2',
        'sub_dir': 'psp',
    },
    {
        'name': 'Sony - Playstation 2',
        'format': 'zip',
        'parts': 27,
        'short_link': 'PS2_COLLECTION_PART$$',
        'sub_dir': 'ps2',
    },
    {
        'name': 'Sony - Playstation 3',
        'format': 'zip',
        'parts': 8,
        'short_link': 'PS3_NOINTRO_EUR_$$',
        'sub_dir': 'ps3',
    },
  ]


config_file_name = 'config.yaml'
if os.path.exists(config_file_name):
    with open(config_file_name, 'r') as file:
        ARCHIVE_PLATFORMS_DATA = yaml.safe_load(file)
else:
    with open(config_file_name, 'w') as file:
        yaml.dump(ARCHIVE_PLATFORMS_DATA, file)
