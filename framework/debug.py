from framework.data import ViewData

from pyrsistent import pvector


def generate_view_data(root_view, origin_data):
    current_data = root_view.get_current_data()
    if origin_data is None or id(root_view) != origin_data.id_:
        origin_data = ViewData(id_=id(root_view),
                               name=root_view.__class__.__name__,
                               data=current_data,
                               submit_callback=root_view._submit_data_callback,
                               child_views=pvector())
    if current_data is not origin_data.data:
        origin_data = origin_data.set("data", current_data)
    origin_child_view_data = origin_data.child_views
    origin_child_view_count = len(origin_child_view_data)
    new_child_view_data = []
    for i, child_view in enumerate(root_view.iter_child_view()):
        if i < origin_child_view_count:
            new_child_view_data.append(generate_view_data(
                child_view, origin_child_view_data[i]))
        else:
            new_child_view_data.append(generate_view_data(child_view, None))
    new_child_view_count = len(new_child_view_data)
    if origin_child_view_count != new_child_view_count or not all(
        [new_child_view_data[i] is origin_child_view_data[i] for i in range(
            new_child_view_count)]):
        origin_data = origin_data.set("child_views",
                                      pvector(new_child_view_data))
    return origin_data
