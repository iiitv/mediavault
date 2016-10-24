from datetime import datetime
from django.contrib.auth.models import User
from django.db import models


class ItemType(models.Model):
    def __str__(self):
        return self.type

    type = models.CharField(max_length=20)


class Artist(models.Model):
    def __str__(self):
        return self.first_name + ' ' + self.last_name

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


class Album(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)


class VideoCodec(models.Model):
    def __str__(self):
        return self.codec

    codec = models.CharField(max_length=128)


class AudioCodec(models.Model):
    def __str__(self):
        return self.codec

    codec = models.CharField(max_length=128)


class SharedItem(models.Model):
    def __str__(self):
        return ''

    name = models.CharField(max_length=2014, default='')
    type = models.ForeignKey(ItemType)
    path = models.CharField(max_length=2048)
    duration = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=2048, null=True, blank=True)
    artist = models.ManyToManyField(Artist)
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


class ItemAccessibility(models.Model):
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
    def __str__(self):
        return '{0} rated {1} {2}/10'.format(self.user, self.item, self.rating)

    user = models.ForeignKey(User)
    item = models.ForeignKey(SharedItem)
    rating = models.PositiveIntegerField()
    time = models.DateTimeField(auto_now=True)


class Suggestion(models.Model):
    def __str__(self):
        return '{0} suggested {1} to {2}'.format(self.from_user, self.item,
                                                 self.to_user)

    from_user = models.ForeignKey(User, related_name='from_user')
    to_user = models.ForeignKey(User, related_name='to_user')
    item = models.ForeignKey(SharedItem)
    time = models.DateField(default=datetime.now)
