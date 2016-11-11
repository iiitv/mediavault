"""
This file declares classes of various models that will be stored in database.
"""
import os
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.db.transaction import atomic
from django.dispatch import receiver

from . import identifier, is_media


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
        return '{2}. {0} - {1}'.format(self.name, self.type, self.id)

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


def get_children(parent, user):
    if not parent:
        return get_root_items(user)
    try:
        parent = int(parent)
    except ValueError:
        return get_root_items(user)
    item = SharedItem.objects.filter(id=parent)
    if len(item) == 0:
        return get_root_items(user)
    else:
        item = item[0]
    return item.children.all()


def get_root_items(user):
    all_children = set()
    all_items = SharedItem.objects.all()
    for item in all_items:
        all_children = all_children.union(set(item.children.all()))
    return filter_items(set(all_items).difference(all_children), user)


def filter_items(items, user):
    allowed = []
    for item in items:
        access = ItemAccessibility.objects.filter(user=user, item=item)
        if len(access) == 1:
            if access[0].accessible:
                allowed.append(item)
    return allowed


def get_children_recursive(parent, user):
    if not parent:
        return get_root_items_recursive(user)
    try:
        parent = int(parent)
    except ValueError:
        return get_root_items_recursive(user)
    item = SharedItem.objects.filter(id=parent)
    if len(item) == 0:
        return get_root_items_recursive(user)
    item = item[0]
    parent_dict = item.dictify()
    children = item.children.all()
    children = filter_items(children, user)
    child_list = [get_children_recursive(child.id, user) for child in children]
    parent_dict['children'] = child_list
    return parent_dict


def get_root_items_recursive(user):
    root_items = get_root_items(user)
    tree = [get_children_recursive(item.id, user) for item in root_items]
    return tree


def get_suggested_items(user):  # TODO : Implement it
    pass


def add_item_recursive(location, user, permission, parent=None):
    print('Adding Item - {0} {1} {2} {3}'.format(location, user, permission,
                                                 parent))
    if not os.path.isdir(location):
        return add_item(location, user, permission, parent)
    else:
        items = os.listdir(location)
        number = add_item(location, user, permission, parent, directory=True)
        curr_dir = SharedItem.objects.get(path=location)
        for item in items:
            number += add_item_recursive(location + '/' + item, user,
                                         permission, curr_dir)
        return number


def remove_item_recursive(item):
    for child in item.children.all():
        remove_item_recursive(child)
    print("Deleting item - {0}".format(item))
    item.delete()


def add_item(location, user, permission, parent, directory=False):
    if len(SharedItem.objects.filter(path=location)) > 0:
        print("Already exists")
        return 0
    if directory:
        mime = 'Directory'
    else:
        mime = identifier.from_file(location)
    if not is_media(mime):
        return 0
    if location[-1] == '/':
        location = location[:-1]
    name = location.split('/')[-1]
    type = ItemType.objects.filter(type=mime)
    if len(type) == 0:
        type = ItemType(type=mime)
        type.save()
    else:
        type = type[0]
    new_item = SharedItem(name=name, type=type,
                          path=location)  # TODO : Get more details
    new_item.save()
    if parent:
        parent.children.add(new_item)
        parent.save()
    if permission == 'all':
        grant_permission(new_item, None, admin_only=False)
    elif permission == 'admin':
        grant_permission(new_item, None, admin_only=True)
    elif permission == 'self':
        grant_permission(new_item, user, admin_only=False)
    return 1


def grant_permission(item, user, admin_only):
    print("Permission Grant - {0} -- {1} -- {2}".format(item, user, admin_only))
    if admin_only:
        users = User.objects.filter(is_superuser=True)
        with atomic():
            for _user in users:
                print("Granting Access of {0} to {1}".format(item, _user))
                accessibility_instance = ItemAccessibility.objects.get(
                    user=_user, item=item)
                accessibility_instance.accessible = True
                accessibility_instance.save()
    elif user:
        print("Granting Access of {0} to {1}".format(item, user))
        accessibility_instance = ItemAccessibility.objects.get(user=user,
                                                               item=item)
        accessibility_instance.accessible = True
        accessibility_instance.save()
    else:
        users = User.objects.all()
        with atomic():
            for _user in users:
                print("Granting Access of {0} to {1}".format(item, _user))
                accessibility_instance = ItemAccessibility.objects.get(
                    user=_user, item=item)
                accessibility_instance.accessible = True
                accessibility_instance.save()


@receiver(post_save, sender=SharedItem)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        permissions = []
        for user in User.objects.all():
            permissions.append(ItemAccessibility(user=user, item=instance,
                                                 accessible=False))
        ItemAccessibility.objects.bulk_create(permissions)


def grant_permission_recursive(item, user, admin_only):
    for child in item.children.all():
        grant_permission_recursive(child, user, admin_only)
    grant_permission(item, user, admin_only)


def remove_permission_recursive(item, user):
    for child in item.children.all():
        remove_permission_recursive(child, user)
    remove_permission(item, user)


def remove_permission(item, user):
    instance = ItemAccessibility.objects.get(user=user, item=item)
    instance.accessible = False
    instance.save()
