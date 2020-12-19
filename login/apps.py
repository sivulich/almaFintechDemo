from django.apps import AppConfig


class LoginConfig(AppConfig):
    name = 'login'

    def ready(self):
        try:
            # Modules must be imported during ready
            from django.contrib.auth.models import User
            from login.models import Profile
            # Create default user
            # Default admin username and password should be moved to .env, for demonstration purposes this is left here
            if not User.objects.filter(username='admin').exists():
                admin = User.objects.create(username='admin', is_staff=True, is_superuser=True)
                admin.set_password('admin')
                admin.save()
            if not Profile.objects.filter(user__username='admin').exists():
                Profile.objects.create(user=User.objects.get(username='admin'))

        # Catch exception on first migration and when migrating
        except Exception as e:
            return
