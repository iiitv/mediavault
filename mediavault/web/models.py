"""
This file declares classes of various models that will be stored in database.
"""
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models


class ItemType(models.Model):
    """
    Database ORM class storing item types.
    """
    def __str__(self):
        return self.type

    type = models.CharField(max_length=20)


class Artist(models.Model):
    """
    Database ORM class for storing Artists
    """
    def __str__(self):
        return self.first_name + ' ' + self.last_name

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


class Album(models.Model):
    """
    Database ORM class for storing Albums
    """
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)


class VideoCodec(models.Model):
    """
    Database ORM class for storing Video Codecs
    """
    def __str__(self):
        return self.codec

    codec = models.CharField(max_length=128)


class AudioCodec(models.Model):
    """
    Database ORM for storing Audio Codecs
    """
    def __str__(self):
        return self.codec

    codec = models.CharField(max_length=128)


class SharedItem(models.Model):
    """
    Database ORM for storing Shared Media Items
    """
    def __str__(self):
        return '{0} - {1} | {2}'.format(self.name, self.type, self.path)

    name = models.CharField(max_length=2014, default='')
    type = models.ForeignKey(ItemType)
    path = models.CharField(max_length=2048)
    duration = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=2048, null=True, blank=True)
    artist = models.ManyToManyField(Artist, blank=True)
    album = models.ForeignKey(Album, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    video_codec = models.ForeignKey(VideoCodec, null=True, blank=True)
    video_frame_rate = models.PositiveIntegerField(null=True, blank=True)
    video_bit_rate = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    audio_codec = models.ForeignKey(AudioCodec, null=True, blank=True)
    audio_channels = models.PositiveIntegerField(null=True, blank=True)
    audio_sample_rate = models.PositiveIntegerField(null=True, blank=True)
    audio_bit_rate = models.PositiveIntegerField(null=True, blank=True)
    children = models.ManyToManyField('SharedItem', blank=True)

    def dictify(self):
        _dict = {
            "id": self.id,
            "name": self.name,
            "type": self.type.type,
            "path": self.path,
            "duration": self.duration,
            "title": self.title,
            "artist": list(self.artist.all()),
            "album": self.album,
            "year": self.year,
            "video_codec": None if not self.video_codec else self.video_codec
                .codec,
            "video_frame_rate": self.video_frame_rate,
            "video_bit_rate": self.video_bit_rate,
            "height": self.height,
            "width": self.width,
            "audio_codec": None if not self.audio_codec else self.audio_codec
                .codec,
            "audio_channels": self.audio_channels,
            "audio_sample_rate": self.audio_sample_rate,
            "audio_bit_rate": self.audio_bit_rate
        }
        return _dict


class ItemAccessibility(models.Model):
    """
    Database ORM to store the accessibility of shared items to users
    """
    def __str__(self):
        return '{0} {1} accessible to {2}'.format(
            self.item,
            '' if self.accessible else 'not',
            self.user
        )

    user = models.ForeignKey(User)
    item = models.ForeignKey(SharedItem)
    accessible = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)


class ItemRating(models.Model):
    """
    Database ORM to store rating of items
    """
    def __str__(self):
        return '{0} rated {1} {2}/10'.format(self.user, self.item, self.rating)

    user = models.ForeignKey(User)
    item = models.ForeignKey(SharedItem)
    rating = models.PositiveIntegerField()
    time = models.DateTimeField(auto_now=True)


class Suggestion(models.Model):
    """
    Database ORM to store suggestions
    """
    def __str__(self):
        return '{0} suggested {1} to {2}'.format(self.from_user, self.item,
                                                 self.to_user)

    from_user = models.ForeignKey(User, related_name='from_user')
    to_user = models.ForeignKey(User, related_name='to_user')
    item = models.ForeignKey(SharedItem)
    time = models.DateField(default=datetime.now)


def get_children(parent):
    if not parent:
        return get_root_items()
    try:
        parent = int(parent)
    except ValueError:
        return get_root_items()
    item = SharedItem.objects.filter(id=parent)
    if len(item) == 0:
        return get_root_items()
    else:
        item = item[0]
    return item.children.all()


def get_root_items():
    all_children = set()
    all_items = SharedItem.objects.all()
    for item in all_items:
        all_children = all_children.union(set(item.children.all()))
    return list(set(all_items).difference(all_children))


def filter_items(items, user):
    allowed = []
    for item in items:
        access = ItemAccessibility.objects.filter(user=user, item=item)
        if len(access) == 1:
            if access[0].accessible:
                allowed.append(item)
    return allowed
