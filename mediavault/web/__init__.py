import os

import magic
import re
import requests
import threading
import subprocess

INF = float('inf')

media_mimes = {
    'Directory': 'directory',
    'video/3gpp': 'video',
    'video/3gpp2': 'video',
    'audio/x-aac': 'audio',
    'video/x-flv': 'video',
    'image/gif': 'image',
    'video/h264': 'video',
    'image/jpeg': 'image',
    'video/jpeg': 'video',
    'audio/x-mpegurl': 'audio',
    'video/x-m4v': 'video',
    'audio/x-ms-wma': 'audio',
    'video/x-ms-wmv': 'video',
    'audio/mpeg': 'audio',
    'video/mpeg': 'video',
    'audio/mp4': 'audio',
    'video/mp4': 'video',
    'audio/ogg': 'audio',
    'video/ogg': 'video',
    'audio/webm': 'audio',
    'video/webm': 'video',
    'image/png': 'image',
    'image/x-png': 'image',
    'image/x-rgb': 'image',
    'image/tiff': 'image',
    'audio/x-wav': 'audio',
    'video/x-matroska': 'video',
    'application/octet-stream': 'audio',  # Risky
    'video/x-ms-asf': 'video',
    'video/x-msvideo': 'video'
}
identifier = magic.Magic(mime=True)


def is_media(mime):
    return mime in media_mimes


def media_type(mime):
    return media_mimes[mime]


def youtube_search(query):
    raw_html = requests.get(
        'https://www.youtube.com/results?search_query={0}'.format(query))
    vids = get_videos(raw_html.text)
    return [get_video_attrs(vid) for vid in vids]


def get_videos(html):
    """
    separate videos in html
    """
    first = html.find('yt-lockup-tile')
    html = html[first + 2:]
    vid = []
    while True:
        pos = html.find('yt-lockup-tile')
        if pos == -1:
            pos = INF
            vid.append(html)
            break
        vid.append(html[:pos + 2])
        html = html[pos + 3:]
    return vid


def get_video_attrs(html):
    """
    get video attributes from html
    """
    result = {}
    # get video id and description
    regex = 'yt\-lockup\-title.*?href.*?watch\?v\=(.*?[^\"]+)'
    regex += '.*? title\=\"(.*?[^\"]+)'
    temp = re.findall(regex, html)
    if len(temp) and len(temp[0]) == 2:
        result['id'] = temp[0][0]
        result['title'] = temp[0][1]
    # length
    length_regex = 'video\-time.*?\>([^\<]+)'
    temp = re.findall(length_regex, html)
    if len(temp) > 0:
        result['length'] = temp[0].strip()
    # uploader
    upl_regex = 'yt\-lockup\-byline.*?\>.*?\>([^\<]+)'
    temp = re.findall(upl_regex, html)
    if len(temp) > 0:
        result['uploader'] = temp[0].strip()
    # time ago
    time_regex = 'yt\-lockup\-meta\-info.*?\>.*?\>([^\<]+).*?([0-9\,]+)'
    temp = re.findall(time_regex, html)
    if len(temp) and len(temp[0]) == 2:
        result['time'] = temp[0][0]
        result['views'] = temp[0][1]
    # thumbnail
    if 'id' in result:
        thumb = 'http://img.youtube.com/vi/%s/0.jpg' % result['id']
        result['thumb'] = thumb
    else:
        return None
    # Description
    desc_regex = 'yt-lockup-description.*?>(.*?)<'
    temp = re.findall(desc_regex, html)
    if len(temp) > 0:
        result['description'] = temp[0]
    else:
        result['description'] = ''
    return result


def download_video(vid_id, user=None):
    if not os.path.isdir('downloads'):
        os.mkdir(os.getcwd() + '/downloads')
    thread = threading.Thread(target=download_video_real, args=[vid_id, user])
    thread.start()


def download_video_real(vid_id, user):
    command = 'cd downloads/ && youtube-dl https://www.youtube.com/watch?v=' \
              '{0}'.format(vid_id)
    subprocess.call(command, shell=True)
    from .models import add_item_recursive
    add_item_recursive(os.getcwd() + '/downloads', user, 'all', None)


def download_audio(vid_id, user=None):
    if not os.path.isdir('downloads'):
        os.mkdir(os.getcwd() + '/downloads')
    thread = threading.Thread(target=download_audio_real, args=[vid_id, user])
    thread.start()
    from .models import add_item_recursive
    add_item_recursive(os.getcwd() + '/downloads', user, 'all', None)


def download_audio_real(vid_id, user):
    command = 'cd downloads/ && youtube-dl --extract-audio https://www.youtu' \
              'be.com/watch?v={0}'.format(vid_id)
    subprocess.call(command, shell=True)
    from .models import add_item_recursive
    add_item_recursive(os.getcwd() + '/downloads', user, 'all', None)
