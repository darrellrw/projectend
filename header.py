import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def get_config():
    return config

def set_config(section, key, value):
    config.set(section, key, value)
    with open("config.ini", "w") as configfile:
        config.write(configfile)