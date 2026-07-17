import os
from pathlib import Path

# SỬA LỖI TẠI ĐÂY: Vì settings.py nằm tại /app/myweb/settings.py
# .parent -> /app/myweb
# .parent.parent -> /app (Thư mục gốc chứa manage.py và db.sqlite3)
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-key-here'
DEBUG = True 

ALLOWED_HOSTS = ['anhnhatiot.cloud', 'anhnhatiot.duckdns.org', 'localhost', '127.0.0.1', '*']
CSRF_TRUSTED_ORIGINS = ['https://anhnhatiot.cloud', 'https://anhnhatiot.duckdns.org']

INSTALLED_APPS = [
    'daphne',
    'channels',         
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Các App của hệ thống
    'myweb',            # Chứa logic Garden và Dashboard chung
    'portal_main',      # Chứa trang chủ Portal
    'myweb.esp_ai',     # Chứa logic AI Vision
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myweb.urls'
ASGI_APPLICATION = 'myweb.asgi.application'

# --- CẤU HÌNH GIAO DIỆN (TEMPLATES) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),           # /app/templates
            os.path.join(BASE_DIR, 'myweb/templates'),     # /app/myweb/templates
            os.path.join(BASE_DIR, 'portal_main/templates'),# /app/portal_main/templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- CẤU HÌNH FILE TĨNH (STATIC) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),       # /app/static
    os.path.join(BASE_DIR, 'myweb/static'), # /app/myweb/static
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- CẤU HÌNH MEDIA ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- ĐIỀU HƯỚNG ĐĂNG NHẬP ---
LOGIN_URL = '/esp-ai/login/'
LOGIN_REDIRECT_URL = 'login_redirect'
LOGOUT_REDIRECT_URL = '/esp-ai/login/'

# --- CẤU HÌNH REDIS ---
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}