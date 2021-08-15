from django.urls import path
from giftPlaylist import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login_action, name='login'),
    path('callback', views.callback),
    path('error', views.error, name='error'),
    path('logout', views.logout_action, name='logout'),
    path('create_playlist', views.create_playlist, name='create_playlist'),
    path('playlist/<int:id>', views.playlist, name='playlist'),
    path('edit_playlist/<int:id>', views.edit_playlist, name='edit_playlist'),
    path('playlist_image/<int:id>', views.get_playlist_photo, name='playlist_photo'),
    path('search/<int:id>', views.search, name='search'),
    path('add_song', views.add_song, name='add_song'),
    path('remove_song', views.remove_song, name='remove_song'),
    path('song/<int:id>', views.song, name='song'),
    path('edit_song/<int:id>', views.edit_song, name='edit_song'),
    path('delete_song', views.delete_song, name='delete_song'),
    path('delete_playlist/<int:id>', views.delete_playlist, name='delete_playlist'),
    path('receiver_grid/<str:uuid>', views.receiver_grid, name='receiver_grid'),
    path('add_comment', views.add_comment, name='add_comment'),
    path('get_comments/<str:uuid>', views.get_comments, name='get_comments'),
]
