from django.contrib import admin
from .models import Song, Playlist, PlaylistSong

# Административный интерфейс для управления песнями
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'upload_date')
    list_filter = ('artist', 'genre', 'upload_date')
    search_fields = ('title', 'artist__name')
    list_per_page = 20

# Административный интерфейс для управления плейлистами
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'user__username')
    list_per_page = 20

# Административный интерфейс для управления связями плейлист-песня
@admin.register(PlaylistSong)
class PlaylistSongAdmin(admin.ModelAdmin):
    list_display = ('playlist', 'song', 'added_date')
    list_filter = ('playlist', 'added_date')
    search_fields = ('playlist__name', 'song__title')
    list_per_page = 20
