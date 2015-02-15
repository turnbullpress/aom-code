## Graphite local_settings.py
# Edit this file to customize the default Graphite webapp settings
#
# Additional customizations to Django settings can be added to this file as well

SECRET_KET = 'tqIaQJEnthL5zVRKgBYR4KkcSzks98F55LRKdZo821tC9pwvCr7Bf5edqTIcr2Gemmttr3FXTMCofzH0zdEaNHpcCstiN7zFZxuUeCxB7rHLbD7VYwlh0gGSstIgkMyvYXLHc6bnwlClioGNI0GFdaVg8xrfnD9gr7W0ESL5O9luLVrRLwpLbZKoEV93DXwMBINTqXemgupVFJnBdUhWZMFfWzRiNDr0pvCawFl5ZVC7Y8fVXy4dj7hSOGzumV9i'
TIME_ZONE = 'America/New_York'
USE_REMOTE_USER_AUTHENTICATION = True
LOG_RENDERING_PERFORMANCE = True
LOG_CACHE_PERFORMANCE = True
LOG_METRIC_ACCESS = True
GRAPHITE_ROOT = '/usr/share/graphite-web'
CONF_DIR = '/etc/graphite'
STORAGE_DIR = '/var/lib/graphite/whisper'
CONTENT_DIR = '/usr/share/graphite-web/static'
WHISPER_DIR = '/var/lib/graphite/whisper'
LOG_DIR = '/var/log/graphite'
INDEX_FILE = '/var/lib/graphite/search_index'  # Search index file

DATABASES = {
  'default': {
    'NAME': 'graphite',
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'USER': 'graphite',
    'PASSWORD': 'strongpassword',
    'HOST': '127.0.0.1',
    'PORT': ''
  }
}
