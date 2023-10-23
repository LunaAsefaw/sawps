from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from stakeholder.models import (
    UserRoleType,
    UserTitle,
    LoginStatus,
    Organisation,
    OrganisationUser,
    OrganisationRepresentative,
    OrganisationInvites,
    Reminders,
    UserProfile
)


admin.site.register(UserRoleType)
admin.site.register(UserTitle)
admin.site.register(LoginStatus)


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("name", "short_code", "province", "national")


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfile'
    list_display = (
        "picture",
    )


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(OrganisationUser)
class OrganisationUserAdmin(admin.ModelAdmin):
    list_display = ("user", "organisation")


@admin.register(OrganisationRepresentative)
class OrganisationRepresentativeAdmin(admin.ModelAdmin):
    list_display = ("user", "organisation")


@admin.register(OrganisationInvites)
class OrganisationInvitesAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "organisation",
        "user_role",
        "joined",
        "assigned_as"
    )


@admin.register(Reminders)
class RemindersAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "reminder",
        "date",
        "status",
        "type",
        "email_sent",
        "organisation"
    )
