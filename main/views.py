from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Song, Artist, Genre, Playlist, PlaylistSong, SearchHistory
from .forms import UserRegisterForm, AddToPlaylistForm, PlaylistForm, ChangeUsernameForm, ChangePasswordForm
import requests
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.http import JsonResponse
import random
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse

# Главная страница - показывает плейлист "Моя музыка" и другие плейлисты пользователя
@login_required
def home(request):
    selected_artist = request.GET.get('artist')
    default_playlist, created = Playlist.objects.get_or_create(
        user=request.user,
        name='Моя музыка',
        defaults={'name': 'Моя музыка'}
    )
    songs = default_playlist.songs.select_related(
        'artist'
    ).prefetch_related(
        'playlistsong_set'
    ).order_by('-playlistsong__added_date')
    
    # Получаем всех исполнителей из "Моя музыка" и сортируем по алфавиту
    artists = Artist.objects.filter(
        song__playlistsong__playlist=default_playlist
    ).distinct().values_list('id', 'name').order_by('name')
    
    # Фильтрация по исполнителю
    if selected_artist:
        songs = songs.filter(artist__id=selected_artist)
    
    playlists = Playlist.objects.filter(user=request.user).exclude(id=default_playlist.id)
    playlist_info = dict(
        Playlist.objects.filter(
            user=request.user,
            songs__in=songs
        ).values_list('songs__id', 'id')
    )
    
    return render(request, 'main/home.html', {
        'songs': songs,
        'playlists': playlists,
        'playlist_info': playlist_info,
        'default_playlist': default_playlist,
        'selected_artist': selected_artist,
        'artists': artists,
    })

# Регистрация нового пользователя
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})

# Создание нового плейлиста
@login_required
def create_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            messages.success(request, 'Плейлист успешно создан!')
            
            # Получаем URL и scroll position из POST запроса
            next_url = request.POST.get('next')
            scroll_position = request.POST.get('scroll_position')
            
            # Если есть next URL, перенаправляем туда с scroll position
            if next_url:
                if scroll_position:
                    return redirect(f"{next_url}#scroll={scroll_position}")
                return redirect(next_url)
            
            # По умолчанию перенаправляем на manage_playlists, если нет next URL
            return redirect('manage_playlists')
        else:
            # Добавляем конкретное сообщение об ошибке для длины названия
            if 'name' in form.errors:
                messages.error(request, 'Название плейлиста не должно превышать 21 символ.')
    else:
        form = PlaylistForm()
    return render(request, 'main/create_playlist.html', {'form': form})

# Добавление песни в плейлист
@login_required
def add_to_playlist(request, song_id=None):
    if request.method == 'POST':
        deezer_id = request.POST.get('deezer_id')
        title = request.POST.get('title')
        artist_name = request.POST.get('artist')
        preview_url = request.POST.get('preview_url')
        cover_url = request.POST.get('cover_url')
        playlist_id = request.POST.get('playlist')
        next_url = request.POST.get('next')
        scroll_position = request.POST.get('scroll_position')
        
        # Получаем или создаем исполнителя
        artist, _ = Artist.objects.get_or_create(name=artist_name)
        
        # Проверяем, существует ли уже песня с таким deezer_id
        try:
            song = Song.objects.get(deezer_id=deezer_id)
            # Обновляем информацию о песне, если она изменилась
            if song.preview_url != preview_url or song.cover_url != cover_url:
                song.preview_url = preview_url
                song.cover_url = cover_url
                song.save()
        except Song.DoesNotExist:
            # Создаем новую песню
            song = Song.objects.create(
                title=title,
                artist=artist,
                deezer_id=deezer_id,
                preview_url=preview_url,
                cover_url=cover_url
            )
        
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
            messages.info(request, 'Песня уже есть в плейлисте!')
        else:
            PlaylistSong.objects.create(playlist=playlist, song=song)
            messages.success(request, f'Песня добавлена в плейлист {playlist.name}!')
        
        # Используем next_url если он есть, иначе используем HTTP_REFERER или home
        if next_url:
            if scroll_position:
                return redirect(f"{next_url}#scroll={scroll_position}")
            return redirect(next_url)
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    # GET request - показываем форму выбора плейлиста
    deezer_id = request.GET.get('deezer_id')
    title = request.GET.get('title')
    artist = request.GET.get('artist')
    preview_url = request.GET.get('preview_url')
    cover_url = request.GET.get('cover_url')
    
    playlists = Playlist.objects.filter(user=request.user).exclude(name='Моя музыка')

    # Если нет плейлистов, перенаправляем на страницу создания плейлиста
    if not playlists.exists():
        messages.info(request, 'У вас пока нет плейлистов. Создайте новый плейлист.')
        scroll_position = request.GET.get('scroll')
        if scroll_position:
            return redirect(f"{reverse('create_playlist')}#scroll={scroll_position}")
        return redirect('create_playlist')
    
    form = AddToPlaylistForm(playlists=playlists)
    
    return render(request, 'main/add_to_playlist.html', {
        'form': form,
        'deezer_id': deezer_id,
        'title': title,
        'artist': artist,
        'preview_url': preview_url,
        'cover_url': cover_url,
        'playlists': playlists
    })

# Удаление песни из плейлиста
@login_required
def remove_from_playlist(request, playlist_id, song_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    song = get_object_or_404(Song, id=song_id)
    PlaylistSong.objects.filter(playlist=playlist, song=song).delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Песня удалена из плейлиста!'})
    messages.success(request, 'Песня удалена из плейлиста!')
    if playlist.name == 'Моя музыка':
        return redirect('home')
    return redirect('my_playlist', playlist_id=playlist.id)

# Просмотр содержимого плейлиста
@login_required
def my_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    songs = playlist.songs.select_related('artist').order_by('-playlistsong__added_date')
    
    return render(request, 'main/my_playlist.html', {'playlist': playlist, 'songs': songs})

# Поиск песен по названию или жанру
@login_required
def search(request):
    query = request.GET.get('q')
    selected_genre = request.GET.get('deezer_genre')
    deezer_genres = get_deezer_genres()
    deezer_results = []
    genre_warning = None
    search_history = []
    error_message = None
    
    # Проверка на одновременное использование поиска и фильтра по жанру
    if query and selected_genre:
        genre_warning = "Фильтр по жанру недоступен при поиске по названию."
        selected_genre = None  # Сбрасываем выбранный жанр
    
    # Получаем список ID песен в избранном
    user_playlist_songs = []
    if request.user.is_authenticated:
        default_playlist = Playlist.objects.filter(user=request.user, name='Моя музыка').first()
        if default_playlist:
            user_playlist_songs = list(default_playlist.songs.values_list('deezer_id', flat=True))
    
    # Сохраняем историю поиска без дубликатов
    if request.user.is_authenticated and query:
        SearchHistory.objects.filter(user=request.user, query=query).delete()
        SearchHistory.objects.create(user=request.user, query=query)
        search_history = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:10]
    elif request.user.is_authenticated:
        search_history = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    if selected_genre and not query:
        chart_url = f'https://api.deezer.com/chart/{selected_genre}/tracks'
        try:
            response = requests.get(chart_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            for item in data.get('data', []):
                deezer_id = item.get('id')
                deezer_results.append({
                    'id': deezer_id,
                    'title': item.get('title'),
                    'artist': item.get('artist', {}).get('name'),
                    'preview_url': item.get('preview'),
                    'cover_url': item.get('album', {}).get('cover_medium'),
                    'deezer_id': deezer_id,
                    'is_favorite': str(deezer_id) in user_playlist_songs
                })
        except requests.exceptions.RequestException as e:
            error_message = "Не удалось получить данные. Пожалуйста, попробуйте повторить поиск или перезагрузить страницу."
            print(f"Deezer API error: {str(e)}")
    
    if query:
        # Поиск в Deezer API
        search_url = f'https://api.deezer.com/search?q={query}'
        try:
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            for item in data.get('data', []):
                deezer_id = item.get('id')
                deezer_results.append({
                    'id': deezer_id,
                    'title': item.get('title'),
                    'artist': item.get('artist', {}).get('name'),
                    'preview_url': item.get('preview'),
                    'cover_url': item.get('album', {}).get('cover_medium'),
                    'deezer_id': deezer_id,
                    'is_favorite': str(deezer_id) in user_playlist_songs
                })
        except requests.exceptions.RequestException as e:
            error_message = "Не удалось получить данные. Пожалуйста, попробуйте повторить поиск или перезагрузить страницу."
            print(f"Deezer API error: {str(e)}")
    
    return render(request, 'main/search.html', {
        'deezer_results': deezer_results,
        'query': query,
        'selected_genre': selected_genre,
        'deezer_genres': deezer_genres,
        'genre_warning': genre_warning,
        'search_history': search_history,
        'error_message': error_message
    })

# Получение списка жанров из Deezer API
def get_deezer_genres():
    import requests
    # Словарь переводов Deezer жанров на русский (только из выпадающего списка)
    genre_translations = {
        'Pop': 'Поп',
        'Rap/Hip Hop': 'Рэп/Хип-хоп',
        'Rock': 'Рок',
        'Dance': 'Дэнс',
        'R&B': 'R&B',
        'Alternative': 'Альтернатива',
        'Electro': 'Электроника',
        'Folk': 'Фолк',
        'Reggae': 'Регги',
        'Jazz': 'Джаз',
        'Klassiek': 'Классика',
        'Films/Games': 'Фильмы/Игры',
        'Metal': 'Метал',
        'Soul & Funk': 'Соул и фанк',
        'Nederlandstalige muziek': 'Голландская музыка',
        'Afrikaanse Muziek': 'Африканская музыка',
        'Arabische Muziek': 'Арабская музыка',
        'Aziatische Muziek': 'Азиатская музыка',
        'Blues': 'Блюз',
        'Braziliaanse Muziek': 'Бразильская музыка',
        'Indische Muziek': 'Индийская музыка',
        'Kids': 'Детская музыка',
        'Latijnse muziek': 'Латиноамериканская',
    }
    try:
        response = requests.get('https://api.deezer.com/genre', timeout=5)
        if response.status_code == 200:
            genres = response.json().get('data', [])
            # Исключаем жанр 'All'
            genres = [g for g in genres if g['id'] != 0]
            # Добавляем перевод
            for g in genres:
                g['name_ru'] = genre_translations.get(g['name'], g['name'])
            return genres
    except requests.RequestException as e:
        print(f'Ошибка при обращении к Deezer API: {e}')
    return []

# Управление плейлистами пользователя
@login_required
def manage_playlists(request):
    playlists = Playlist.objects.filter(user=request.user).exclude(name='Моя музыка')
    return render(request, 'main/manage_playlists.html', {'playlists': playlists})

# Удаление плейлиста
@login_required
def delete_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    if request.method == 'POST':
        playlist.delete()
        messages.success(request, 'Плейлист успешно удален!')
        return redirect('manage_playlists')

# Переименование плейлиста
@login_required
def rename_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    if request.method == 'POST':
        new_name = request.POST.get('name')
        if new_name:
            playlist.name = new_name
            playlist.save()
            messages.success(request, 'Плейлист успешно переименован!')
            return redirect('manage_playlists')
    return render(request, 'main/rename_playlist.html', {'playlist': playlist})

# Добавление/удаление песни из избранного
@require_POST
@login_required
def add_to_favorites(request, song_id=None):
    deezer_id = request.POST.get('deezer_id')
    title = request.POST.get('title')
    artist_name = request.POST.get('artist')
    preview_url = request.POST.get('preview_url')
    cover_url = request.POST.get('cover_url')
    
    # Получаем или создаем исполнителя
    artist, _ = Artist.objects.get_or_create(name=artist_name)
    
    # Проверяем, существует ли уже песня с таким deezer_id
    try:
        song = Song.objects.get(deezer_id=deezer_id)
        # Обновляем информацию о песне, если она изменилась
        if song.preview_url != preview_url or song.cover_url != cover_url:
            song.preview_url = preview_url
            song.cover_url = cover_url
            song.save()
    except Song.DoesNotExist:
        # Создаем новую песню
        song = Song.objects.create(
            title=title,
            artist=artist,
            deezer_id=deezer_id,
            preview_url=preview_url,
            cover_url=cover_url
        )
    
    # Получаем или создаем плейлист "Моя музыка"
    playlist, _ = Playlist.objects.get_or_create(
        user=request.user,
        name='Моя музыка',
        defaults={'name': 'Моя музыка'}
    )
    
    # Проверяем, не добавлена ли песня уже в плейлист
    playlist_song = PlaylistSong.objects.filter(playlist=playlist, song=song).first()
    
    if playlist_song:
        # Если песня уже в плейлисте, удаляем её
        playlist_song.delete()
        msg = 'Песня удалена из избранного!'
        success = True
    else:
        # Если песни нет в плейлисте, добавляем её
        PlaylistSong.objects.create(playlist=playlist, song=song)
        msg = 'Песня добавлена в избранное!'
        success = True
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': success,
            'message': msg,
            'is_favorite': not bool(playlist_song)
        })
    
    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# Управление пользователями (только для администраторов)
@login_required
def manage_users(request):
    if not request.user.is_staff:
        messages.error(request, 'Нет доступа!')
        return redirect('home')
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'main/manage_users.html', {'users': users})

# Удаление пользователя
@login_required
def delete_user(request, user_id):
    if not request.user.is_staff:
        messages.error(request, 'Нет доступа!')
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Пользователь удалён!')
        return redirect('manage_users')
    return render(request, 'main/delete_user.html', {'user_obj': user})

# Очистка истории поиска
@require_POST
@login_required
def clear_search_history(request):
    SearchHistory.objects.filter(user=request.user).delete()
    return JsonResponse({'success': True})

# Страница радио
@login_required
def radio_view(request):
    return render(request, 'main/radio.html')

# Получение случайного трека для радио
@login_required
def get_random_track(request):
    try:
        # Получаем случайный жанр из списка популярных жанров
        genres = [132, 116, 152, 113, 165, 85, 106, 466, 144, 129, 173, 464, 169, 2, 12, 16, 75, 81, 99, 153]
        random_genre = random.choice(genres)
        
        # Получаем чарт для выбранного жанра
        chart_url = f'https://api.deezer.com/chart/{random_genre}/tracks'
        response = requests.get(chart_url)
        
        if response.status_code == 200:
            data = response.json()
            tracks = data.get('data', [])
            
            if tracks:
                # Выбираем случайный трек из чарта
                random_track = random.choice(tracks)
                
                # Формируем данные для ответа
                song_data = {
                    'title': random_track['title'],
                    'artist': {
                        'name': random_track['artist']['name']
                    },
                    'cover_url': random_track['album']['cover_medium'],
                    'preview_url': random_track['preview']
                }
                
                return JsonResponse(song_data)
        
        return JsonResponse({'error': 'Не удалось получить трек'}, status=404)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def change_username(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST, user=request.user)
        if form.is_valid():
            new_username = form.cleaned_data.get('new_username')
            request.user.username = new_username
            request.user.save()
            messages.success(request, 'Имя пользователя успешно изменено!')
            return redirect('home')
    else:
        form = ChangeUsernameForm(user=request.user)
    return render(request, 'main/change_username.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password1')
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Обновляем сессию
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('home')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'main/change_password.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Ваш аккаунт успешно удален!')
        return redirect('login')
    return render(request, 'main/delete_account.html')
