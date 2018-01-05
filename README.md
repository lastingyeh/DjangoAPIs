### Create APIs Project

##### 建立專案流程

+ 虛擬環境建立
  
        > virtualenv env-api
  
+ 啟動虛擬環境

        > source env-api/bin/activate
  
+ 安裝 packages ( 安裝資訊定義在 requirements.txt )

        (env-api) > pip install -r requirements.txt
        
+ 建立專案

        (env-api) > django-admin startproject RestAPIs
        
+ 建立應用程式 1
        
        (env-api) > cd RestAPIs
        
        (env-api) > python manage.py startapp musics
        
+ 建立應用程式 2 (針對不同 Request 操作設定權限)

        (env-api) > cd RestAPIs
        
        (env-api) > python manage.py startapp shares
        
+ 加入 superuser 帳號

        (env-api) > python manage.py createsuperuser 
        
        (env-api) > ... (新增帳號操作)
        
### API 建立

##### 基本架構

1. RestAPIs.['urls'] => musics.['views'] => .['models','serializers' => .['models']]
    
2. RestAPIs.['urls'] => shares.['views'] => .['models','serializers' => .['models']]
    
##### 加入權限
    
1. musics.['views'] + permission_classes = (IsAuthenticated,)
    
2. RestAPIs.['urls'] + url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    
3. 新增權限後，必須登入後才能存取 APIs
    
4. 個別權限設定 (shares)

    _shares/views.py_
    
    ```python
        
        class ShareViewSet(viewsets.ModelViewSet):
            queryset = Share.objects.all()
            serializer_class = ShareSerializer
            ...
        
            def get_permissions(self):
                if self.action in ('create',):
                    self.permission_classes = [IsAuthenticated]
        
                return [permission() for permission in self.permission_classes]
        
            # GET api/shares/
            def list(self, request, **kwargs):
                users = Share.objects.all()
                serializer = ShareSerializer(users, many=True)
        
                return Response(serializer.data, status=status.HTTP_200_OK)
        
            # POST api/shares/
            @permission_classes((IsAuthenticated,))
            def create(self, request, **kwargs):
                name = request.data.get('name')
                users = Share.objects.create(name=name)
                serializer = ShareSerializer(users)
        
                return Response(serializer.data, status=status.HTTP_201_CREATED)
   ```
    
### Parser 設定 
    
##### 設定 Content-Type 只允許 application/json

_settings.py_

```python

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    )
}
    
```
    
##### 設定 單一 Content-Type

_shares/views.py_ 

```python

from rest_framework.parsers import JSONParser
...
class ShareViewSet(viewsets.ModelViewSet):
    ...
    # 
    parser_classes = (JSONParser,)
    ...

```

*Postman Hints* 

    1. Headers Set - "Content-Type":"application/json;charset=utf-8"
    
    2. POST Data - Body/raw : {"name":"xxx"}
    
[Parser 更多資訊...](http://www.django-rest-framework.org/api-guide/parsers/#parsersr)  

### 自定義 Router

_musics/views.py_

```python

from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import detail_route, list_route

from .models import Music
from .serializers import MusicSerializer

class MusicViewSet(viewsets.ModelViewSet):
    queryset = Music.objects.all()
    serializer_class = MusicSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    # /api/music/{pk}/ds/ # use alias path-name (url_path='ds')
    @detail_route(methods=['get'], url_path='ds') 
    def detail(self, request, pk=None):
        music = get_object_or_404(Music, pk=pk)
        result = {
            'singer': music.singer,
            'song': music.song
        }

        return Response(result, status=status.HTTP_200_OK)

    # /api/music/all_singer/
    @list_route(methods=['get'])
    def all_singer(self, request):
        music = Music.objects.values_list('singer', flat=True).distinct()

        return Response(music, status=status.HTTP_200_OK)

```

### Test APIs

_musics/test.py_

```python

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from .models import Music


class MusicViewTestCase(APITestCase):
    # url_reverse = reverse('api:music-list')
    url = '/api/music/'
    url_detail = '/api/music/{}/'
    # url_detail_route_reverse = reverse('api:music-detail', kwargs={'pk': 1})
    url_detail_route = '/api/music/{}/ds/'
    url_list_route = '/api/music/all_singer/'

    def setUp(self):
        print('SetUP')

        self.client = APIClient()

        User.objects.create_user(username='test_user', password='password123')

        self.client.login(username='test_user', password='password123')

        self.request_data = {
            'song': 'song_test',
            'singer': 'singer_test'
        }

        self.music = Music.objects.create(song='song_test', singer='singer_test')

    # Test POST (Create Music)
    def test_api_music_create(self):
        print('test_api_music_create')

        self.response = self.client.post(
            self.url,
            self.request_data,
            format='json'
        )

        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Music.objects.count(), 2)
        self.assertEqual(Music.objects.get(pk=self.music.id).song, 'song_test')
        self.assertEqual(Music.objects.get(pk=self.music.id).singer, 'singer_test')

    # Test GET (Get All Musics)
    def test_api_music_retrieve(self):
        print('test_api_music_retrieve')

        music = Music.objects.get(pk=self.music.id)

        response = self.client.get(self.url_detail.format(self.music.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('song', None), music.song)
        self.assertEqual(response.data.get('singer', None), music.singer)

    # Test PATCH (Update partial data for song)
    def test_api_music_partial_update(self):
        print('test_api_music_partial_update')

        update_song = {'song': 'song_update'}

        response = self.client.patch(self.url_detail.format(self.music.id), update_song, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('song', None), update_song.get('song', None))

    # Test PUT (Update all data for Music)
    def test_api_music_update(self):
        print('test_api_music_update')

        update_song = {'song': 'song_update', 'singer': 'singer_update'}

        response = self.client.put(self.url_detail.format(self.music.id), update_song, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('song', None), update_song.get('song'))
        self.assertEqual(response.data.get('singer', None), update_song.get('singer'))

    # Test DELETE (Delete Music)
    def test_api_music_delete(self):
        print('test_api_music_delete')

        response = self.client.delete(self.url_detail.format(self.music.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Test GET (detail_route -> alias route-name: ds)
    def test_api_music_detail_route(self):
        print('test_api_music_detail_route')

        music = Music.objects.get(pk=self.music.id)

        response = self.client.get(self.url_detail_route.format(self.music.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('song', None), music.song)
        self.assertEqual(response.data.get('singer', None), music.singer)

    # Test GET (list_route)
    def test_api_music_list_route(self):
        print('test_api_music_list_route')

        music = Music.objects.values_list('singer', flat=True).distinct()

        response = self.client.get(self.url_list_route)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(next(iter(response.data)), next(iter(music)))
        
```

### 感謝原作者 [twtrubiks](https://github.com/twtrubiks)

##### 參考 1： https://github.com/twtrubiks/django-rest-framework-tutorial
##### 參考 2： https://www.youtube.com/watch?v=lunVXqMVsrs&feature=youtu.be
##### 參考 3： https://www.youtube.com/watch?v=Qnir5iFpMyQ&feature=youtu.be


### PyCharm 相關
    
##### 瀏覽 Database 結構

+ 安裝 plugins 路徑 : Preferences / Plugins / Browse Repositories / Database Navigator

![alt tag](https://github.com/lastingyeh/DjangoAPIs/blob/master/res/browse_repos.jpeg)
        
##### 解決 pycharm import 上層模組錯誤問題

+ 加入 Source Folders 參考路徑 : (Right Click) RestAPIs => (Sources)

![alt tag](https://github.com/lastingyeh/DjangoAPIs/blob/master/res/plugins_path.jpeg)

##### 設定 Django Debug Config

![alt tag](https://github.com/lastingyeh/DjangoAPIs/blob/master/res/debug.jpeg)

