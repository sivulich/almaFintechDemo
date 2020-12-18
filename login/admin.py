from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from login.models import Profile
from django.forms.models import ModelForm
# Register your models here.


class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        """ Should returns True if data differs from initial.
        By always returning true even unchanged inlines will get validated and saved."""
        return True


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    form = AlwaysChangedModelForm
    verbose_name_plural = 'Profile'
    max_num = 1
    min_num = 1
    fk_name = 'user'


class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)


class CustomUserAdmin(UserAdmin):
    add_form = UserCreateForm
    prepopulated_fields = {'username': ('email',)}
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'username', 'password1', 'password2',),
        }),
    )
    inlines = (ProfileInline,)


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)