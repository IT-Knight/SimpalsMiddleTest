import json
from elasticsearch import Elasticsearch, helpers


class ElasticSearch:

    def __init__(self):
        self.es = Elasticsearch('http://localhost:9200')

    def get_adverts_from_ElasticSearch(self):
        all_adverts_from_ElasticSearch: dict = self.es.search(index="adverts", size=10000)
        return all_adverts_from_ElasticSearch["hits"]["hits"]

    def delete_adverts_from_ElasticSearch(self, filter_query):
        self.es.delete_by_query(index="adverts", body=filter_query)

    def update_and_insert_adverts_in_ElasticDB(self, adverts_from_MongoDB: list):
        actions = []
        for advert in adverts_from_MongoDB:
            advert: dict
            advert.update(dict(idd=str(advert["_id"]))) 
            advert.pop("_id")
            _id = advert["idd"]  # i don't know why i can't do this straight, there's raises an Exception Error.
            advert.pop("idd")
            actions.append({
                "_index": "adverts",
                "_id": _id,
                "_source": json.dumps(advert)
            })
        helpers.bulk(self.es, actions)


