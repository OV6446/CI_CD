from django import template

register = template.Library()

@register.filter
def get_playlist_id(playlist_info, song_id):
    return playlist_info.get(song_id) 