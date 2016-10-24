from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.SharedItem)
admin.site.register(models.Album)
admin.site.register(models.Artist)
admin.site.register(models.AudioCodec)
admin.site.register(models.ItemAccessibility)
admin.site.register(models.ItemRating)
admin.site.register(models.ItemType)
admin.site.register(models.Suggestion)
admin.site.register(models.VideoCodec)
