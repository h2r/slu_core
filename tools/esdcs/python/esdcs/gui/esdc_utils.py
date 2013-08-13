def highlightTextLabel(label, esdc):
    """Change the label text to highlight a single esdc"""
    start, end = esdc.range
    labelText = (esdc.entireText[0:start]+ 
                 "<b>" + esdc.entireText[start:end] + "</b>" +
                 esdc.entireText[end:])
    label.setText(labelText)

def highlightTextLabelESDCs(label, esdcs):
    """Change the label text to highlight a list of esdcs"""
    offset = 0
    labelText = ''
    text = esdcs[0].entireText
    esdcs.sort(key=lambda esdc: esdc.range[0])
    for esdc in esdcs:
        start, end = esdc.range
        labelText += (text[offset:start]
                      + "<b>"
                      + text[start:end]
                      + "</b>")
        offset = end
    labelText += text[offset:]
    label.setText(labelText)
