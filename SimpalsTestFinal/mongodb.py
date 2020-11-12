
from pymongo import MongoClient


class MongoDB:

    # init == connect to MongoDB
    def __init__(self):
        self.cluster = MongoClient("mongodb://127.0.0.1:27017")
        self.db = self.cluster["Johny194"]
        self.collection = self.db.Adverts

    # call needed functions
    def save_to_db(self, adverts: list):
        for advert in adverts:
            advert: dict
            self.collection.update_one({"id": advert["id"]}, {"$set": advert})

    def get_all_adverts_from_db_by_lang(self, lang="ru"):
        adverts = self.collection.find({"lang": lang})
        adverts = [x for x in list(adverts)]
        return adverts

    def get_all_adverts_from_db(self):
        adverts = self.collection.find()
        adverts = [x for x in list(adverts)]
        return adverts

    def get_advert_from_db(self, advert_id, lang="ru"):
        db_query = {"id": advert_id, "lang": lang}
        advert_json = self.collection.find_one(db_query)
        return advert_json

    def update(self, filter, update, upsert=False):
        self.collection.update_one(filter, {"$set": update}, upsert=upsert)

    def delete_one(self, filter):
        self.collection.delete_one(filter)

    def delete_many(self, filter):
        self.collection.delete_many(filter)

    # no need
    def _insert_one(self, advert: dict):
        self.collection.insert_one(advert)

    def _insert_many(self, adverts: list):
        pass








