#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect static files
python manage.py collectstatic --no-input

# 3. Migrate Database (Fixes missing tables)
python manage.py migrate

# 4. Auto-Create Superuser (The Shell Bypass)
python create_superuser.py

#i have added whitenoise to settings.py for static files handling on render.com
#i have also added signup url pattern to tutti/urls.py and created signup.html template for user registration
#i have also updated login.html to include a link to the signup page for new users
#i have also updated settings.py to include STATIC_ROOT and STATICFILES_STORAGE for proper static file management
# Now the app is ready to be served