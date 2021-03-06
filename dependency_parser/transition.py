"""
Code taken from assignment: http://stp.lingfil.uu.se/~sara/kurser/parsing18/dep_parsing.html

My additions:
    -   transition()
    -   stack_to_string()
    -   other minor changes
"""

from collections import deque

SH = 0
RE = 1
RA = 2
LA = 3
transitions = ["SH", "RE", "RA", "LA"]

labels = ["det", "nsubj", "case", "nmod", "root"]
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
    Perform a transition by modifying the data structures from the arguments.
    :param trans: Transition. Either int or tuple
    :param stack: 'top' is stack[0] (reversed compared to description in paper)
    :param buffer: 'next' is buffer[0]
    :param arcs: List of tuples: (head, dependent, label)
    :return:
    """

    if trans == SH:
        # move next from the buffer to the stack
        stack.appendleft(buffer.popleft())

    elif trans == RE and stack:
        # remove top from the stack

        stack.popleft()

    elif trans[0] == RA and stack and buffer:
        # add (top, next, label) to the arc set; move next from the buffer to the stack

        label = trans[1]
        top = stack[0]
        next = buffer.popleft()

        arc = (top, next, label)

        arcs.append(arc)
        stack.appendleft(next)

    elif trans[0] == LA and stack and buffer:
        # add (next, top, label) to the arc set; remove top from the stack

        label = trans[1]
        top = stack.popleft()
        next = buffer[0]

        arc = (next, top, label)

        arcs.append(arc)
    else:
        print("Could not perform transformation.", file=sys.stdersr)


def stack_to_string(stack):
    global words
    return [words[i] for i in stack]


def parse():
    global words
    words = "root the cat is on the mat today".split()
    stack = deque([0])
    buffer = deque([x for x in range(1, len(words))])
    arcs = []
    for trans in [SH, (LA, "det"), SH, (LA, "nsubj"), SH, SH, SH, (LA, "det"),
                  (LA, "case"), (RA, "nmod"), RE, (RA, "nmod")]:
        transition(trans, stack, buffer, arcs)

    assert len(buffer) == 0, "Parse incomplete, buffer not empty."

    attach_orphans(arcs, len(words))
    print_tree(0, arcs, words, "")


if __name__ == "__main__":
    parse()
