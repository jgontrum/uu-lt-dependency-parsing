"""
Code taken from assignment: http://stp.lingfil.uu.se/~sara/kurser/parsing18/dep_parsing.html

My additions:
    -   oracle()
    -   import functions from transition.py
"""

import sys
from collections import deque

SH = 0
RE = 1
RA = 2
LA = 3
transitions = ["SH", "RE", "RA", "LA"]
words = []

labels = ["nsubj", "csubj", "nsubjpass", "csubjpass", "dobj", "iobj", "ccomp",
          "xcomp", "nmod", "advcl", "advmod", "neg", "aux", "auxpass", "cop",
          "mark", "discourse", "vocative", "expl", "nummod", "acl", "amod",
          "appos", "det", "case", "compound", "mwe", "goeswith", "name",
          "foreign", "conj", "cc", "punct", "list", "parataxis", "remnant",
          "dislocated", "reparandum", "root", "dep", "nmod:npmod", "nmod:tmod",
          "nmod:poss", "acl:relcl", "cc:preconj", "compound:prt"]


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


def read_sentences():
    sentence = []
    sentences = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            sentences.append(sentence)
            sentence = []
        elif line[0] != "#":
            token = line.split("\t")
            sentence.append(token)
    return (sentences)


def print_tab(arcs, words, tags):
    hs = {}
    ls = {}
    for (h, d, l) in arcs:
        hs[d] = h
        ls[d] = l
    for i in range(1, len(words)):
        print("\t".join([words[i], tags[i], str(hs[i]), ls[i]]))
    print()


def oracle(stack, buffer, heads, labels):
    """
    Predicts the next transition based on gold annotations.
    Algorithm can be found at Goldberg and Nivre, CoLING 2012, Algorithm 1.
    :param stack: stack[0] == top
    :param buffer: buffer[0] == next
    :param heads: head for a given word
    :param labels: label for a transition to a given word
    :return:
    """

    top = stack[0]
    next = buffer[0]

    # Check for left arc
    if heads[top] == next:
        return LA, labels[top]

    # Check for right arc
    if heads[next] == top:
        return RA, labels[next]

    # Check for reduce
    for k in range(0, top):
        if heads[k] == next or heads[next] == k:
            return RE

    # Else
    return SH


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

        # Get the last word from the stack
        top = stack[0]

        # Search for an arc with top as dependent
        valid_arc = list(filter(lambda arc: arc[1] == top, arcs))

        # Precondition matched: Arc found that is leading tso w_i
        if valid_arc:
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

        # Check preconditions
        arc_to_top = list(filter(lambda arc: arc[1] == top, arcs))
        if top != 0 and not arc_to_top:
            # top is not the root and there are no arcs with top as dependent
            arc = (next, top, label)
            arcs.append(arc)
        else:
            # Recover the stack
            stack.appendleft(top)


def parse(sentence):
    global words
    sentence.insert(0, ("root", "_", "0", "_"))
    words = [sentence[i][0] for i in range(len(sentence))]
    tags = [sentence[i][1] for i in range(len(sentence))]
    heads = [int(sentence[i][2]) for i in range(len(sentence))]
    labels = [sentence[i][3] for i in range(len(sentence))]
    stack = deque([0])
    buffer = deque([x for x in range(1, len(words))])
    arcs = []
    while buffer:
        trans = oracle(stack, buffer, heads, labels)
        transition(trans, stack, buffer, arcs)
    attach_orphans(arcs, len(words))
    if tab_format:
        print_tab(arcs, words, tags)
    else:
        print_tree(0, arcs, words, "")


if __name__ == "__main__":
    tab_format = False
    if len(sys.argv) == 2 and sys.argv[1] == "tab":
        tab_format = True
    for sentence in read_sentences():
        parse(sentence)
