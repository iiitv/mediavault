"""
This file declares classes of various models that will be stored in database
and methods to manipulate them.
"""
import os
from datetime import datetime
from operator import itemgetter

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.db.transaction import atomic
from django.dispatch import receiver
from django.utils import timezone

from . import identifier, is_media, media_type


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
    views = models.PositiveIntegerField(null=False, blank=False, default=0)
    is_root = models.BooleanField(default=False)
    seen_by = models.ManyToManyField(User, blank=True)
    time_added = models.DateTimeField(default=timezone.now)

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

    def exists(self):
        return os.path.exists(self.path)

    def media_type(self):
        return media_type(self.type.type)

    def accessible(self, user):
        return ItemAccessibility.objects.get(user=user, item=self).accessible

    def _html(self, destination):
        html = '''<a href="{0}">
            <div class="mv">
                <span class="mv-type"><i class="fa fa-{1}" aria-hidden="true"></i></span>
                <span class="mv-name">{2}</span>
                <span class="pull-right">{3} <i class="fa fa-eye aria-hidden="true"></i></span>
            </div>
        </a>'''
        link = '/{0}/{1}'.format(destination, self.id)
        media_t = media_type(self.type.type)
        if media_t == 'audio':
            fa = 'music'
        elif media_t == 'video':
            fa = 'video-camera'
        elif media_t == 'image':
            fa = 'image'
        else:
            fa = 'folder'
        return html.format(link, fa, self.name, self.views)

    def html(self):
        return self._html('media')

    def manage_html(self):
        return self._html('shared-items')


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
    time = models.DateTimeField(default=datetime.now)


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
    return SharedItem.objects.filter(is_root=True)


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
        print('Unrecognized mime {1} for - {0}... Ignoring.'.format(location,
                                                                    mime))
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
    if parent is None:
        new_item.is_root = True
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


def get_suggested_items(user):
    items = [instance.item for instance in
             ItemAccessibility.objects.filter(user=user, accessible=True) if
             instance.item.type.type != 'Directory']
    max_views = max([item.views for item in items]) if len(items) > 0 else 1
    max_views = max_views + 1 if max_views == 0 else max_views
    items_lot = [(item, item.views / max_views * 10.0) for item in items]
    seen_list = []
    unseen_list = []
    for item, score in items_lot:
        ratings = [rating_instance.rating for rating_instance in
                   ItemRating.objects.filter(item=item)]
        number_of_ratings = len(ratings)
        if number_of_ratings > 0:
            average_rating = sum(ratings) / number_of_ratings
        else:
            average_rating = 5.0
        tpl = (item, score + average_rating)
        if user in list(item.seen_by.all()):
            seen_list.append(tpl)
        else:
            unseen_list.append(tpl)
    seen_list = sorted(seen_list, key=itemgetter(1), reverse=True)
    unseen_list = sorted(unseen_list, key=itemgetter(1), reverse=True)
    if len(seen_list) >= 3:
        ret_lst = unseen_list[:7] + seen_list[:3]
    else:
        ret_lst = unseen_list[:10 - len(seen_list)] + seen_list
    return [i[0] for i in ret_lst]


def get_latest_items(user, count=10):
    items = [instance.item for instance in
             ItemAccessibility.objects.filter(
                 ~models.Q(item__type__type='Directory'), user=user,
                 accessible=True).order_by('-item__time_added')[:count]]
    return items
