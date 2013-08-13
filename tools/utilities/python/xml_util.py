from sys import argv
def text_from_nodes(nodes):
    text = ""
    for n in nodes:
        for child in n.childNodes:
            if hasattr(child, "data"):
                text += child.data
    return str(text)


