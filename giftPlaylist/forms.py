from django import forms
from giftPlaylist.models import User, Playlist
from django.contrib.auth import authenticate

MAX_UPLOAD_SIZE = 2500000

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = {'note', 'name', 'hidden_artwork',}
    def clean_picture(self):
        picture = self.cleaned_data['hidden_artwork']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture
 
