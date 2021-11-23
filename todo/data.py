from pyrsistent import field
from pyrsistent import PRecord

from framework.data import RecordWithUUID


class TodoItemData(RecordWithUUID):
    done = field()
    content = field()
    color = field()


class TodoAppData(PRecord):
    todo_list = field()   # a list of TodoItemData
