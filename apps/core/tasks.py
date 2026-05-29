from config.celery import app


@app.task
def placeholder():
    """Placeholder — core has no async tasks of its own."""
