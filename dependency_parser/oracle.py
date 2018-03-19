"""
Code taken from assignment: http://stp.lingfil.uu.se/~sara/kurser/parsing18/dep_parsing.html

My additions:
    -   oracle()
    -   import functions from transition.py
"""

import sys
from collections import deque

from dependency_parser.transition import transition, SH, LA, RA, RE, \
    print_tree, attach_orphans

words = []

labels = ["nsubj", "csubj", "nsubjpass", "csubjpass", "dobj", "iobj", "ccomp",
          "xcomp", "nmod", "advcl", "advmod", "neg", "aux", "auxpass", "cop",
          "mark", "discourse", "vocative", "expl", "nummod", "acl", "amod",
          "appos", "det", "case", "compound", "mwe", "goeswith", "name",
          "foreign", "conj", "cc", "punct", "list", "parataxis", "remnant",
          "dislocated", "reparandum", "root", "dep", "nmod:npmod", "nmod:tmod",
          "nmod:poss", "acl:relcl", "cc:preconj", "compound:prt"]


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
