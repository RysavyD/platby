# coding: utf8

# výhledově asi vše předělat na grid (view=grid.html),
# kdežto původně jsem předával rows (view=pohyby.html)

from mz_wkasa_platby import Uc_sa, zpatky, aliases

@auth.requires_membership('admin')
def vsechny():
    response.view = 'podvojne/grid.html'
    return dict(grid=_grid(db.pohyb))

@auth.requires_membership('admin')
def castka():
    if request.args:
        form = None
    else:
        form = SQLFORM.factory(Field('castka', 'integer', label='Částka', requires=IS_NOT_EMPTY()),
                            Field('vice', 'boolean', label='nebo více'))
    if form and form.process().accepted:
        session.castka_castka = form.vars.castka
        session.castka_vice = form.vars.vice
    if session.castka_vice:
            return dict(form=form, grid=_grid(db.pohyb.castka>=session.castka_castka))
    elif session.castka_castka:
            return dict(form=form, grid=_grid(db.pohyb.castka==session.castka_castka))
    return dict(form=form, grid=None)

'''
@auth.requires_membership('admin')
def vse():
    response.view = 'podvojne/pohyby.html'
    cnt_args = len(request.args)
    if cnt_args<2:
        query = None
    else:
        if request.args[0]=='0':
            md = db.pohyb.idma_dati==None
        else:
            md = db.pohyb.idma_dati==request.args[0]
        if request.args[1]=='0':
            dal = db.pohyb.iddal==None
        else:
            dal = db.pohyb.iddal==request.args[1]
        query = ((md)&(dal))
        if cnt_args>=4:
            od = request.args[2]
            pred = request.args[3]
            query &= ((db.pohyb.datum>=datetime.date(
                        int(od[:4]), int(od[4:6]), int(od[6:])))&
                    (db.pohyb.datum<datetime.date(
                        int(pred[:4]), int(pred[4:6]), int(pred[6:]))))
    return _podvojne(query)
'''

@auth.requires_membership('admin')
def nedavne():
    response.view = 'podvojne/pohyby.html'
    return _podvojne(db.pohyb.datum>=zpatky(60))

@auth.requires_membership('admin')
def zal_plus():
    response.view = 'podvojne/pohyby.html'
    return _podvojne(db.pohyb.iddal==Uc_sa.oz)

@auth.requires_membership('admin')
def fungujeme():
    response.view = 'podvojne/pohyby.html'
    return _podvojne(db.pohyb.iddal==Uc_sa.oz_fu)

@auth.requires_membership('admin')
def bu():
    response.view = 'podvojne/pohyby.html'
    return _podvojne((db.pohyb.iddal==Uc_sa.bezny)|
              (db.pohyb.idma_dati==Uc_sa.bezny))

@auth.requires_membership('admin')
def pokladna():
    response.view = 'podvojne/pohyby.html'
    return _podvojne((db.pohyb.iddal==Uc_sa.pokladna)|
              (db.pohyb.idma_dati==Uc_sa.pokladna))

@auth.requires_membership('admin')
def chybi():
    response.flash = "chybějící podvojný účet je nutno doplnit před daňovým přiznáním"
    response.view = 'podvojne/pohyby.html'
    return _podvojne((db.pohyb.iddal==None)|
              (db.pohyb.idma_dati==None))

@auth.requires_membership('admin')
def ucet():
    if len(request.args)==1:
        ucet = db.ucet[request.args[0]]
        if ucet:
            response.view = 'podvojne/pohyby.html'
            return _podvojne((db.pohyb.idma_dati==request.args[0])|
                (db.pohyb.iddal==request.args[0]),
                hdr = '%s : %s (%s)' % (ucet.ucet, ucet.nazev, ucet.zkratka),
                lnk = A('přehled účtů', _href=URL('zaverky', 'osnova')),
                fp = True)
    session.flash = "nesprávně zadaný účet (id)"
    redirect(URL('zaverky', 'osnova'))


def _podvojne(query, fp=False, hdr=None, lnk=None):
    left, md, dal, org, dalsi_pole = _get_query_parts(db, fp)
    pohyby = db(query).select(
          db.pohyb.ALL,
          db.auth_user.nick,
          org.nick,
          md.zkratka, dal.zkratka,
          *dalsi_pole,
          left=left,
          orderby=~db.pohyb.datum)
    if fp:
        for pohyb in pohyby:
            if pohyb.partner.nazev:
                pohyb.pohyb.popis = pohyb.partner.nazev + ((', '+pohyb.pohyb.popis) if pohyb.pohyb.popis else '')
    return dict(hdr=hdr, lnk=lnk, pohyby=pohyby)

def _get_query_parts(db, fp=False):
    md, dal, org = aliases(db)
    if fp:
        left = (db.auth_user.on(db.auth_user.id==db.pohyb.idauth_user),
              org.on(org.id==db.pohyb.idorganizator),
              md.on(md.id==db.pohyb.idma_dati),
              dal.on(dal.id==db.pohyb.iddal),
              db.fp.on(db.fp.id==db.pohyb.fp_id),
              db.partner.on(db.partner.id==db.fp.partner_id))
        dalsi_pole = (db.partner.nazev,)
    else:
        left = (db.auth_user.on(db.auth_user.id==db.pohyb.idauth_user),
              org.on(org.id==db.pohyb.idorganizator),
              md.on(md.id==db.pohyb.idma_dati),
              dal.on(dal.id==db.pohyb.iddal))
        dalsi_pole = ()
    return left, md, dal, org, dalsi_pole

def _grid(query):
    left, md, dal, org, dalsi_pole = _get_query_parts(db, fp=True)
    if auth.has_membership('pokladna'):
        fields=(db.pohyb.datum, db.pohyb.castka,
          md.ucet, dal.ucet,
          db.auth_user.nick, org.nick, db.partner.nazev, db.pohyb.popis,
          )
    else:
        fields=(db.pohyb.datum, db.pohyb.castka,
          md.zkratka, dal.zkratka,
          db.auth_user.nick, org.nick, db.partner.nazev, db.pohyb.popis,
          ),
    grid = SQLFORM.grid(
        query,
        left=left,
        fields=fields,
        headers={'auth_user.nick': "Zákazník", 'org.nick': "Org", 'partner.nazev': "Partner",
            'md.ucet': "MD", 'dal.ucet': "Dal", 'md.zkratka': "MD", 'dal.zkratka': "Dal"},
        deletable=auth.has_membership('pokladna'),
        editable=auth.has_membership('pokladna'),
        create=auth.has_membership('pokladna'),
        csv=auth.has_membership('pokladna'),
        showbuttontext=False,
        maxtextlengths={'auth_user.email' : 30},
        paginate=100,
        searchable=False,
        orderby=~db.pohyb.datum,
        )
    return grid
