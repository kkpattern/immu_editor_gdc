from pyrsistent import field
from pyrsistent import PRecord


class Vector2(PRecord):
    x = field(initial=0)
    y = field(initial=0)


class GameObjectDataBase(PRecord):
    id_ = field(initial=0)
    pos = field(initial=Vector2(x=0, y=0))  # Vector2
    is_selected = field(initial=False)


class TreeData(GameObjectDataBase):
    type_ = "Tree"


class HouseData(GameObjectDataBase):
    type_ = "House"


class MountainData(GameObjectDataBase):
    type_ = "Mountain"


class LevelData(PRecord):
    objects = field()   # a [id: object] map
