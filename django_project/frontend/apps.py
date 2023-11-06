from django.apps import AppConfig


def create_clear_uploaded_boundary_files():
    from importlib import import_module
    from django.core.exceptions import ValidationError

    try:
        IntervalSchedule = (
            import_module('django_celery_beat.models').IntervalSchedule
        )

        PeriodicTask = (
            import_module('django_celery_beat.models').PeriodicTask
        )
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=30,
            period=IntervalSchedule.DAYS
        )
    except Exception as e:
        print(e)
        return

    try:
        PeriodicTask.objects.update_or_create(
            task='clear_uploaded_boundary_files',
            defaults={
                'name': 'Clear Uploaded Boundary Files',
                'interval': schedule
            }
        )
    except ValidationError as e:
        print(e)


def create_clear_expired_map_session():
    from importlib import import_module
    from django.core.exceptions import ValidationError

    try:
        IntervalSchedule = (
            import_module('django_celery_beat.models').IntervalSchedule
        )

        PeriodicTask = (
            import_module('django_celery_beat.models').PeriodicTask
        )
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=2,
            period=IntervalSchedule.HOURS
        )
    except Exception as e:
        print(e)
        return

    try:
        PeriodicTask.objects.update_or_create(
            task='clear_expired_map_session',
            defaults={
                'name': 'clear_expired_map_session',
                'interval': schedule
            }
        )
    except ValidationError as e:
        print(e)


class FrontendConfig(AppConfig):
    name = 'frontend'

    def ready(self):
        # Create a task to clear old boundary files
        create_clear_uploaded_boundary_files()
        create_clear_expired_map_session()
