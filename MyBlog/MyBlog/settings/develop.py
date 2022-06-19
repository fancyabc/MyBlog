from pickle import TRUE
from .base import *


# 开发过程使用这个setting文件


# SECURITY WARNING: don't run with debug turned on in production!
# 本选项（DEBUG）仅在开发过程中打开


DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
# 需要（你开发的环境）已经安装了sqlite3
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}