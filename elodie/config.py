"""Load config file as a singleton."""
from configparser import RawConfigParser
from os import path

from elodie import constants

config_file = '%s/config.ini' % constants.application_directory


def load_config():
    if hasattr(load_config, "config"):
        return load_config.config

    if not path.exists(config_file):
        return {}

    load_config.config = RawConfigParser()
    load_config.config.read(config_file)
    return load_config.config


def load_timestamp_definition():
    config = load_config()

    # If Filename is in the config, and contains a timestamp
    # definition, use this in destination filenames
    if('Filename' in config):
        config_filename = config['Filename']
        if('timestamp' in config_filename):
            constants.default_timestamp_definition = config_filename['timestamp']

