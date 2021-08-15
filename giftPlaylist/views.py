from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.files.images import ImageFile 

from django.utils import timezone
from datetime import timedelta
from giftPlaylist.models import User, Playlist, Song, Comment
from giftPlaylist.credentials import REDIRECT_URI, CLIENT_SECRET, CLIENT_ID
from django.http import HttpResponse, Http404


from giftPlaylist.forms import PlaylistForm

#from PIL import Image
from io import BytesIO

import json
from urllib.parse import urlparse
from requests import Request, post, get


@login_required
def home(request):
    context = {}
    context['username'] = request.user.username
    context['name'] = request.user.name
    context['playlists'] = request.user.playlists.all()
    return render(request, 'giftPlaylist/home.html', context)

def login_action(request):
    if request.method == "GET":
        return render(request, 'giftPlaylist/login.html')
    scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
    params = {'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID}
    url = Request('GET', 'https://accounts.spotify.com/authorize', params=params).prepare().url
    return redirect(url)

def callback(request):
    try:
        code = request.GET['code']
    except:
        return redirect('error')

    data = {'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET}
    response = post('https://accounts.spotify.com/api/token', data=data).json()

    try:
        access_token = response.get('access_token')
    except:
        return redirect('error')
    
    try:
        username = getUserInfo(access_token, 'id')
    except:
        return redirect('error')

    try:
        user = User.objects.get(username=username)
    except:
        user = User()
        user.username = username
    try:
        user.access_token = access_token
        user.token_type = response.get('token_type')
        user.refresh_token = response.get('refresh_token')
        user.expires_in = timezone.localtime()  + timedelta(seconds=response.get('expires_in'))
        user.name = getUserInfo(access_token, 'display_name')
    except:
        return redirect('error')
    user.save()

    authenticate(username = user.username)
    login(request, user)

    return redirect('home')

def error(request):
    return render(request, 'giftPlaylist/hacked.html')

def logout_action(request):
    logout(request)
    return redirect('login')

def getUserInfo(access_token, info):
    headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + access_token}
    r = get('https://api.spotify.com/v1/me', headers=headers).json()
    return r.get(info)

def getSearchQuery(access_token, query, playlist):
    limit = 10
    params = {'q': query,
            'type': "track",
            'limit': limit,
            'market': "US",}
    headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + access_token,}
    r = get('https://api.spotify.com/v1/search', params=params, headers=headers).json()

    queries = r["tracks"]["items"]
    if len(queries) < limit: 
        limit = len(queries)
    results = []
    for i in range(limit):
        s = {}
        spotify_id = queries[i]["id"]
        s["name"] = queries[i]["name"]
        artists = [artist["name"] for artist in queries[i]["artists"]]
        s["artist"] = ', '.join([name for name in artists])
        s["spotify_id"] = spotify_id
        s["album_artwork"] = queries[i]["album"]["images"][0]["url"]
        s["duration"] = queries[i]["duration_ms"]
        d = timedelta(milliseconds = queries[i]["duration_ms"])
        s["display_duration"] = str(d)[3:7] if (str(d)[2] == "0") else str(d)[2:7]
        try:
            test = Song.objects.get(playlist_id = playlist,
                                spotify_id = spotify_id)
            s["added"] = True
        except:
            s["added"] = False
        results.append(s)
    return results

@login_required
def get_playlist_photo(request, id):
    try:
        p = Playlist.objects.get(id=id)
    except:
        return redirect('error')

    return HttpResponse(p.hidden_artwork, content_type='image/jpeg')


@login_required
def playlist(request, id):
    try:
        p = Playlist.objects.get(id=id)
    except:
        return redirect('error')
    if p.user != request.user:
        return redirect('home')

    s = p.songs.all()
    n = len(p.songs.all())
    n = f"1 song" if n == 1 else f"{n} songs"

    k = sum([song.duration for song in s], timedelta())

    context = {"playlist": p, "songs": s, "num_songs": n, "playlist_duration": k}
    return render(request, 'giftPlaylist/playlist.html', context)

@login_required
def edit_playlist(request, id):
    try:
        p = Playlist.objects.get(id = id)
    except:
        return redirect('error')

    if request.method == "GET":
        return redirect('playlist', id=id)

    if p.user != request.user:
        return redirect('playlist', id=id)

    form = PlaylistForm(request.POST, request.FILES)
    
    if not form.is_valid():
        return redirect('playlist', id=id)
    
    p.name = form.cleaned_data['name']
    p.note = form.cleaned_data['note']
    img = form.cleaned_data['hidden_artwork']
    if img != None:
        p.hidden_artwork = img
    p.save()
    return redirect('playlist', id=id)

@login_required
def create_playlist(request):
    p = Playlist()
    p.user = request.user
    p.save()
    return redirect('playlist', id=p.id)

@login_required
def delete_playlist(request, id):
    if request.method == "GET":
        return redirect('home')
    try:
        p = Playlist.objects.get(id = id)
    except:
        return redirect('error')
    try:
        if p.user != request.user:
            return redirect('home')
        p.songs.all().delete()
        p.comments.all().delete()
        p.delete()
    except:
        return redirect('home')
    return redirect('home')

@login_required
def search(request, id):
    try:
        p = Playlist.objects.get(id=id)
    except:
        return redirect('error')
    if p.user != request.user:
        return redirect('home')
    context = {"playlist": p}
    
    if request.method == "POST":
        query = request.POST.get("query")
        access_token = get_access_token(request.user)
        context["songs"] = getSearchQuery(access_token, query, p)
    
    return render(request, 'giftPlaylist/search.html', context)

@login_required
def add_song(request):
    if request.method == "GET":
        return redirect('home')
    try:
        p = Playlist.objects.get(id=request.POST.get("playlist_id"))
        s = Song()
        if (p.user != request.user):
            return redirect('home')
        s.name = request.POST.get("name")
        s.artist = request.POST.get("artist")
        s.album_artwork = request.POST.get("art")
        s.spotify_id = request.POST.get("spotify_id")
        s.playlist_id = Playlist.objects.get(id=request.POST.get("playlist_id"))
        s.duration = timedelta(milliseconds = int(request.POST.get("duration")))
    except:
        return redirect('error')
    
    s.save()
    
    return update_search(request, request.POST.get("id"), True)

@login_required
def update_search(request, id, is_added):
    response_data = {
        'song_id': id,
        'is_added': is_added,
    }

    response_json = json.dumps(response_data)
    return HttpResponse(response_json, content_type='application/json')

@login_required
def remove_song(request):
    if request.method == "GET":
        return redirect('home')
    
    try:
        p = Playlist.objects.get(id=request.POST.get("playlist_id"))
        if (p.user != request.user):
            return redirect('home')
        Song.objects.get(playlist_id = request.POST.get("playlist_id"),
                    spotify_id = request.POST.get("spotify_id")).delete()
    except:
        return redirect('error')

    return update_search(request, request.POST.get("id"), False)


@login_required
def song(request, id):
    try:
        s = Song.objects.get(id=id)
    except:
        return redirect('error')
    p = s.playlist_id
    
    if p.user != request.user:
        return redirect('home')
    
    context = {"playlist": p, "song": s}
    return render(request, 'giftPlaylist/song.html', context)

#TODO: form verification
@login_required
def edit_song(request, id):
    try:
        s = Song.objects.get(id=id)
    except:
        return redirect('error')
    if request.method == "GET":
        return redirect('song', id=id)

    p = s.playlist_id
    if request.user != p.user:
        return redirect('home')

    try:
        s.note = request.POST.get("note")
        s.save()
    except:
        return redirect('error')

    return redirect('song', id=id)

#TODO: form verification
@login_required
def delete_song(request):
    if request.method == "GET":
        return redirect('home')

    try:
        song_id = request.POST.get("song_id")
        s = Song.objects.get(id=song_id)
        p_id = request.POST.get("playlist_id")
        p = Playlist.objects.get(id=request.POST.get("playlist_id"))
        if (p.user != request.user):
            return redirect('home')
    except:
        return redirect('error')
    s.delete()

    return redirect('playlist', id=p_id)

def get_access_token(user):
    expiry = user.expires_in

    if expiry <= timezone.localtime() :
        response = post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'refresh_token',
            'refresh_token': user.refresh_token,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }).json()
        try:
            access_token = response.get('access_token')
        except:
            return redirect('error')

        user.access_token = access_token
        user.token_type = response.get('token_type')
        user.refresh_token = response.get('refresh_token')
        user.expires_in = timezone.localtime()  + timedelta(seconds=response.get('expires_in'))
    else:
        access_token = user.access_token
    return access_token

@login_required
def receiver_grid(request, uuid):
    try:
        p = Playlist.objects.get(link_id=uuid)
    except:
        return redirect('error')

    songs = []
    for s in p.songs.all().order_by('id'):
        item = {
            'id': s.id,
            'name': s.name,
            'artist': s.artist,
            'art': s.album_artwork,
            'spotify_id': s.spotify_id,
            'note': s.note,
        }
        songs.append(item)

    n = len(p.songs.all())

    context = {"playlist": p, "songs": songs, "num_songs": n, "showHome": p.user==request.user}
    return render(request, 'giftPlaylist/grid.html', context)

#TODO: form verification
@login_required
def add_comment(request):
    if request.method == 'GET':
        return redirect(reverse('home'))

    # form verification
    
    try:
        comment = Comment()
        comment.input_text = request.POST["comment_text"]
        if request.POST["comment_text"] == "": 
            redirect('receiver_grid', uuid=uuid)
        uuid = request.POST["uuid"]
        p = Playlist.objects.get(link_id=uuid)
        comment.playlist = p
        comment.name = request.POST["comment_name"]
    except:
        return redirect('receiver_grid', uuid=uuid)
    
    comment.save()

    return get_comments(request, uuid)

@login_required
def get_comments(request, uuid):
    if request.method == 'GET':
        return redirect(reverse('home'))
    try:
        p = Playlist.objects.get(link_id=uuid)
    except:
        return redirect('error')
    response_data = []
    for comment in p.comments.all().order_by('id'):
        item = {
            'id': comment.id,
            'text': comment.input_text,
            'date': str(comment.date_time),
            'name': comment.name,
        }
        response_data.append(item)

    response_json = json.dumps(response_data)
    return HttpResponse(response_json, content_type='application/json')
