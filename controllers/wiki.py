# coding: utf8

'''pro práva editace přidat do skupin wiki_editor, wiki_author'''

@auth.requires_membership('pokladna')
def index():
    if not request.args:
        redirect(URL('wiki', 'index', args='index'))
    return auth.wiki()
