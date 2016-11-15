import configparser
def load(name, defaults={}):
    config = configparser.ConfigParser()
    config.read("config/%s.ini"%name)
    for cat in defaults:
        if cat not in config:
            config[cat]=defaults[cat]
        else:
            for key in defaults[cat]:
                if key not in config[cat]:
                    config[cat][key]=defaults[cat][key]            
    save(name, config)
    return config

def save(name, config):
    with open("config/%s.ini"%name, "w") as configfile:
        config.write(configfile)
