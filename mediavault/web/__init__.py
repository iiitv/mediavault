import magic

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
    'application/octet-stream': 'audio'  # Risky
}
identifier = magic.Magic(mime=True)


def is_media(mime):
    return mime in media_mimes


def media_type(mime):
    return media_mimes[mime]
