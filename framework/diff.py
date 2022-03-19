def list_diff(old_list, new_list, get_key):
    """Compare two list, return a operation list for updating the old_list to
    new_list.

    This is a heuristic algorithm. Time complexity is O(n). Do not guarantee
    optimal result. The delete operation is always before insert operation.

    This algorithm is inspired by javascript list-diff. list-diff:
    https://github.com/livoras/list-diff/blob/master/lib/diff.js
    """
    moves = []
    old_length = len(old_list)
    new_length = len(new_list)
    old_key_list = [get_key(d) for d in old_list]
    new_key_list = [get_key(d) for d in new_list]
    new_i = old_i = 0
    # Remove the nodes no longer exists.
    sim_key_list = []
    while new_i < new_length and old_i < old_length:
        old_key = old_key_list[old_i]
        new_key = new_key_list[new_i]
        if old_key == new_key:
            old_i += 1
            new_i += 1
            sim_key_list.append(new_key)
        else:
            next_old_i = old_i+1
            next_new_i = new_i+1
            if old_length == new_length and next_old_i == next_new_i and (
                    next_old_i < old_length) and (
                        old_key_list[next_old_i] == new_key_list[next_new_i]):
                # In EVE Echoes' editors, a common operation is to change a
                # single element in a list. So we do a very simple test to see
                # if this happens.
                # Example:
                # old_list: [1, 2, 6, 2, 4]
                #                  ^
                #                  |
                #                old_i
                # new_list: [1, 2, 5, 2, 4]
                #                  ^
                #                  |
                #                new_i
                # The result will be:
                # [(2, -1, 6), (2, 1, 5)]
                #
                # 1. remove the element at index 2.
                # 2. insert a new element at index 2.
                moves.append((old_i, -1, old_list[old_i]))
                old_i += 1
                new_i += 1
            elif next_new_i < new_length and (
                    old_key == new_key_list[next_new_i]):
                # We simply consider there will be a new element inserted.
                old_i += 1
                new_i = next_new_i+1
                sim_key_list.append(old_key)
            else:
                # We simply consider this element been removed.
                moves.append((old_i, -1, old_list[old_i]))
                old_i += 1
    while old_i < old_length:
        moves.append((old_i, -1, old_list[old_i]))
        old_i += 1
    # Insert remain nodes.
    moves = list(reversed(moves))
    sim_length = len(sim_key_list)
    new_i = sim_i = 0
    while new_i < new_length and sim_i < sim_length:
        sim_key = sim_key_list[sim_i]
        new_key = new_key_list[new_i]
        new_item = new_list[new_i]
        if sim_key == new_key:
            sim_i += 1
            new_i += 1
        else:
            moves.append((new_i, 1, new_item))
            new_i += 1
    while new_i < new_length:
        moves.append((new_i, 1, new_list[new_i]))
        new_i += 1
    return moves
