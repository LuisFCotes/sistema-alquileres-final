

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-n4z9acd#s(n(dz*=^t+3cc00yaqd-a_q65f(zl3=x2!1uri&w&'


DEBUG = True

ALLOWED_HOSTS = ['*']



INSTALLED_APPS = [
    'jazzmin', 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
   
    'clientes.apps.ClientesConfig',
    'vehiculos.apps.VehiculosConfig',
    'alquileres.apps.AlquileresConfig',
    'seguros.apps.SegurosConfig',
    'servicios.apps.ServiciosConfig',
    'detalles_alquiler.apps.DetallesAlquilerConfig',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



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




LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True



STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



JAZZMIN_SETTINGS = {
    # Textos
    "site_title": "Alquiler de Vehículos",
    "site_header": "Alquileres",
    "site_brand": "Alquiler de Vehículos",
    "welcome_sign": "Bienvenido al sistema de alquiler de vehículos",
    "copyright": "Luis Felipe Cotes y Alana Marcela Lemus Mendoza",


    "search_model": ["clientes.Cliente", "vehiculos.Vehiculo", "alquileres.Alquiler"],


    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index", "icon": "fas fa-home"},
        {"model": "alquileres.Alquiler"},
        {"model": "clientes.Cliente"},
        {"model": "vehiculos.Vehiculo"},
    ],

    # Menú lateral
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": [
        "alquileres",
        "clientes",
        "vehiculos",
        "servicios",
        "auth",
    ],

    # Iconos (Font Awesome)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user-shield",
        "auth.Group": "fas fa-users",
        "clientes.Cliente": "fas fa-id-card",
        "vehiculos.Vehiculo": "fas fa-car-side",
        "alquileres.Alquiler": "fas fa-file-signature",
        "servicios.Servicio": "fas fa-concierge-bell",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    # Formularios: los inlines (Seguro y Servicios) se muestran en pestañas
    "changeform_format": "horizontal_tabs",
    "related_modal_active": True,

    "show_ui_builder": False,
    # Menú en la barra superior para cambiar de tema y de modo claro/oscuro en vivo
    "show_theme_chooser": True,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",              
    "default_theme_mode": "auto",  
    "accent": "accent-primary",
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_child_indent": True,
    "sidebar_nav_small_text": False,
    "navbar_small_text": False,
    "body_small_text": False,
    "actions_sticky_top": True,
}
X_FRAME_OPTIONS = 'SAMEORIGIN'



STATICFILES_DIRS = [BASE_DIR / 'static']

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'


from django.contrib.messages import constants as message_constants 
MESSAGE_TAGS = {
    message_constants.DEBUG: 'secondary',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}


SESSION_COOKIE_AGE = 60 * 60 * 8

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
