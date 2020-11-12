
import requests
from aiohttp import web
from mongodb import MongoDB


class ServerHadler:
    BASE = "https://partners-api.999.md"
    auth = ("apuUo-UFpcW8Xe8gSeavLMFPITga", "")

    def __init__(self):
        pass

    async def index(self, request):
        text = """Use API-methods from https://999.md/api/documentation
    Examples:
    print(requests.get("http://localhost:8080/adverts").json())
    print(requests.get("http://localhost:8080/adverts/66092035").json())
    print(requests.get("http://localhost:8080/adverts?lang=ro").json())"""
        return web.Response(text=text)

    # Get all adverts from Mongo and website
    async def get_adverts(self, request):
        params = {
            "page_size": request.query.get("page_size"),
            "page": request.query.get("page"),
            "states": request.query.get("states"),
            "lang": request.query.get("lang")}

        # !!! First, /adverts returns all adverts from MongoDB.
        # but, becouse task was not that clear - /adverts can/may return all adverts from /
        # Johnny194 account on https://partners-api.999.md, on Exception, that should never be.
        try:
            lang = "ru"
            if params.get("lang") == "ro":
                lang = "ro"
            adverts = MongoDB().get_all_adverts_from_db_by_lang(lang)
            [advert.pop("_id") for advert in adverts]
            json_adverts = {"results": adverts}
            return web.json_response(json_adverts)

        # excepttion should never be, its just an example for fix, or refactor, or of main API of 999.md
        except Exception:
            response_obj = requests.get(self.BASE + f"/adverts", params=params, auth=self.auth)
            return web.json_response(body=response_obj.content)
    
    # returns 1 advert from MongoDB, works as API method GET /adverts/{advert_id} of https://partners-api.999.md
    async def get_advert(self, request):
        advert_id = request.match_info['advert_id']
        params = {"lang": request.query.get("lang")}
        try:
            lang = "ru"
            if params.get("lang") == "ro":
                lang = "ro"
            advert = MongoDB().get_advert_from_db(advert_id, lang)
            advert.pop("_id")
            return web.json_response(advert)
        except:
            response_obj = requests.get(self.BASE + f"/adverts/{advert_id}", params=params, auth=self.auth)
            return web.json_response(body=response_obj.content)

    # ElasticSearch simple handler
    async def elasticsearch_get_adverts(self, request):
        response_obj = requests.get(f"http://localhost:9200/adverts/_search?size=10000")
        return web.json_response(body=response_obj.content)

    async def categories(self, request):
        params = {"lang":  request.query["lang"]}
        response_obj = requests.get(self.BASE + f"/categories", params=params, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def subcategories(self, request):
        category_id = request.match_info['category_id']
        params = {"lang":  request.query["lang"]}
        response_obj = requests.get(self.BASE + f"/categories/{category_id}/subcategories", params=params, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def subcategory_offer_types_list(self, request):
        category_id = request.match_info['category_id']
        subcategory_id = request.match_info['subcategory_id']
        params = {"lang":  request.query["lang"]}
        response_obj = requests.get(self.BASE + f"/categories/{category_id}/subcategories/{subcategory_id}/offer-types", params=params, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def users_phone_numbers_list(self, request):
        params = {"lang":  request.query["lang"]}
        response_obj = requests.get(self.BASE + f"/phone_numbers", params=params, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def get_features_for_creating_a_new_advert(self, request):
        params = {"category_id": request.query.get("category_id"),
                  "subcategory_id": request.query.get("subcategory_id"),
                  "offer_type": request.query.get("offer_type"),
                  "lang": request.query.get("lang")
                  }
        response_obj = requests.get(self.BASE + "/features", params=params, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def get_dependent_options(self, request):
        params = {"subcategory_id": request.query.get("subcategory_id"),
                  "dependency_feature_id": request.query.get("dependency_feature_id"),
                  "parent_option_id": request.query.get("parent_option_id"),
                  "lang": request.query.get("lang")
                  }
        response_obj = requests.get(self.BASE + "/dependent_options", params=params, auth=self.auth)
        return web.json_response(body=response_obj.content)


    ############################################################################################################
    ###### Further functions are usable, but with 400, 500 error from "https://partners-api.999.md" on Johny194 account
    ###### More Explanations in /SimpalsTestDevelopersEdition/server_handlers.py and /Extra/test_requests.py
    async def get_features_of_existing_advert(self, request):
        advert_id = request.match_info['advert_id']
        params = {"lang": request.query.get("lang")}
        response_obj = requests.get(self.BASE + f"/adverts/{advert_id}/features", params=params, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def add_advert(self, request):
        advert_object_attributes = await request.json()
        response_obj = requests.post(self.BASE + f"/adverts", json=advert_object_attributes, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def update_advert(self, request):
        advert_id = request.match_info['advert_id']
        partial_json_data = await request.json()
        response_obj = requests.patch(self.BASE + f"/adverts/{advert_id}", json=partial_json_data, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def republish_advert(self, request):
        advert_id = request.match_info['advert_id']
        response_obj = requests.post(self.BASE + f"/adverts/{advert_id}/republish", auth=self.auth)
        return web.json_response(body=response_obj.content)
    # Запрещена

    async def color_advert(self, request):
        advert_id = request.match_info['advert_id']
        response_obj = requests.post(self.BASE + f"/adverts/{advert_id}/color", auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def set_advert_access_policy(self, request):
        advert_id = request.match_info['advert_id']
        access_policy_json = await request.json()
        response_obj = requests.put(self.BASE + f"/adverts/{advert_id}/access_policy", json=access_policy_json, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def get_advert_autorepublisher_settings(self, request):
        advert_id = request.match_info['advert_id']
        response_obj = requests.get(self.BASE + f"/adverts/{advert_id}/autorepublisher", auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def setup_advert_autorepublisher(self, request):
        print(request)
        advert_id = request.match_info['advert_id']
        autorepublisher_params = await request.json()
        response_obj = requests.put(self.BASE + f"/adverts/{advert_id}/autorepublisher", json=autorepublisher_params, auth=self.auth)
        print(response_obj.json())
        return web.json_response(body=response_obj.content)

    async def images(self, request):
        reader = await request.multipart()
        field = await reader.next()
        image_file = {field.name: await field.read()}
        response_obj = requests.post(self.BASE + f"/image", files=image_file, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def get_advert_booster_settings(self, request):
        advert_id = request.match_info['advert_id']
        response_obj = requests.get(self.BASE + f"/adverts/{advert_id}/booster/settings/", auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def setup_advert_booster(self, request):
        advert_id = request.match_info['advert_id']
        setup_booster_params = await request.json()
        response_obj = requests.post(self.BASE + f"/adverts/{advert_id}/booster/settings/", json=setup_booster_params, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def stop_advert_booster(self, request):
        advert_id = request.match_info['advert_id']
        response_obj = requests.post(self.BASE + f"/adverts/{advert_id}/booster/pause/", auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def increase_booster_budget_for_advert(self, request):
        advert_id = request.match_info['advert_id']
        budget = await request.json()
        response_obj = requests.post(self.BASE + f"/adverts/{advert_id}/booster/budget/overall", json=budget, auth=self.auth)
        return web.json_response(body=response_obj.content)

    async def update_booster_daily_limit_for_advert(self, request):
        advert_id = request.match_info['advert_id']
        daily_limit = await request.json()
        response_obj = requests.post(self.BASE + f"/adverts/{advert_id}/booster/budget/overall", json=daily_limit, auth=self.auth)
        return web.json_response(body=response_obj.content)
