from abc import ABC, abstractmethod
from typing import Callable
from threading import Lock, Timer

from misc.exceptions import EmbeddedException

EXECUTION_INTERVAL = 60


class TaskCreationException(EmbeddedException):
    def __init__(self, *args, task=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = task

class TaskAbortException(EmbeddedException):
    """"""


class Task(ABC):

    def __init__(self, execution_interval: float = EXECUTION_INTERVAL, error_callback: Callable = None):
        self._execution_interval = execution_interval
        self._execution_lock = Lock()
        self._next_execution = None
        self._next_execution_lock = Lock()
        self._started = False

        self._error_callback = error_callback

    def _schedule_next_execution(self):
        with self._next_execution_lock:
            if self._started:
                self._next_execution = Timer(self._execution_interval, self._execute)
                self._next_execution.start()

    def _abort_next_execution(self):
        with self._next_execution_lock:
            if self._next_execution:
                self._next_execution.cancel()
            self._next_execution = None
            self._started = False

    def start(self):
        if not self._started:
            self._started = True
            self._schedule_next_execution()

    def stop(self):
        self._abort_next_execution()

    def _execute(self):
        try:
            with self._next_execution_lock:
                self.execute()
        except Exception as ex:
            self._handle_exception(ex)
        else:
            self._schedule_next_execution()

    @abstractmethod
    def execute(self):
        raise NotImplementedError()

    def _handle_exception(self, ex: Exception):
        if self._error_callback:
            self._error_callback(self, ex)
        else:
            raise ex
        self.stop()