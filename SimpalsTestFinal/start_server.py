
from aiohttp import web
import asyncio

from server_handlers import ServerHadler
from synchronizer_999_to_MondoDB import synchro_adverts_999_to_DB
from synchronizer_MongoDB_to_ElasticSearch import synchro_adverts_MongoDB_to_ElasticSearch

app = web.Application()
handler = ServerHadler()

app.add_routes([
    web.get('/', handler.index),
    web.get("/categories", handler.categories),
    web.get("/categories/{category_id}/subcategories", handler.subcategories),
    web.get("/categories/{category_id}/subcategories/{subcategory_id}/offer-types", handler.subcategory_offer_types_list),
    web.get("/phone_numbers", handler.users_phone_numbers_list),
    web.get("/features", handler.get_features_for_creating_a_new_advert),
    web.get("/dependent_options", handler.get_dependent_options),
    web.get("/adverts/{advert_id}", handler.get_advert),
    web.get("/adverts/{advert_id}/features", handler.get_features_of_existing_advert),
    web.post("/adverts", handler.add_advert),
    web.patch("/adverts/{advert_id}", handler.update_advert),
    web.get("/adverts", handler.get_adverts),
    web.post("/adverts/{advert_id}/republish", handler.republish_advert),
    web.post("/adverts/{advert_id}/color", handler.color_advert),
    web.put("/adverts/{advert_id}/access_policy", handler.set_advert_access_policy),
    web.get("/adverts/{advert_id}/autorepublisher", handler.get_advert_autorepublisher_settings),
    web.put("/adverts/{advert_id}/autorepublisher", handler.setup_advert_autorepublisher),
    web.post("/images", handler.images),
    web.get("/adverts/{advert_id}/booster/settings", handler.get_advert_booster_settings),
    web.post("/adverts/{advert_id}/booster/settings/", handler.setup_advert_booster),
    web.post("/adverts/{advert_id}/booster/pause/", handler.stop_advert_booster),
    web.post("/adverts/{advert_id}/booster/budget/overall", handler.increase_booster_budget_for_advert),
    web.post("/adverts/{advert_id}/booster/budget/daily_limit", handler.update_booster_daily_limit_for_advert),
    web.get("/elasticsearch/adverts/_search", handler.elasticsearch_get_adverts)
])


async def start_background_synchro(app):
    app['sunchronizer_999_to_MongoDB'] = asyncio.create_task(synchro_adverts_999_to_DB())
    app['sunchronizer_MongoDB_to_ElasticSearch'] = asyncio.create_task(synchro_adverts_MongoDB_to_ElasticSearch())

app.on_startup.append(start_background_synchro)
web.run_app(app)