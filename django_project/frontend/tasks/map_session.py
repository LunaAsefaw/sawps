from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task(name="clear_expired_map_session")
def clear_expired_map_session():
    """
    Clear expired map session.

    This job will be run every 2 hours.
    """
    from frontend.utils.map import delete_expired_map_materialized_view
    total = delete_expired_map_materialized_view()
    logger.info(f'System cleared {total} expired sessions')
