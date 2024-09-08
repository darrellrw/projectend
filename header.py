import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def get_config():
    return config

def set_config(section, key, value):
    config.set(section, key, value)
    with open("config.ini", "w") as configfile:
        config.write(configfile)

def save_config(folder_path, config_dict):
    config["Configure"] = config_dict
    with open(folder_path + "/config.ini", "w") as configfile:
        config.write(configfile)

def read_from_config_file(file_path):
    config_file = configparser.ConfigParser()
    config_file.read(file_path)
    return config_file