from contextlib import contextmanager


@contextmanager
def disconnected_signal(signal, receiver, sender):
    """
    Temporarily disconnect a signal.
    """
    signal.disconnect(receiver, sender=sender)
    try:
        yield
    finally:
        signal.connect(receiver, sender=sender)
