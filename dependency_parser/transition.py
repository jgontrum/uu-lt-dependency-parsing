"""
Code taken from assignment: http://stp.lingfil.uu.se/~sara/kurser/parsing18/dep_parsing.html

My additions:
    -   transition()
    -   stack_to_string()
    -   other minor changes
"""

from collections import deque
from sys import stderr

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
    global words

    print(
        f"STACK: {stack_to_string(stack)} ||| BUFFER: {stack_to_string(buffer)}",
        file=stderr)

    if trans == SH:
        # move next from the buffer to the stack

        print(f"SHIFT: BUFFER[{words[buffer[0]]}] -> STACK", file=stderr)
        stack.appendleft(buffer.popleft())

    elif trans == RE and stack:
        # remove top from the stack

        # Get the last word from the stack
        top = stack[0]

        # Search for an arc with top as dependent
        valid_arc = list(filter(lambda arc: arc[1] == top, arcs))

        # Precondition matched: Arc found that is leading tso w_i
        if valid_arc:
            print(f"REDUCE: {words[top]} removed from STACK", file=stderr)
            stack.popleft()

    elif trans[0] == RA and stack and buffer:
        # add (top, next, label) to the arc set; move next from the buffer to the stack

        label = trans[1]
        top = stack[0]
        next = buffer.popleft()

        arc = (top, next, label)

        print(f"RA: ({words[top]}, {words[next]}, {label})", file=stderr)

        arcs.append(arc)
        stack.appendleft(next)

    elif trans[0] == LA:
        # add (next, top, label) to the arc set; remove top from the stack

        label = trans[1]
        top = stack.popleft()
        next = buffer[0]

        # Check preconditions
        arc_to_top = list(filter(lambda arc: arc[1] == top, arcs))
        if top != 0 and not arc_to_top:
            # top is not the root and there are no arcs with top as dependent
            arc = (next, top, label)
            arcs.append(arc)
            print(f"LA: ({words[top]}, {words[next]}, {label})", file=stderr)


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
