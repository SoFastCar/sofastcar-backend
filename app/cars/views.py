# Create your views here.
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cars.models import Car
from cars.serializers import CarSerializer, CarDetailInfoSerializer


class CarViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 GenericViewSet):
    """
        특정 기간에 따른 차량과 가격 정보, 타임테이블을 반환하는 API
        ---
        # 내용
            [GET] /carzones/123/cars?date_time_start=202009251400&date_time_end=202009251600
            -> 특정 기간에 따른 해당 쏘카존 차량들의 디테일 정보 반환
            [GET] /carzones/123/cars/1?date_time_start=202009251400&date_time_end=202009251600
            -> 특정 기간에 따른 해당 차량 하나의 디테일정보 반환
        ---
            쿼리 파라미터는 2020년09월26일14시00분 -> 202009261400(str값) (KST:한국시간기준)
            시간차에 의한 DB 권장사항에 따라 DB에는 UTC 기준으로 시간이 저장되고 이 값이 Response로 나갈때
            timezone을 KST로 변경하여 보여주게 됩니다
    """
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_class(self):
        if self.action == 'info':
            return CarDetailInfoSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        queryset = queryset.filter(zone=self.kwargs.get('carzone_pk'))
        return super().filter_queryset(queryset)

    def list(self, request, *args, **kwargs):
        try:
            date_time_start = request.query_params.get('date_time_start')
            date_time_end = request.query_params.get('date_time_end')
        except Exception as e:
            return Response('wrong date_time_format : ex)202009051430',
                            status=status.HTTP_400_BAD_REQUEST)

        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def info(self, request, *args, **kwargs):
        """
            특정 차량의 디테일 정보와 가격 정보를 반환하는 API
            ---
            # 내용
            [GET] /carzones/123/cars/456/info
             -> 특정 쏘카존 차량의 디테일 정보 반환
        """
        return super().retrieve(request, *args, **kwargs)
