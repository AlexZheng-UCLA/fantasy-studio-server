from celery import Celery
from worker import _full_process


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        # include=['CELERY_IMPORTS']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
celery = Celery()


@celery.task(name='full_process_task')
def full_process_task(metadata):
    return _full_process(metadata)


