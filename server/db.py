import os
from flask_pymongo import pymongo


class OpBopDb:
    """ Class that handles OpBopDb DB operations """

    def __init__(self):
        try:
            client = pymongo.MongoClient(os.environ["MONGO_CLIENT"])
            self.db = client.get_database('flask_mongodb_atlas')
        except:
            self.db = None

    def reset_db(self, uri: str) -> None:
        """ Backup plan for when Heroku inevitably does the bad """
        client = pymongo.MongoClient(uri)
        self.db = client.get_database('flask_mongodb_atlas')
    
    def find_by_url(self, url: str) -> dict:
        """ Attempts to find cached article output, returns if found """
        hits = self.db.db["articles"].find({"url": url.lower()})

        if hits.count() == 0:
            return None
        else:
            ret = hits[0]
            ret.pop('_id')
            return ret
    
    def insert_article(self, article: dict) -> None:
        """ Adds article to db/OpBop cache """
        self.db.db["articles"].insert_one({
            "url": article["url"],
            "tldr": article["tldr"],
            "reduction": article["reduction"],
            "simplified": article["simplified"],
            "sensitivity": article["sensitivity"],
            "reliability": article["reliability"]
        })
