#https://docs.djangoproject.com/en/dev/topics/email/

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG
COPY_LOGS_TO_STDOUT = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': ':memory:',
        #'NAME': '/tmp/django-email-manager.sqlite',
        'NAME': 'django-email-manager.sqlite',
    }
}

INSTALLED_APPS = (
    'django_nose',
    'coverage',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',

    'email_manager',
)


EMAIL_MANAGER_USING_CELERY = False
EMAIL_MANAGER_TASK = 'email-manager-task'
CELERY_ALWAYS_EAGER = True


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
#    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)

ROOT_URLCONF = 'urls'

# Production backend
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Development backends
# Instead of sending out real e-mails the console backend just writes the
# e-mails that would be send to the standard output.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/tmp/app-messages' # change this to a proper location

#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 465 # or 587
#EMAIL_USE_TLS = True
#EMAIL_HOST_USER = 'USERNAME@gmail.com'
#EMAIL_HOST_PASSWORD = 'PASSWORD'
#EMAIL_SUBJECT_PREFIX = '[django-email-manager]'

# python -m smtpd -n -c DebuggingServer localhost:1025
#EMAIL_HOST = 'localhost'
#EMAIL_PORT = '1025'
