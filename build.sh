
#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect static files
python manage.py collectstatic --no-input

# 3. Migrate Database
python manage.py migrate

# 4. Create Superuser (Directly here!)
# This checks if 'admin' exists. If not, it creates admin/admin123
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123', is_teacher=True) if not User.objects.filter(username='admin').exists() else print('Admin already exists')" | python manage.py shell

#i have added whitenoise to settings.py for static files handling on render.com
#i have also added signup url pattern to tutti/urls.py and created signup.html template for user registration
#i have also updated login.html to include a link to the signup page for new users
#i have also updated settings.py to include STATIC_ROOT and STATICFILES_STORAGE for proper static file management
# Now the app is ready to be served