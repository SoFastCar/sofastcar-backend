# Create your views here.
from django.db.models import Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from .models import CarZone
from .serializers import CarZoneSerializer, CarZonePricesSerializer


class CarZoneViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    """
        특정 쏘카존 정보 혹은 리스트 반환하는 API
        ---
        # 내용
            [GET] /carzones : 모든 쏘카존 디테일 정보 반환 (리스트)
            [GET] /carzones/123 : 특정 쏘카존 디테일 정보 반환
            [GET] /carzones/?keyword=성수동 : 쏘카존 이름, 주소 검색 기능
    """
    queryset = CarZone.objects.all()
    serializer_class = CarZoneSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_class(self):
        if self.action == 'info':
            return CarZonePricesSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = CarZone.objects.filter(Q(address__icontains=keyword) | Q(name__icontains=keyword))
        return queryset

    @action(detail=False)
    def distance(self, request, *args, **kwargs):
        """
            기준 위치(위도,경도) 및 거리에 따른 쏘카존 반환

                [GET] /carzones/distance?lat={float}&lon={float}&distance={float}

                lat : 위도 (float), 단위: degree
                lon : 경도 (float), 단위: degree
                distance : 거리 (float), 단위: km

                값이 없거나 부적절한 값일 경우 모두 400 에러로 반환합니다
        """
        lat_per_km = 1 / 109.958489129649955
        lon_per_km = 1 / 88.74

        try:
            std_lat = float(request.query_params.get('lat'))
            std_lon = float(request.query_params.get('lon'))
            distance = float(request.query_params.get('distance'))
        except Exception as e:
            return Response('lat=float, lon=float, distance=float are required',
                            status=status.HTTP_400_BAD_REQUEST)

        boundary = {
            'max_lat': std_lat + lat_per_km * distance,
            'min_lat': std_lat - lat_per_km * distance,
            'max_lon': std_lon + lon_per_km * distance,
            'min_lon': std_lon - lon_per_km * distance,
        }
        zones = CarZone.objects.filter(latitude__gte=boundary['min_lat'],
                                       latitude__lte=boundary['max_lat'],
                                       longitude__gte=boundary['min_lon'],
                                       longitude__lte=boundary['max_lon'], )

        serializer = self.get_serializer(zones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True)
    def info(self, request, *args, **kwargs):
        """
            기간에 따른 쏘카존 차량, 금액, 보험료, 시간표
            ---
            # 내용
                [GET] /carzones/260/info?date_time_start=202009251400&date_time_end=202009251600

                쏘카존 선택 후 대여기간 입력시 보여지는 차량과 가격, 보험료 목록 입니다.
                (마지막에 타임 테이블 같이 나오도록 하였습니다)
            ---
                쿼리 파라미터는 2020년09월26일14시00분 -> 202009261400(str값) (KST:한국시간기준)
                시간차에 의한 DB 권장사항에 따라 DB에는 UTC 기준으로 시간이 저장되고 이 값이 Response로 나갈때
                timezone을 KST로 변경하여 보여주게 됩니다

                사용자가 예약 종료 시점을 언제로 잡을지 모르기 때문에,
                해당 쏘카존에서 차량별 일단 사용자가 원하는 시작 시점부터 잡혀있는 타임테이블은 모두 반환하게 하였습니다
        """
        carzone = get_object_or_404(CarZone, id=kwargs.get('pk'))
        try:
            date_time_start = request.query_params.get('date_time_start')
            date_time_end = request.query_params.get('date_time_end')
        except Exception as e:
            return Response('wrong date_time_format : ex)202009051430',
                            status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
