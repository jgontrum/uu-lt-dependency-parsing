"""
Code taken from assignment: http://stp.lingfil.uu.se/~sara/kurser/parsing18/dep_parsing.html

My additions:
    -   transition()
    -   labels
    -   example
"""

from collections import deque

SH = 0
RA = 1
LA = 2

labels = ["att", "subj", "pc", "pu", "obj", "pred", "root"]
words = []


def attach_orphans(arcs, n):
    attached = []
    for (h, d, l) in arcs:
        attached.append(d)
    for i in range(1, n):
        if not i in attached:
            arcs.append((0, i, "root"))


def print_tree(root, arcs, words, indent):
    if root == 0:
        print(" ".join(words[1:]))
    children = [(root, i, l) for i in range(len(words)) for l in labels if
                (root, i, l) in arcs]
    for (h, d, l) in sorted(children):
        print(indent + l + "(" + words[h] + "_" + str(h) + ", " + words[
            d] + "_" + str(d) + ")")
        print_tree(d, arcs, words, indent + "  ")


def transition(trans, stack, buffer, arcs):
    """
    Perform an arc-standard transition by modifying the data structures
    from the arguments.

    Implements the algorithm in Küber et al. 2009, Figure 3.1.

    :param trans: Transition. Either int or tuple
    :param stack: 'top' is stack[0] (reversed compared to description in source)
    :param buffer: 'next' is buffer[0]
    :param arcs: List of tuples: (head, dependent, label)
    :return:
    """

    if trans == SH and buffer:
        # move next from the buffer to the stack
        stack.appendleft(buffer.popleft())

    elif trans[0] == RA and stack and buffer:
        # add (top, next, label) to the arc set; pop the stack
        # and replace the symbol on the buffer

        label = trans[1]
        top = stack.popleft()
        next = buffer.popleft()

        arc = (top, next, label)

        arcs.append(arc)
        buffer.appendleft(top)

    elif trans[0] == LA and stack and buffer:
        # add (next, top, label) to the arc set; remove top from the stack

        label = trans[1]
        top = stack.popleft()
        next = buffer[0]

        # Check preconditions
        if top != 0:
            # top is not the root
            arc = (next, top, label)
            arcs.append(arc)
        else:
            # Recover the stack
            stack.appendleft(top)


def parse():
    global words
    words = "root economic news had little effect on financial markets .".split()
    stack = deque([0])
    buffer = deque([x for x in range(1, len(words))])
    arcs = []

    # Example taken from Küber et al. 2009, page 24.
    for trans in [
        SH,
        (LA, "att"),
        SH,
        (LA, "subj"),
        SH,
        SH,
        (LA, "att"),
        SH,
        SH,
        SH,
        (LA, "att"),
        (RA, "pc"),
        (RA, "att"),
        (RA, "obj"),
        SH,
        (RA, "pu"),
        (RA, "pred"),
        SH
    ]:
        transition(trans, stack, buffer, arcs)

    # Check terminal condition
    assert len(buffer) == 0 and len(stack) == 1 and stack[0] == 0, \
        "Parse incomplete, buffer not empty."

    attach_orphans(arcs, len(words))
    print_tree(0, arcs, words, "")


if __name__ == "__main__":
    parse()
