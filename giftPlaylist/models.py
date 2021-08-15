from django.db import models
import uuid
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone, dateformat

class User(AbstractBaseUser):
  username = models.CharField(max_length=50, unique=True)
  refresh_token = models.CharField(max_length=500)
  access_token = models.CharField(max_length=500)
  token_type = models.CharField(max_length=50)
  expires_in = models.DateTimeField()
  name = models.CharField(max_length=50)
  USERNAME_FIELD = 'username'
  

class Playlist(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT, default=None, related_name="playlists", blank=True, null=True) # TODO: change this to real user obj
  hidden_artwork = models.ImageField(blank=True)
  note = models.CharField(max_length=200, blank=True)
  name = models.CharField(max_length=50, default="New Playlist")
  link_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

  def __str__(self):
    return 'Playlist(id=' + str(self.name) + ')'

class Song(models.Model):
  playlist_id = models.ForeignKey(Playlist, on_delete=models.PROTECT, default=None, related_name="songs", blank=True, null=True)
  note = models.CharField(max_length=200, blank=True)
  album_artwork = models.CharField(max_length=200)
  duration = models.DurationField()
  name = models.CharField(max_length=50)
  artist = models.CharField(max_length=50)
  spotify_id = models.CharField(max_length=200) #id of the spotify song

  def __str__(self):
    return 'Song(id=' + str(self.name) + ')'

class Comment(models.Model):
  input_text = models.CharField(max_length=500, blank=False, null=False)
  date_time = models.DateTimeField(default=timezone.now)
  playlist = models.ForeignKey(Playlist, on_delete=models.PROTECT, default=None, related_name="comments")
  name = models.CharField(max_length=500, blank=False, null=False)

  def __str__(self):
    return 'Comment(id=' + str(self.id) + ')'
 
