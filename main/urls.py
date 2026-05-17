from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    # Регистрация пользователя
    path('register/', views.register, name='register'),
    # Поиск песен
    path('search/', views.search, name='search'),
    # Создание плейлиста
    path('create-playlist/', views.create_playlist, name='create_playlist'),
    # Добавление песни в плейлист
    path('add-to-playlist/', views.add_to_playlist, name='add_to_playlist'),
    # Добавление в избранное
    path('add-to-favorites/', views.add_to_favorites, name='add_to_favorites'),
    # Удаление песни из плейлиста
    path('remove-from-playlist/<int:playlist_id>/<int:song_id>/', views.remove_from_playlist, name='remove_from_playlist'),
    # Просмотр плейлиста
    path('my-playlist/<int:playlist_id>/', views.my_playlist, name='my_playlist'),
    # Управление плейлистами
    path('manage-playlists/', views.manage_playlists, name='manage_playlists'),
    # Переименование плейлиста
    path('rename-playlist/<int:playlist_id>/', views.rename_playlist, name='rename_playlist'),
    # Удаление плейлиста
    path('delete-playlist/<int:playlist_id>/', views.delete_playlist, name='delete_playlist'),
    # Управление пользователями (админ)
    path('manage-users/', views.manage_users, name='manage_users'),
    # Удаление пользователя (админ)
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    # Очистка истории поиска
    path('clear-search-history/', views.clear_search_history, name='clear_search_history'),
    # Страница радио
    path('radio/', views.radio_view, name='radio'),
    # API для получения случайного трека
    path('api/random-track/', views.get_random_track, name='random_track'),
    path('change_username/', views.change_username, name='change_username'),
    path('change_password/', views.change_password, name='change_password'),
    path('delete_account/', views.delete_account, name='delete_account'),
] 