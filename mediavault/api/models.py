from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from web.models import SharedItem, ItemAccessibility


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        items = SharedItem.objects.all()
        instances = []
        for item in items:
            instances.append(
                ItemAccessibility(user=instance, item=item, accessible=False)
            )
        ItemAccessibility.objects.bulk_create(instances)
