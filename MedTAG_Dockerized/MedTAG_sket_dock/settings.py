from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@lz@il^r84q80c)r$yl-vo7ez(rdhwjnaz-98-kj6)t@h0$wvp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ALLOWED_HOSTS = ['localhost','exa.dei.unipd.it']
ALLOWED_HOSTS = ['*']


# Application definition
# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend',
#     'groundtruth_app.backends.myBackend',
# ]


# SESSION_COOKIE_AGE = 2000000
# LOGIN_URL = '/login'
# LOGIN_REDIRECT_URL = "/login"

SESSION_EXPIRES_AT_BROWSER_CLOSE = True
# SESSION_EXPIRE_SECONDS = 5
# SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True




INSTALLED_APPS = [
    'MedTAG_sket_dock_App',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 'corsheaders'

]
# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOWED_HEADERS = ('XSRF-Token','csrftoken','X-CSRFToken')
# CORS_ORIGIN_WHITELIST = (
#     'http://localhost:3000',
#
# )
# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:3000',
#
# ]
# CSRF_TRUSTED_ORIGINS = [
#     'http://localhost:3000',
# ]

MIDDLEWARE = [
    # 'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',


]

ROOT_URLCONF = 'MedTAG_sket_dock.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], #ELIMINO AL BISOGNO
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

WSGI_APPLICATION = 'MedTAG_sket_dock.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    # 'default1': {
    #             'ENGINE': 'django.db.backends.sqlite3',
    #             'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #         },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ground_truth',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'



# CSRF_COOKIE_NAME = "XSRF-TOKEN"
# CSRF_COOKIE_HTTPONLY = False
# SESSION_COOKIE_HTTPONLY = False
# CSRF_COOKIE_SECURE = False