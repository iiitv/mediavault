import json

from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from web.models import get_children


def explore(request):
    """
    Return files and folders contained in a location
    :param request: The request object
    :return: JSON response
    """
    key = request.GET.get('key', None)
    if not key:
        return HttpResponse(json.dumps({"error": "No key provided"}), 401)
    user = Token.objects.filter(key=key)
    if len(user) == 0:
        return HttpResponse(json.dumps({"error": "Invalid key"}), 401)
    user = user[0].user
    parent = request.GET.get('parent', None)
    children = get_children(parent, user)
    children_dict = []
    for child in children:
        children_dict.append(child.dictify())
    return_dict = {
        "parent": parent,
        "number": len(children_dict),
        "children": children_dict
    }
    return HttpResponse(json.dumps(return_dict))
