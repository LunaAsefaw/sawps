from typing import Union, List

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.template.loader import render_to_string
from django.utils import timezone

from stakeholder.models import (
    OrganisationUser,
    Reminders,
    UserProfile
)


@shared_task
def send_reminder_email(*args):
    reminder = None
    recipient_email = None
    user = None

    if len(args) > 0:
        reminder = args[0]
        try:
            reminder_details = Reminders.objects.get(pk=reminder)
            user = User.objects.get(pk=reminder_details.user.pk)
            recipient_email = user.email
            if len(args) > 1:
                recipient_email = args[1]
        except Exception:
            reminder_details = None

    message = render_to_string(
        'emails/reminder_email.html',
        {
            'domain': Site.objects.get_current().domain,
            'name': user.username,
            'reminder': reminder_details.reminder,
            'date': reminder_details.date,
            'organisation': reminder_details.organisation
        },
    )
    subject = "Reminder: " + reminder_details.title
    send_mail(
        subject,
        None,
        settings.SERVER_EMAIL,
        [recipient_email],
        html_message=message
    )


@shared_task
def send_reminder_emails(*args):
    """check any reminders that need to be sent,
    update reminder status and user notifications"""
    current_datetime = timezone.now()
    due_reminders = Reminders.objects.filter(
        status=Reminders.ACTIVE,
        email_sent=False,
        date__lte=current_datetime
    )

    for reminder in due_reminders:
        if reminder.type == Reminders.PERSONAL:
            send_reminder_email(reminder.id)
            update_user_profile(reminder.user)
        else:
            org_users_list = OrganisationUser.objects.filter(
                organisation=reminder.organisation
            )
            for org_user in org_users_list:
                send_reminder_email(reminder.id, org_user.user.email)
                update_user_profile(org_user.user)
        reminder.status = Reminders.PASSED
        reminder.email_sent = True
        reminder.save()


def update_user_profile(user):
    user_profiles = UserProfile.objects.filter(user=user)
    if user_profiles.exists():
        user_profile = user_profiles.first()
        user_profile.received_notif = False
        user_profile.save()


@shared_task
def update_property_short_code(organisation_id):
    from property.models import Property
    from property.utils import batch_short_code_update

    prov_orgs: Union[QuerySet, List[dict]] = Property.objects.filter(
        organisation_id=organisation_id
    ).values('province', 'organisation').distinct()
    for prov_org in prov_orgs:
        batch_short_code_update(prov_org['province'], prov_org['organisation'])
