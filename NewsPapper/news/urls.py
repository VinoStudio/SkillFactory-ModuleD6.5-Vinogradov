from django.urls import path
from .views import NewsList, NewsDetail, CreateNews, UpdateNews, DeleteNews, SearchList, become_author, CategoryList, subscribe, unsubscribe

app_name = 'news'

urlpatterns = [
    path('', NewsList.as_view(), name='posts'),
    path('<int:pk>', NewsDetail.as_view(), name='post_details'),
    path('add/', CreateNews.as_view(), name='post_create'),
    path('<int:pk>/edit', UpdateNews.as_view(), name='post_update'),
    path('<int:pk>/delete', DeleteNews.as_view(), name='delete_post'),
    path('search/', SearchList.as_view(), name='search_post'),
    path('become_author/', become_author, name='author_status'),
    path('category/<str:name>', CategoryList.as_view(), name='categories'),
    path('subscribe/<str:name>', subscribe, name='subscribe'),
    path('unsubscribe/<str:name>', unsubscribe, name='unsubscribe'),
]