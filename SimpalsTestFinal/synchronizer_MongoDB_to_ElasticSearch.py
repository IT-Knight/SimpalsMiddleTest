
import asyncio
import copy

from elasticsearch_script import ElasticSearch
from mongodb import MongoDB


async def synchro_adverts_MongoDB_to_ElasticSearch():

    def get_adverts_from_MongoDB():
        adverts_from_MongoDB = list(MongoDB().get_all_adverts_from_db())
        if len(adverts_from_MongoDB) > 0:
            return adverts_from_MongoDB

    def delete_unnexisting_adverts_from_ElasticSearchDB(adverts_from_MongoDB: list):

        user_MongoDB_adverts_id: set = set(advert["id"] for advert in adverts_from_MongoDB)
        adverts_from_ElasticSearchDB: list = list(ElasticSearch().get_adverts_from_ElasticSearch())
        # delete unexisting adverts on website from ElasticSearchDB
        if len(adverts_from_ElasticSearchDB) > 0:
            for advert in adverts_from_ElasticSearchDB[:]:
                #  # if advert id is not in new list - it's deleted from ElasticSearch _index="adverts"
                if advert["_source"]["id"] not in user_MongoDB_adverts_id:
                    delete_filter = {"query": {"match": {"_id": advert["_id"]}}}
                    # print(delete_filter)
                    ElasticSearch().delete_adverts_from_ElasticSearch(delete_filter)
                    adverts_from_ElasticSearchDB.remove(advert)
        # there is may besame bug like in Mongo, about same adverts or advert copies that will be not deleted
        # a function check adverts on copies and delete them
        # this delete all copies to last, decision based on the re-recording this adverts on the next step, but without copies
        adverts_from_ElasticSearchDB_copy: list = copy.deepcopy(adverts_from_ElasticSearchDB)
        adverts_id_from_ElasticSearchDB_list = [x["_source"]["id"] for x in adverts_from_ElasticSearchDB_copy]
        Elastic_adverts_id_set = set(adverts_id_from_ElasticSearchDB_list)

        for el in Elastic_adverts_id_set:
            copies_count = adverts_id_from_ElasticSearchDB_list.count(el)
            if copies_count > 2:
                delete_filter = {"query": {"match": {"id": el}}}
                ElasticSearch().delete_adverts_from_ElasticSearch(delete_filter)

    while True:
        adverts_from_MongoDB: list = list(get_adverts_from_MongoDB())
        delete_unnexisting_adverts_from_ElasticSearchDB(adverts_from_MongoDB)
        ElasticSearch().update_and_insert_adverts_in_ElasticDB(adverts_from_MongoDB)
        await asyncio.sleep(1)