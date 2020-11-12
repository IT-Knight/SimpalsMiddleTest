
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
import copy
import asyncio

from mongodb import MongoDB


async def synchro_adverts_999_to_DB():

    def get_convert_rate() -> str:
        response = requests.get("https://www.bnm.md/ru")
        BNM_bank_html = response.text
        soup = BeautifulSoup(BNM_bank_html, 'html.parser')
        current_convert_rate = soup.find("span", {'title': "Euro"}).findNext().getText()
        return current_convert_rate

    def convert_EUR_to_MDL(adverts: list):
        for advert in adverts:
            if advert["price"].get("unit") == "eur":
                advert["price"].update(unit="mdl")
                EUR_price = advert["price"].get("value")  # price in ЕUR
                Convert_rate = Decimal(get_convert_rate())  # current exchange rate
                # round price in MDL by banking method
                MDL_price = Decimal(EUR_price * Convert_rate).quantize(Decimal("1"),
                                                                       "ROUND_HALF_EVEN")  # type: 'decimal.Decimal'
                advert["price"].update(value=str(MDL_price))
                yield advert
            else:
                yield advert

    def get_adverts():
        auth = ("apuUo-UFpcW8Xe8gSeavLMFPITga", "")
        response = requests.get("https://partners-api.999.md/adverts", auth=auth)
        json_result = response.json()  # type: dict

        if json_result.get("adverts") is not None:  # check if adverts exists at all
            # getting adverts from website by iterating
            for advert in json_result["adverts"]:
                advert: dict
                # getting adverts on RU and RO both languages
                advert_data: dict = requests.get(f"https://partners-api.999.md/adverts/{advert['id']}?lang=ru",
                                                 auth=auth).json()
                advert_data.update(lang="ru")
                yield advert_data
                advert_data: dict = requests.get(f"https://partners-api.999.md/adverts/{advert['id']}?lang=ro",
                                                 auth=auth).json()
                advert_data.update(lang="ro")
                yield advert_data

    def delete_unnexisting_adverts_from_DB(user_adverts_data: list):
        user_adverts_id: list = [advert["id"] for advert in user_adverts_data]
        adverts_from_db = list(MongoDB().get_all_adverts_from_db())

        # delete unexisting adverts on website from MongoDB
        if len(adverts_from_db) > 0:
            adverts_id_from_db: list = [advert["id"] for advert in adverts_from_db]
            for advert in adverts_from_db[:]:
                # if advert id is not in new list - we delete it from MongoDB
                if advert["id"] not in user_adverts_id:
                    delete_filter = {"_id": advert["_id"]}
                    MongoDB().delete_one(delete_filter)
                    adverts_from_db.remove(advert)
        # there is was a bug, about same adverts or adverts copies that will be not deleted
        # a function needed to check adverts on copies and delete them
        # and... here it is, delete all copies, ecxept one version of advert, may be buggy too. Easy fixes.
        # It's an extra not that easy function.
        adverts_from_db_copy = copy.deepcopy(adverts_from_db)
        [advert.pop("_id") for advert in adverts_from_db_copy]
        index_set = set()
        for el in adverts_from_db_copy:
            copies_count = adverts_from_db_copy.count(el)
            if copies_count > 1:
                index = adverts_from_db_copy.index(el)
                index_set.add((index, copies_count))
        for index, copies_count in index_set:
            try:
                delete_filter = {"id": adverts_from_db[index]["id"], "lang": adverts_from_db[index]["lang"]}
            except KeyError:
                delete_filter = {"id": adverts_from_db[index]["id"]}
            for _ in range(copies_count-1):
                MongoDB().delete_one(delete_filter)

    def update_and_insert_adverts_in_DB(adverts_with_converted_MDL_price: list):
        for advert in adverts_with_converted_MDL_price:
            update_filter = {"id": advert["id"], "lang": advert["lang"]}
            MongoDB().update(update_filter, advert, upsert=True)

    while True:
        user_adverts_data: list = list(get_adverts())
        delete_unnexisting_adverts_from_DB(user_adverts_data)
        edited_adverts_with_MDL_price: list = list(convert_EUR_to_MDL(user_adverts_data))
        update_and_insert_adverts_in_DB(edited_adverts_with_MDL_price)
        await asyncio.sleep(1)