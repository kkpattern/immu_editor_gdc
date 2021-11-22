def list_diff(old_list, new_list, get_key):
    """比较两个列表, 得到一个操作列表可以将old_list变成new_list. 得到的操作列表
    一定是移除操作在前面, 插入操作在后面.

    此算法时间复杂度为O(n), 但不能保证为最佳结果. 此算法是为diff based UI
    rendering设计的, 通常情况下根据用户的输入old_list和new_list的diff是逐个少量
    改变的. 对于old_list, new_list发生大量变化从而导致大量moves的情况, 建议考虑
    直接移除old_list并创建new_list(这里实际指old_list和new_list对应的UI元素).

    此算法受到了javascript list-diff的启发. list-diff:
    https://github.com/livoras/list-diff/blob/master/lib/diff.js
    """
    moves = []
    old_length = len(old_list)
    new_length = len(new_list)
    old_key_list = [get_key(d) for d in old_list]
    new_key_list = [get_key(d) for d in new_list]
    new_i = old_i = 0
    # 先移除所有需要移除的.
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
                # 在实际使用场景中, 一个非常常见的变更是list中的某个元素发生了
                # 变更, 当满足这个if条件时我们就认为是发生了这种情况, 处理方式
                # 为移除当前old data, 同时跳过匹配当前new data. 后续的插入流程
                # 里会添加对应的新增操作的.
                # 举例:
                # old_list: [1, 2, 6, 2, 4]
                #                  ^
                #                  |
                #                old_i
                # new_list: [1, 2, 5, 2, 4]
                #                  ^
                #                  |
                #                new_i
                # 最后生成的moves为:
                # [(2, -1, 6), (2, 1, 5)]
                # 针对这种情况做特殊处理的好处是列表的变更更稳定, 例如在UI界面
                # 上, 对于一个list容器做此操作, 只有发生变更的item会增删, 其他
                # item都不会有任何变更.
                moves.append((old_i, -1, old_list[old_i]))
                old_i += 1
                new_i += 1
            elif next_new_i < new_length and (
                    old_key == new_key_list[next_new_i]):
                # case 1: 如果old_key和new_item的下一个是一样的, 那么推测
                # 是这里会insert一个进来. 直接跳过留给第二个insert pass处理
                old_i += 1
                new_i = next_new_i+1
                sim_key_list.append(old_key)
            else:
                # 简单的认为这个元素就是移除了.
                moves.append((old_i, -1, old_list[old_i]))
                old_i += 1
    while old_i < old_length:
        moves.append((old_i, -1, old_list[old_i]))
        old_i += 1
    # 然后根据需要依次插入剩下的.
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
