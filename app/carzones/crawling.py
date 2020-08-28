import requests
import xmltodict

from .models import CarZone


class Crawling:
    # auth_key : 공공데이터 오픈 API 접속
    auth_key = '0s72jicHY1E68xaoFc7QOBVPw%2Fz371oN%2BQ2D22%2BAIvjSJsp5RmE5XsXobvWD0mHeo0MPsShSNMTm3%2FAiKM9eAw%3D%3D'
    url = 'http://openapi.tago.go.kr/openapi/service/CarSharingInfoService/getCarZoneListByAddr'
    queryParams = '?' + 'ServiceKey=' + f'{auth_key}' \
                  + '&pageNo=' + '1' \
                  + '&numOfRows=' + '350' \
                  + '&zoneAddr=' + '서울'

    url = url + queryParams
    content = requests.get(url).content

    # xml 형식 -> 딕셔너리 형태로 변경
    content_to_dict = xmltodict.parse(content)

    entry_list = []
    for item in content_to_dict['response']['body']['items']['item']:
        # 운영종료 제외
        if not '운영종료' in item['zoneName']:
            entry_list.append(item)

    for entry in entry_list:
        CarZone.objects.get_or_create(
            address=entry['address'],
            latitude=entry['latitude'],
            longitude=entry['longitude'],
            zone_id=entry['zoneId'],
            name=entry['zoneName']
        )


start_crawling = Crawling()
start_crawling
