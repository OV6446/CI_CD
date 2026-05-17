from django.db import models
from django.contrib.auth.models import User

# Модель исполнителя
class Artist(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя исполнителя')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'

# Модель музыкального жанра
class Genre(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название жанра')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

# Модель песни
class Song(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название песни')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name='Исполнитель')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, verbose_name='Жанр')
    deezer_id = models.CharField(max_length=32, unique=True, null=True, blank=True, verbose_name='Deezer ID')
    preview_url = models.URLField(max_length=300, null=True, blank=True, verbose_name='Deezer превью')
    cover_url = models.URLField(max_length=300, null=True, blank=True, verbose_name='Обложка')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    
    def __str__(self):
        return f"{self.title} - {self.artist.name}"
    
    class Meta:
        verbose_name = 'Песня'
        verbose_name_plural = 'Песни'
        ordering = ['-upload_date']

# Модель плейлиста пользователя
class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField(max_length=21, verbose_name='Название плейлиста', default='Мой плейлист')
    songs = models.ManyToManyField(Song, through='PlaylistSong', verbose_name='Песни')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    class Meta:
        verbose_name = 'Плейлист'
        verbose_name_plural = 'Плейлисты'
        ordering = ['-created_at']

# Модель связи между плейлистом и песней
class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, verbose_name='Плейлист')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, verbose_name='Песня')
    added_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    class Meta:
        verbose_name = 'Песня в плейлисте'
        verbose_name_plural = 'Песни в плейлистах'
        unique_together = ['playlist', 'song']
        ordering = ['-added_date']

# Модель истории поиска пользователя
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    query = models.CharField(max_length=255, verbose_name='Поисковый запрос')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата поиска')

    class Meta:
        verbose_name = 'История поиска'
        verbose_name_plural = 'История поиска'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.query} ({self.created_at:%d.%m.%Y %H:%M})"
