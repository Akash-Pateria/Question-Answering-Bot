from configobj import ConfigObj

#return value for a given key from conf file
def read_class(key):
    config = ConfigObj('fine_class.conf')
    value = config[key]
    return value
