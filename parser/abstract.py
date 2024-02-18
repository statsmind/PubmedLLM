from w3lib import html

from parser.util import replace_entities

SPECIAL_CHARS = {
    u'\u2009': ' ',
    u'\u202f': ' ',
    u'\u00a0': ' ',
    u'\u2217': '*',
}


def parse_abstract(AbstractTexts):
    """
        - 1 no AbstractText
        - 2 sigle AbstractText
        - 3 multiple AbstractTexts with Labels
        
        * remove html tags
        * repalce html entities
        * repalce special chars
    """
    if not AbstractTexts:
        abstract = '.'
    elif len(AbstractTexts) == 1:
        abstract = ''.join(AbstractTexts[0].itertext()) or '.'
    else:
        abstracts = []
        for each in AbstractTexts:
            label = each.attrib.get('Label')
            text = ''.join(each.itertext())
            if label:
                abstracts.append('{}: {}'.format(label, text))
            else:
                abstracts.append(text)
        abstract = '\n'.join(abstracts)

    # ===========
    # remove tags
    # ===========
    abstract = html.remove_tags(abstract)

    # ===============
    # repalce entities
    # ===============
    abstract = replace_entities(abstract)

    # =====================
    # replace special chars
    # =====================
    for special, replace in SPECIAL_CHARS.items():
        abstract = abstract.replace(special, replace)

    return abstract
