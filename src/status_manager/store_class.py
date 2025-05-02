import threading


class TaskStatuses:
    _instance = None 
    _lock = threading.Lock() 
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:  
                if cls._instance is None:  
                    cls._instance = super(TaskStatuses, cls).__new__(cls)
                    cls._instance._status_dict = {}  
                    cls._instance._lock = threading.Lock()  
        return cls._instance

    def _update_task_status(self, task_id: str, status: str):
        with self._lock:
            self._status_dict[task_id] = status

    def get_status(self, task_id: str) -> str:
        with self._lock:
            return self._status_dict.get(task_id, 'not found')
    
    def set_status_pending(self, task_id: str):
        self._update_task_status(task_id, 'pending')

    def set_status_running(self, task_id: str):
        self._update_task_status(task_id, 'running')

    def set_status_finished(self, task_id: str):
        self._update_task_status(task_id, 'finished')

    def set_status_failed(self, task_id: str):
        self._update_task_status(task_id, 'failed')
