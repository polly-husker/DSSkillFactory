import csv
import logging
import re
from json import loads

import scrapy
from requests import post


class AutoRuSpider(scrapy.Spider):
    name = 'auto_ru'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/cars/ac/all/']

    def parse(self, response, iteration_number=0, result_list=None):
        # self.log(response.text, level=logging.ERROR)
        if result_list == None:
            result_list = list()
        all_cars = response.xpath(
                f'//*[@id="initial-state"]/text()'
            ).extract_first()
        all_cars_dict = loads(all_cars)
        all_model_data = all_cars_dict["breadcrumbsPublicApi"]["data"][0]
        all_mark_data = all_cars_dict["breadcrumbsPublicApi"]["data"][1]
        all_marks = [
            mark["id"] for mark in
            all_mark_data["entities"]
        ]
        # all_marks = ['MINI', 'LEXUS', 'BMW']
        all_mark_models = [
            mark["id"] for mark in
            all_model_data["entities"]
        ]
        # self.log(all_marks, level=logging.ERROR)
        # self.log(all_mark_models, level=logging.ERROR)
        current_mark = all_model_data['mark']['id']
        if current_mark not in [
            'GAZ',
            'VAZ',
            'UAZ',
            'DAEWOO',
        ]:
        # if current_mark in ['MINI', 'LEXUS', 'BMW']:
            for model in all_mark_models:
                for page in range(1, 200):
                    url = "https://auto.ru/-/ajax/desktop/listing/"

                    HEADERS = {
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Connection': 'keep-alive',
                        'Content-Length': '137',
                        'content-type': 'application/json',
                        'Cookie': '_csrf_token=b9b55a86fcb97f1d9f3f5cfd688cdc34933361bc0f993a8a; autoru_sid=a%3Ag6007f1d12h92ns1iv1aki1331mm403r.06c40ab23da1727e6c28d4383ac9ecdf%7C1611133393187.604800.F3b2dgeD_eR74Un3wiMSug.ZVaCRfqwrJW6CBBxGIQoD6DKLADDPAwd82ewehpavBw; autoruuid=g6007f1d12h92ns1iv1aki1331mm403r.06c40ab23da1727e6c28d4383ac9ecdf; autoru_gdpr=1; suid=2f86fce14cc885f28b1a3c68d49f0466.b6c616b7dca7ce939de64f2da2214f1e; from_lifetime=1611142111171; from=direct; X-Vertis-DC=sas; yuidcs=1; yuidlt=1; yandexuid=156675331611133395; crookie=8W6qzAcHUlIBfGGPUf1QriXe/J/vEjS6XyYz2sc2fFfwfJHVMVjoBPDvmlGVduOveshBBs6nNssqbfmEhiECrTNUDOE=; cmtchd=MTYxMTEzMzM5ODEwNw==; popup_new_user=new; proven_owner_popup=1; gdpr=0; cycada=ArilX4Bp10IP4j3l5qgJKzrVUUG13dPRMT66OlbNOZc=; _ym_uid=1611133399152559058; _ym_d=1611142111; _ym_isad=2; mmm-search-accordion-is-open-cars=%5B0%5D; ',
                        'Host': 'auto.ru',
                        'origin': 'https://auto.ru/cars/all/',
                        'Referer': 'https://auto.ru/cars/all/',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
                        'x-client-app-version': 'a346bd28d0',
                        'x-page-request-id': 'cd74ad49c2719886e26c9fca085a8b35',
                        'x-client-date': '1611143873391',
                        'x-csrf-token': 'b9b55a86fcb97f1d9f3f5cfd688cdc34933361bc0f993a8a',
                        'x-requested-with': 'fetch',
                    }

                    param = {
                        'catalog_filter': [{
                            "mark": current_mark,
                            "model": model
                        }],
                        'section': "all",
                        'category': "cars",
                        'sort': "fresh_relevance_1-desc",
                        "top_days": 900,
                        "geo_radius": 200,
                        "geo_id": [213],
                        'page': page
                    }
                    resp = post(url, json=param, headers=HEADERS)
                    data = loads(resp.text)
                    # self.log(data, level=logging.ERROR)
                    if not data.get('offers'):
                        break
                    else:
                        for offer in data['offers']:
                            offer_data = from_elem_to_dict(
                                offer,
                                current_mark,
                                model
                            )
                            result_list.append(offer_data)
                self.log(str(len(result_list))+current_mark, level=logging.ERROR)
            try:
                keys = result_list[0].keys()
                with open('auto_ru_900.csv', 'w', newline='') as output_file:
                    dict_writer = csv.DictWriter(output_file, keys, delimiter=';')
                    dict_writer.writeheader()
                    dict_writer.writerows(result_list)
            except:
                pass
        next_page = f'https://auto.ru/cars/{all_marks[iteration_number]}/all/'
        self.log(next_page, level=logging.ERROR)
        yield response.follow(
            next_page,
            self.parse,
            cb_kwargs={
                "iteration_number": iteration_number+1,
                "result_list": result_list,
            }
        )


def from_elem_to_dict(d_elem, mark, model):
    d_dict = {}
    try:
        d_dict['bodyType'] = d_elem['vehicle_info']['configuration']['human_name']
    except:
        d_dict['bodyType'] = None

    try:
        d_dict['brand'] = d_elem['vehicle_info']['mark_info']['code']
    except:
        d_dict['brand'] = None

    # модель
    d_dict['model'] = model

    try:
        d_dict['fuelType'] = d_elem['lk_summary'].split()[-1]
    except:
        d_dict['fuelType'] = None

    try:
        d_dict['numberOfDoors'] = d_elem['vehicle_info']['configuration']['doors_count']
    except:
        d_dict['numberOfDoors'] = None

    try:
        d_dict['productionDate'] = d_elem['documents']['year']
    except:
        d_dict['productionDate'] = None

    try:
        d_dict['vehicleTransmission'] = d_elem['vehicle_info']['tech_param'][
            'transmission']
    except:
        d_dict['vehicleTransmission'] = None

    try:
        d_dict['enginePower'] = d_elem['vehicle_info']['tech_param']['power']
    except:
        d_dict['enginePower'] = None

    try:
        d_dict['mileage'] = d_elem['state']['mileage']
    except:
        d_dict['mileage'] = None

    try:
        d_dict['Привод'] = d_elem['lk_summary'].split(', ')[-2]
    except:
        d_dict['Привод'] = None

    try:
        d_dict['Руль'] = d_elem['vehicle_info']['steering_wheel']
    except:
        d_dict['Руль'] = None

    try:
        d_dict['Владельцы'] = int(float(d_elem['documents']['owners_number']))
    except:
        d_dict['Владельцы'] = None

    try:
        d_dict['ПТС'] = d_elem['documents']['pts']
    except:
        d_dict['ПТС'] = None

    try:
        d_dict['Таможня'] = d_elem['documents']['custom_cleared']
    except:
        d_dict['Таможня'] = None

    try:
        d_dict['Владение'] = d_elem['documents']['purchase_date']
    except:
        d_dict['Владение'] = None

    try:
        d_dict['Владение_year'] = d_elem['documents']['purchase_date']['year']
    except:
        d_dict['Владение_year'] = None

    try:
        d_dict['Владение_month'] = d_elem['documents']['purchase_date']['month']
    except:
        d_dict['Владение_month'] = None

    try:
        d_dict['price'] = d_elem['price_info']['RUR']
    except:
        d_dict['price'] = None

    # дата размещения объявления решил добавить
    try:
        d_dict['start_date'] = d_elem['additional_info']['hot_info'][
            'start_time']
    except:
        d_dict['start_date'] = None

    # статус объявления
    try:
        d_dict['hidden'] = d_elem['additional_info']['hidden']
    except:
        d_dict['hidden'] = None

    # 'acceleration'
    try:
        d_dict['acceleration'] = d_elem['vehicle_info']['tech_param']['acceleration']
    except:
        d_dict['acceleration'] = None

    # 'clearance_min'
    try:
        d_dict['clearance'] = d_elem['vehicle_info']['tech_param']['clearance_min']
    except:
        d_dict['clearance'] = None

    try:
        d_dict['fuel_rate'] = d_elem['vehicle_info']['tech_param']['fuel_rate']
    except:
        d_dict['fuel_rate'] = None

    try:
        d_dict['vendor'] = d_elem['vehicle_info']['vendor']
    except:
        d_dict['vendor'] = None

    try:
        d_dict['state_not_beaten'] = d_elem['state']['state_not_beaten']
    except:
        d_dict['state_not_beaten'] = None

    try:
        d_dict['modelDate'] = str(d_elem['vehicle_info']['super_gen']['year_from'])[:4]
    except:
        d_dict['modelDate'] = None




    try:
        try:
            try:
                d_dict['color'] = d_elem['vehicle_info']['complectation']['vendor_colors'][0]['stock_color']['name_ru']
            except:
                d_dict['color'] = d_elem['vehicle_info']['complectation']['vendor_colors'][1]['name_ru']
        except:
            d_dict['color'] = d_elem['color_hex']
    except:
        d_dict['color'] = None


    try:
        d_dict['saleId'] = d_elem['saleId']
    except:
        d_dict['saleId'] = None


    try:
        ed = d_elem['vehicle_info']['tech_param']['human_name'].split()[0]
        try:
            ed_float = float(ed)
            if ed_float > 9:
                raise
            d_dict['engineDisplacement'] = ed_float
        except:
            if (
                d_elem.get('vehicle_info')
                and d_elem['vehicle_info'].get('tech_param')
                and d_elem['vehicle_info']['tech_param'].get('human_name')
            ):
                all_floats = re.findall(
                    "\d\.\d+",
                    d_elem['vehicle_info']['tech_param']['human_name']
                )
                if float(all_floats[0]) > 6:
                    d_dict['engineDisplacement'] = d_elem['vehicle_info']['tech_param']['human_name']
                else:
                    d_dict['engineDisplacement'] = all_floats[0]

    except:
        d_dict['engineDisplacement'] = None


    return d_dict










