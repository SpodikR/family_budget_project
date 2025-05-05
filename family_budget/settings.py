from pathlib import Path

import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-qclafv+bq#01j_qs5nck*fvck+964#-(g-eij@!tup$k*g-wy4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin', # Додаток для покращення адмінки Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'budget',
    'accounts',
    'notes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'family_budget.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # --- ЗМІНЕНО ---
        # Додаємо шлях до папки templates в корені проекту
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # --- КІНЕЦЬ ЗМІН ---
        'APP_DIRS': True, # Залишаємо True, щоб Django шукав шаблони і в додатках
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'family_budget.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'uk'

TIME_ZONE = 'Europe/Kyiv'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATIC_ROOT = BASE_DIR / 'staticfiles' # Розкоментуйте та налаштуйте для production

# --- НАЛАШТУВАННЯ МЕДІА ФАЙЛІВ (завантажені користувачами) ---

# URL-префікс для доступу до медіа файлів через браузер.
# Важливо, щоб він не перетинався з STATIC_URL або URL-адресами додатків.
MEDIA_URL = '/media/'
# Абсолютний шлях до папки, де Django буде зберігати завантажені файли.
# Для розробки можна створити папку 'media' в корені проекту.
# УВАГА: Цей шлях НЕ повинен бути таким самим, як STATIC_ROOT.
# УВАГА: На production сервері ця папка має бути поза кодом проекту
#         і веб-сервер (Nginx, Apache) має бути налаштований для її роздачі.
MEDIA_ROOT = BASE_DIR / 'media' # BASE_DIR визначається на початку settings.py

# --- КІНЕЦЬ НАЛАШТУВАНЬ МЕДІА ---

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- НАЛАШТУВАННЯ АВТЕНТИФІКАЦІЇ ---

# URL, на який перенаправляти після успішного входу.
# 'budget:dashboard' - це ім'я нашого URL дашборду.
LOGIN_REDIRECT_URL = 'budget:dashboard'

# URL, на який перенаправляти після виходу.
# Можна вказати 'login' або сторінку logged_out, якщо вона є.
# Якщо хочете показувати стандартну сторінку /accounts/logged-out/,
# можна закоментувати або видалити цей рядок.
# LOGOUT_REDIRECT_URL = 'login' # Або 'budget:dashboard' чи інша
LOGOUT_REDIRECT_URL = '/accounts/login/'
# --- КІНЕЦЬ НАЛАШТУВАНЬ АВТЕНТИФІКАЦІЇ ---
# family_budget/settings.py
# ... інші налаштування ...

# --- НАЛАШТУВАННЯ JAZZMIN ---
JAZZMIN_SETTINGS = {
    # Заголовок вікна (вкладка браузера і сторінка входу)
    "site_title": "Бюджет Адмін",

    # Заголовок на сторінці входу і у верхній панелі
    "site_header": "Сімейний Бюджет",

    # Текст бренду (зазвичай короткий)
    "site_brand": "Бюджет",

    # (Опціонально) Логотип - шлях до статичного файлу
    # "site_logo": "images/logo.png", # Потрібно створити файл і запустити collectstatic

    # Текст у футері адмінки
    "copyright": "Мій Бюджетний Додаток",

    # Чи показувати UI builder для швидкої зміни теми (дуже корисно!)
    "show_ui_builder": True,

     # Іконки для додатків та моделей (використовуються класи Font Awesome 5)
    "icons": {
        "auth": "fas fa-users-cog", # Додаток Auth
        "auth.user": "fas fa-user", # Модель User
        "auth.Group": "fas fa-users", # Модель Group
        "accounts": "fas fa-user-lock", # Твій додаток Accounts
        "budget": "fas fa-wallet", # Твій додаток Budget
        "budget.category": "fas fa-tags",
        "budget.income": "fas fa-plus-circle", # Або fa-arrow-down
        "budget.expense": "fas fa-minus-circle", # Або fa-arrow-up
        "notes": "fas fa-book", # Твій додаток Notes
        "notes.note": "fas fa-sticky-note",
        "notes.notephoto": "fas fa-image",
    },
    # Іконка за замовчуванням для батьківських пунктів меню
    "default_icon_parents": "fas fa-folder",
    # Іконка за замовчуванням для дочірніх пунктів меню
    "default_icon_children": "fas fa-circle",

    # Групування моделей за назвою додатку
    "use_google_fonts_cdn": True,
    "show_sidebar": True,
    "navigation_expanded": True, # Розгортати меню за замовчуванням
}

# Налаштування, які можна змінювати через UI Builder
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True, # Трохи менший текст основного контенту
    "brand_small_text": False,
    "brand_colour": "navbar-dark", # Колір бренду (відповідає navbar)
    "accent": "accent-primary", # Колір акцентів
    "navbar": "navbar-dark", # Колірна схема навігації (dark/light)
    "no_navbar_border": False,
    "navbar_fixed": True, # Закріпити верхню панель
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True, # Закріпити бічну панель
    "sidebar": "sidebar-dark-primary", # Колірна схема бічної панелі
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default", # Базова тема (можна змінити на 'flatly', 'darkly' тощо)
    "dark_mode_theme": "darkly", # Тема для темного режиму
}
# --- КІНЕЦЬ НАЛАШТУВАНЬ JAZZMIN ---