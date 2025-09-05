from configparser import ConfigParser

"""
Файл, в котором инициализируется переменная
для доступа к конфигам из config.ini
"""

config = ConfigParser()
config.read("config.ini")
