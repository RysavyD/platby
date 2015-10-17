# coding: utf8

from datetime import datetime, timedelta, time, date
from mz_wkasa_platby import Uc_sa

def clenove():
    return _clenove('clen sdruzeni', True)

def hlorg():
    return _clenove('hlavni organizator', False)

def rada():
    return _clenove('rada', False)

def dk():
    return _clenove('dk', False)

def _clenove(skupina, hlavni):
    response.view = 'prehledy/clenove.html'
    clen_id = _getgrpid(skupina)
    clenove = db(db.clenstvi.group_id==clen_id).select(
          db.clenstvi.ALL, db.auth_user.nick,
          left=db.auth_user.on(db.auth_user.id==db.clenstvi.user_id),
          orderby=db.auth_user.nick.lower())
    return dict(clenove=clenove, hlavni=hlavni)

def add_hl_org():
    _add_x('hlorg', 'hlavní organizátor', "už je hlavním organizátorem", "přidán do seznamu hlavních organizátorů")

def add_rada():
    _add_x('rada', 'rada', "už je v radě", "přidán do rady")

def add_dk():
    _add_x('dk', 'dk', "už je v DK", "přidán do DK")

def _add_x(kam_potom, skupina, msg_uz_je, msg_pridan):
    grp_id = _getgrpid(skupina)
    if len(request.args)==1:
        clenstvi = db((db.clenstvi.user_id==request.args[0]) & (db.clenstvi.group_id==grp_id)).select().first()
        if clenstvi:
            if clenstvi.do_dne:
                clenstvi.update_record(do_dne=None)
                session.flash = msg_pridan
            else:
                session.flash = msg_uz_je
        else:
            db.clenstvi.insert(user_id=int(request.args[0]), group_id=grp_id)
            session.flash = msg_pridan
        redirect(URL(kam_potom))

def _getgrpid(gr_name):
    grp = db(db.auth_group.role==gr_name).select().first()
    if not grp:
        db.auth_group.insert(role=gr_name)
        db.commit()
        grp = db(db.auth_group.role==gr_name).select().first()
    return grp.id

@auth.requires_signature()
def zrus_clenstvi():
    if len(request.args)==1:
        clenstvi = db(db.clenstvi.id==request.args[0]).select().first()
        if not clenstvi.do_dne:
            clenstvi.update_record(do_dne=date.today())
    redirect(URL('default', 'index'))

@auth.requires_membership('vedeni')
def zakaznici():
    grid = SQLFORM.grid(db.auth_user,
              fields=(db.auth_user.vs, db.auth_user.ss,
                  db.auth_user.organizator,
                  db.auth_user.nick, db.auth_user.zaloha,
                  db.auth_user.first_name, db.auth_user.last_name,
                  db.auth_user.email, db.auth_user.email_ver,
                  db.auth_user.telefon, db.auth_user.tel_ver,
                  db.auth_user.prihlasen,
                  db.auth_user.neposilat, db.auth_user.ne_ostatnim,
                  db.auth_user.id
                  ),
              deletable=auth.has_membership('pokladna'),
              editable=auth.has_membership('pokladna'),
              create=auth.has_membership('pokladna'),
              csv=auth.has_membership('pokladna'),
              paginate=100,
              orderby=db.auth_user.nick.lower(),  # 'auth_user.nick COLLATE lexical'
              showbuttontext=False,
              maxtextlengths={'auth_user.email' : 30}
              )
    search_input = grid.element('#w2p_keywords')
    search_input and search_input.attributes.pop('_onfocus')
    return dict(grid=grid)

@auth.requires_login()
def zadosti():
    vyznam = {1:'převést zálohu sem',
              2:'vrátit zálohu na účet',
              3:'žádost o členství',
              4:'refundace'}
    zadosti = db(db.zadost.id>0).select(
          db.zadost.ALL, db.auth_user.nick,
          left=db.auth_user.on(db.auth_user.id==db.zadost.idauth_user),
          orderby=~db.zadost.zadost)
    return dict(zadosti=zadosti, vyznam=vyznam)

@auth.requires_membership('pokladna')
def vyridit():
    if len(request.args)>=2:
        if request.args(0)=='1': # převést sem zálohu sa.cz
            redirect(URL('zalohu_sem', args=request.args(1)))
        elif request.args(0)=='2': # vrátit zálohu
            redirect(URL('zalohu_vratit', args=request.args(1)))
        elif request.args(0)=='3': # přijmout za člena
            redirect(URL('prijmout_clena', args=request.args(1)))
    redirect(URL('zadosti'))

@auth.requires_membership('pokladna')
def prijmout_clena():     # asi by to chtělo rodné číslo...?
    if len(request.args)>=1:
        zadost = db.zadost[request.args(0)]
        user_id = zadost.idauth_user
        clenstvi = db(db.clenstvi.user_id==user_id).select()
        for clenstvi1 in clenstvi:
            if not clenstvi1.do_dne:
                session.flash = "přerušeno - má zahájené členství -> smazat žádost"
                redirect(URL('zadosti'))
        clen_id = db(db.auth_group.role=='clen sdruzeni').select().first().id
        auth.add_membership(clen_id, user_id)
        db.clenstvi.insert(user_id=user_id, group_id=clen_id,
                        ode_dne=date.today())
        redirect(URL('vyrizeno', args=request.args(0)))
    redirect(URL('zadosti'))

@auth.requires_membership('pokladna')
def zalohu_vratit():
    if len(request.args)>=1:
        form = SQLFORM.factory(
                Field('cislo_uctu', length=30, label='Číslo účtu',
                        requires=IS_NOT_EMPTY()),
                Field('kod_banky', length=10, label='Kód banky',
                        requires=IS_NOT_EMPTY()),
                Field('zaloha', 'decimal(11,2)',
                        label="Zálohu snížit o (vč.poplatku)"),
                Field('strhnout', 'decimal(11,2)', label="Z toho poplatek"),
                Field('vs', length=30, label='VarSym'),
                Field('ss', length=30, label='SpecSym'),
                )
        zadost = db.zadost[request.args(0)]
        zakaznik = db.auth_user[zadost.idauth_user]
        zaloha = zakaznik.zaloha 
        form.vars.zaloha = zaloha
        form.vars.strhnout = 30.0 # nefunguje: min((30., form.vars.zaloha))
        form.vars.cislo_uctu = zadost.cislo_uctu
        form.vars.kod_banky = zadost.kod_banky
        form.vars.vs = zadost.vs
        form.vars.ss = zadost.ss
        
        if form.process().accepted:
            zaloha = form.vars.zaloha  # tj. kolik ze zálohy vzít vč. poplatku
            # toto brani zpracovani po nacteni platby z banky, proto kontrolu vyhazuji 9.6.2015
            #if zaloha>zakaznik.zaloha:
            #    session.flash = "přerušeno - zákazník nemá tolik na záloze"
            #    redirect(URL('zadosti'))
            if zaloha<form.vars.strhnout:
                session.flash = "přerušeno - stržená částka nestačí na poplatek"
                redirect(URL('zadosti'))
            cas = datetime.now()
            if form.vars.strhnout:     # if poplatek
                db.pohyb.insert(idauth_user=zadost.idauth_user,
                      idma_dati=Uc_sa.oz, iddal=Uc_sa.vynos_jiny,
                      datum=cas, castka=form.vars.strhnout,
                      popis="Poplatek Vrácení zálohy %s"%zakaznik.nick,
                      zakaznik=zadost.vs, vs=zadost.vs,
                      id_pokynu='vr zal p')
            prevedeno = zaloha-form.vars.strhnout
            '''
            # pohyb se zapsat nesmí, protože z banky (nebo z pokladny?) přijde
            #   vzápětí skutečný pohyb, takže by se dublovaly a záloha by šla
            #   do mínusu
            if prevedeno>0:
                db.pohyb.insert(idauth_user=zadost.idauth_user,
                      idma_dati=Uc_sa.oz, iddal=Uc_sa.vraceno,
                      datum=cas, castka=prevedeno,
                      popis="Vrácení zálohy %s"%zakaznik.nick,
                      zakaznik=zadost.vs, vs=zadost.vs, ss=zadost.vs, ks='0308',
                      cislo_uctu=zadost.cislo_uctu, kod_banky=zadost.kod_banky,
                      id_pokynu='vr zal bu')
            '''
            zakaznik.update_record(zaloha=zakaznik.zaloha-form.vars.strhnout)
                  # dříve tu bylo -zaloha(=-form.vars.zaloha), jenže tím se
                  #  strhávalo duplicitně, ještě i poté, co platba došla z banky
            zadost.update_record(zadano=zaloha, prevedeno=prevedeno)
            mail_subj = Uc_sa.mail_subj
            podpis = Uc_sa.podpis
            mail.send(zakaznik.email,
                  mail_subj % TFu('Vrácení osobní zálohy'),
                  ('Ze zálohy Kč %1.2f\n'
                  'po stržení poplatku Kč %1.2f\n'
                  'jsme poslali Kč %1.2f\n'
                  'na účet %s/%s.\n\n'
                  'V případě nejasnosti kontaktuj pokladníka.\n'
                  'Díky za účast na našich akcích a rádi Tě uvidíme později.'
                  %(zaloha, form.vars.strhnout, zaloha-form.vars.strhnout,
                        zadost.cislo_uctu, zadost.kod_banky))
                  + (podpis%zakaznik.email))
            redirect(URL('vyrizeno', args=request.args(0)))
        response.view = 'prehledy/zalohu.html'
        return dict(form=form)              
    redirect(URL('zadosti'))

@auth.requires_membership('pokladna')
def zalohu_sem():
    if len(request.args)>=1:
        form = SQLFORM.factory(
                Field('castka', 'decimal(11,2)', label="Kolik Kč přebíráme?")
                )
        if form.process().accepted:
            zadost = db.zadost[request.args(0)]
            povel = (zadost.vs, form.vars.castka)
            __init(povel[0], povel[1])
            zadost.update_record(zadano=form.vars.castka,
                                prevedeno=form.vars.castka)
            redirect(URL('vyrizeno', args=request.args(0)))
        response.view = 'prehledy/zalohu.html'
        return dict(form=form)              
    redirect(URL('zadosti'))

# duplicitně převzato z fixdata.py
def __init(vs, castka):
    zakaznik = db(db.auth_user.vs==vs).select().first()
    if zakaznik:
        db.pohyb.insert(
              idauth_user=zakaznik.id,
              castka=castka,
              idma_dati=Uc_sa.oz_sa,
              iddal=Uc_sa.oz,
              datum=datetime.now(),
              popis="převod ze spolecneaktivity.cz",
              zakaznik=vs,
              vs=vs,
              ss=vs,
              id_pokynu='z sa.cz'
              )
        zakaznik.update_record(zaloha=zakaznik.zaloha + Decimal(castka))
          # decimal+-float, float+-decimal není podporováno
          # přiřazením float do zakaznik.zaloha by bylo zakaznik.zaloha float,
          # ačkoli při uložení do databáze se to automaticky převede na Decimal
        mail_subj = Uc_sa.mail_subj
        podpis = Uc_sa.podpis
        mail.send(zakaznik.email,
            mail_subj % TFu('Připsána záloha ze spolecneaktivity.cz'),
              ('Byla vynulována Tvoje osobní záloha %s Kč na webu Jiřího Poučka spolecenaktivity.cz.\n'
              'O tuto částku byla navýšena Tvoje osobní záloha v účetním systému sdružení,\n'
              'takže bude možné platit i pro spolecneaktivity.cz i pro fungujeme.aspone.cz.\n\n'
              'Další podrobnosti zjištíš přihlášením se do účetního systému sdružení (přihlašovací údaje jsou uvedeny níže).\n'
              'V případě nejasností kontaktuj pokladníka.' % castka)
              + (podpis%zakaznik.email))

@auth.requires_membership('pokladna')
def vyrizeno():
    if len(request.args)>=1:
        db.zadost[request.args[0]] = dict(prevod=datetime.now(),
                              vyridil_id=auth.user_id)
        if len(request.args)>=3:
            db.zadost[request.args[0]] = dict(zadano=request.args[1],
                                          prevedeno=request.args[2])
    redirect(URL('zadosti'))

@auth.requires_membership('vedeni')
def duplicity():
    count = db.pohyb.id.count()
    seznam = db((db.pohyb.idauth_user!=None)
                  & (db.pohyb.idma_dati==Uc_sa.oz)
                  & (db.pohyb.ss>='9000')
            ).select(
            db.pohyb.idauth_user, db.pohyb.idma_dati, 
                  db.pohyb.castka, db.pohyb.ss,
                  db.auth_user.nick, db.auth_user.vs, count,
            orderby=db.pohyb.idauth_user|db.pohyb.castka|db.pohyb.ss,
            groupby=db.pohyb.idauth_user|db.pohyb.castka|db.pohyb.ss,
            having=(count>1),
            left=db.auth_user.on(db.auth_user.id==db.pohyb.idauth_user))
    return dict(seznam=seznam, count=count)

# ponecháno zde, protože potenciálně může sloužit pro "jednoduche" i "podvojne"
@auth.requires_membership('pokladna')
def pridat_pohyb():
    response.view = 'prehledy/edit_pohyb.html'
    form = SQLFORM(db.pohyb, ignore_rw=True)
    if form.process().accepted:
        redirect(URL('platby', 'prehled'))
    return dict(form=form)

# ponecháno zde, protože potenciálně může sloužit pro "jednoduche" i "podvojne"
@auth.requires_membership('pokladna')
def edit_pohyb():
    if len(request.args)>0:
        form = SQLFORM(db.pohyb, request.args[0], ignore_rw=True)
        if form.process().accepted:
            redirect(URL(request.vars['section'], request.vars['next']))
        return dict(form=form)

# ponecháno zde, protože potenciálně může sloužit pro "jednoduche" i "podvojne"
@auth.requires_membership('pokladna')
def del_pohyb():
    if len(request.args)>0:
        del db.pohyb[request.args[0]]
        redirect(URL(request.vars['section'], request.vars['next']))
