import uuid

from pyrsistent import field
from pyrsistent import PRecord


class RecordWithUUID(PRecord):
    SERIALIZE_UUID = False
    id_ = field(type=(str, type(None)),
                initial=None,
                factory=lambda v: v if v is not None else str(uuid.uuid4()))

    def copy(self):
        return self.set("id_", str(uuid.uuid4()))

    def serialize(self, format_=None):
        result = super(RecordWithUUID, self).serialize(format_)
        if not self.SERIALIZE_UUID:
            del result["id_"]
        return result


class ViewData(PRecord):
    id_ = field()
    name = field()
    data = field()
    submit_callback = field()
    child_views = field()


class DataManager(object):
    def __init__(self, initial_data):
        self._history = [initial_data]
        self._history_index = 0
        self._record_head_in_history = True

    def get_data(self):
        return self._history[self._history_index]

    def push_data(self, new_data, record_in_history=True):
        if self._history_index != len(self._history)-1:
            self._history = self._history[:self._history_index+1]
        else:
            if not self._record_head_in_history:
                self._history.pop(-1)
        if not self._history or self._history[-1] != new_data:
            self._history.append(new_data)
        self._history_index = len(self._history)-1
        self._record_head_in_history = record_in_history

    def redo(self):
        if self._history_index < len(self._history)-1:
            self._history_index += 1

    def undo(self):
        if self._history_index > 0:
            self._history_index -= 1
