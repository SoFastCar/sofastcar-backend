from django.db import models


# ios 요청사항 : 광고 이벤트 이미지 파일들을 볼 수 있도록 해주세요
class EventPhoto(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(null=True, upload_to='EventImages/%Y/%m/%d')
