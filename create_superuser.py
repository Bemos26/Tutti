import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tutti.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser: {username}")
        # Note: We set is_teacher=True so the admin can access teacher features
        User.objects.create_superuser(username=username, email=email, password=password, is_teacher=True)
        print("Superuser created successfully!")
    else:
        print("Superuser already exists. Skipping.")

if __name__ == "__main__":
    create_admin()