import json
import os

default_config = {
    "prefix": "+",
    "token": "NjgzNDQ2MTUzMTMxMzI3NTM3.Xlrq1A.H2twVyLdvihsVcmHQZygvj94KBQ",
    "database": "postgresql://postgres:Web042914@172.17.0.2:5432/ditto",
}


class Config:
    def __init__(self, filename="config.json"):
        self.filename = filename
        self.config = {}
        if not os.path.isfile(filename):
            with open(filename, "w") as file:
                json.dump(default_config, file)
        with open(filename) as file:
            self.config = json.load(file)
        self.prefix = self.config.get("prefix", default_config.get("prefix"))
        self.token = self.config.get("token", default_config.get("token"))
        self.database = self.config.get("database", default_config.get("database"))
        self.nookipedia_key = self.config.get("nookipediaKey", "")
        self.topgg_key = self.config.get("topggKey")

    def store(self):
        c = {"prefix": self.prefix, "token": self.token, "database": self.database}
        with open(self.filename, "w") as file:
            json.dump(c, file)
