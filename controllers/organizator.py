# coding: utf8

from mz_wkasa_platby import sa_ss, Uc_sa, vs2id

@auth.requires_login()
def pokladna():
    adm = auth.has_membership('vedeni')
    if adm and request.args(0)=='vse': 
        query = db.pohyb.idorganizator!=None
    else: 
        organizator = adm and vs2id(db, request.args(0)
                  ) or auth.user_id # lze zadat parametrem
        query = db.pohyb.idorganizator==organizator 
    zapisy = db(query).select(
                db.pohyb.ALL, db.auth_user.nick,
                left=db.auth_user.on(db.auth_user.id==db.pohyb.idauth_user),
                orderby=~db.pohyb.datum)
    mam = 0
    for zapis in zapisy:
        if zapis.pohyb.iddal == Uc_sa.org:   # organizátor vydal
            mam -= zapis.pohyb.castka
        else:                        # organizátor získal
            mam += zapis.pohyb.castka

    return dict(zapisy=zapisy, mam=mam,
              adm=adm, pokladnik=auth.has_membership('pokladna'),
              arg=request.args(0) or '')
    u'''význam pohyb.ks(konst.sym.)
    1.pozice peníze, 2.pozice doklad
    0 není, 1 předat, 2 předáno, 3 odsouhlaseno, ? neví se,
        ! doklad ztracen, # neví se, ale bylo dříve označeno jako odsouhlasené
    kombinace pro Vyřízeno: 33, 30, 3#, 3!
    statusy, které zobrazí Odsouhlasit: 22, 23, 2#, 2!, 32
    '''

@auth.requires_membership('vedeni')
def dluhy():
    zapisy = db(db.pohyb.idorganizator!=None).select(
                db.pohyb.castka, db.pohyb.idma_dati, db.pohyb.iddal,
                db.pohyb.idorganizator, db.auth_user.nick, db.auth_user.email, db.auth_user.vs,
                left=db.auth_user.on(db.auth_user.id==db.pohyb.idorganizator),
                orderby=db.pohyb.idorganizator)
    dluhy = {}
    id_last = -999
    for zapis in zapisy:
        if id_last!=zapis.pohyb.idorganizator:
            id_last = zapis.pohyb.idorganizator
            klic = zapis.auth_user.nick or ('id %s' % zapis.pohyb.idorganizator)
            dluhy[klic] = [0, zapis.auth_user.email, zapis.auth_user.vs]
        if zapis.pohyb.iddal==Uc_sa.org:   # organizátor vydal
            dluhy[klic][0] -= zapis.pohyb.castka
        else:                              # organizátor získal
            dluhy[klic][0] += zapis.pohyb.castka
    return dict(dluhy=dluhy)

@auth.requires_login()
def pokladnikovi():
    organizator = auth.has_membership('vedeni'
        ) and vs2id(db, request.args(0)) or auth.user_id  # lze zadat parametrem
    _skryj(2)
    form = SQLFORM(db.pohyb)
    if form.validate():
        db.pohyb.insert(idorganizator=organizator, id_pokynu=TFu('do pokladny'), 
                idma_dati=Uc_sa.pokladna, iddal=Uc_sa.org, ks='20',
                **dict(form.vars))
        redirect(URL('pokladna'))
    response.view = 'organizator/novy_pohyb.html'
    return dict(form=form, warning=False)

@auth.requires_login()
def od_pokladnika():
    organizator = auth.has_membership('vedeni'
        ) and vs2id(db, request.args(0)) or auth.user_id  # lze zadat parametrem
    _skryj(2)
    form = SQLFORM(db.pohyb)
    if form.validate():
        db.pohyb.insert(idorganizator=organizator, id_pokynu=TFu('z pokladny'),
                idma_dati=Uc_sa.org, iddal=Uc_sa.pokladna, ks='20',
                **dict(form.vars))
        redirect(URL('pokladna'))
    response.view = 'organizator/novy_pohyb.html'
    return dict(form=form, warning=False)

@auth.requires_login()
def dar():
    organizator = auth.has_membership('vedeni'
        ) and vs2id(db, request.args(0)) or auth.user_id  # lze zadat parametrem
    _skryj()
    form = SQLFORM(db.pohyb)
    for idx in xrange(len(form[0])-1, -1, -1):
        row = form[0][idx]
        _na_konec(row, idx, form, 'pohyb_idauth_user__row', -2)
        _na_konec(row, idx, form, 'pohyb_cislo_uctu__row')
    _set_akce(form)
    if form.validate():
        idpokynu = TFu('dar')
        iddal = Uc_sa.dary
        db.pohyb.insert(idorganizator=organizator,
                id_pokynu=idpokynu,
                idma_dati=Uc_sa.org, iddal=iddal, ks='10',
                **dict(form.vars))
        _get_akce(form)
        redirect(URL('pokladna'))
    response.view = 'organizator/novy_pohyb.html'
    return dict(form=form, warning=False)

@auth.requires_login()
def strhnout():
    organizator = auth.has_membership('vedeni'
        ) and vs2id(db, request.args(0)) or auth.user_id  # lze zadat parametrem
    _skryj(warning=True)
    form = SQLFORM(db.pohyb)
    for idx in xrange(len(form[0])-1, -1, -1):
        row = form[0][idx]
        _na_konec(row, idx, form, 'pohyb_idauth_user__row', -2)
        _na_konec(row, idx, form, 'pohyb_cislo_uctu__row')
    _set_akce(form)
    if form.validate():
        if form.vars.idauth_user:                 
            idpokynu = TFu('za akci (strhnout z os.zál.)')
            iddal = Uc_sa.oz        
            uzivatel = db.auth_user[form.vars.idauth_user]
            uzivatel.update_record(zaloha=uzivatel.zaloha + form.vars.castka)
        else:
            idpokynu = TFu('za akci (kdo ???)')
            iddal = Uc_sa.oz_x        
        db.pohyb.insert(idorganizator=organizator,
                id_pokynu=idpokynu,
                idma_dati=Uc_sa.org, iddal=iddal, ks='10',
                **dict(form.vars))
        _get_akce(form)
        redirect(URL('pokladna'))
    response.view = 'organizator/novy_pohyb.html'
    return dict(form=form, warning=True)

@auth.requires_login()
def hotovka():
    organizator = auth.has_membership('vedeni'
        ) and vs2id(db, request.args(0)) or auth.user_id  # lze zadat parametrem
    _skryj()
    form = SQLFORM(db.pohyb)
    for idx in xrange(len(form[0])-1, -1, -1):
        row = form[0][idx]
        _na_konec(row, idx, form, 'pohyb_idauth_user__row', -2)
        _na_konec(row, idx, form, 'pohyb_cislo_uctu__row')
    _set_akce(form)
    if form.validate():
        idpokynu = TFu('za akci (ne na os.zálohu)')
        iddal = Uc_sa.vynos      
        db.pohyb.insert(idorganizator=organizator,
                id_pokynu=idpokynu,
                idma_dati=Uc_sa.org, iddal=iddal, ks='10',
                **dict(form.vars))
        _get_akce(form)
        redirect(URL('pokladna'))
    response.view = 'organizator/novy_pohyb.html'
    return dict(form=form, warning=False)

@auth.requires_login()
def hotov_vydaj():
    organizator = auth.has_membership('vedeni'
        ) and vs2id(db, request.args(0)) or auth.user_id  # lze zadat parametrem
    _skryj(1)
    form = SQLFORM(db.pohyb)
    _set_akce(form)
    if form.validate():
        db.pohyb.insert(idorganizator=organizator, id_pokynu=TFu('výdaj'),
                idma_dati=Uc_sa.akce, iddal=Uc_sa.org, ks='11',
                **dict(form.vars))
        _get_akce(form)
        redirect(URL('pokladna'))
    response.view = 'organizator/novy_pohyb.html'
    return dict(form=form, warning=False)

@auth.requires_membership('pokladna')
def cokoliv():
    for fld in db.pohyb:
        fld.readable = True
        fld.writable = True
    form = SQLFORM(db.pohyb)
    if form.process().accepted:
        if form.vars.idauth_user:
            redirect(URL('platby', 'pohyby',
                        args=db.auth_user[form.vars.idauth_user].vs))
        else:
            redirect(URL('pokladna'))
    response.view = 'organizator/novy_pohyb.html'
    return dict(form=form, warning=False)

def _skryj(vic=0, warning=False):
    '''oba parametry řeší různé varianty skrývání/ukázání údajů - mohly by tedy být sloučeny do jednoho
    další nesystematické informace jsou pro request.function v šabloně
    '''
    db.pohyb.partner_id.readable=db.pohyb.partner_id.writable=False
    db.pohyb.fp_id.readable=db.pohyb.fp_id.writable=False
    db.pohyb.idma_dati.readable=db.pohyb.idma_dati.writable=False
    db.pohyb.iddal.readable=db.pohyb.iddal.writable=False
    db.pohyb.id_pokynu.readable=db.pohyb.id_pokynu.writable=False
    db.pohyb.kod_banky.readable=db.pohyb.kod_banky.writable=False
    db.pohyb.idorganizator.readable=db.pohyb.idorganizator.writable=False
    db.pohyb.zakaznik.readable=db.pohyb.zakaznik.writable=False
    db.pohyb.ks.readable=db.pohyb.ks.writable=False
    db.pohyb.id_pohybu.readable=db.pohyb.id_pohybu.writable=False
    db.pohyb.datum.comment = TFu('skutečné datum příjmu')
    db.pohyb.vs.readable=db.pohyb.vs.writable=False
    if vic>=1:
        db.pohyb.popis.comment = TFu(
            'cokoli, co chceš sdělit pokladníkovi, nebo co má u tohoto pohybu zůstat poznamenáno')
        db.pohyb.idauth_user.readable=db.pohyb.idauth_user.writable=False
        db.pohyb.cislo_uctu.readable=db.pohyb.cislo_uctu.writable=False
        db.pohyb.datum.comment = TFu('datum podle dokladu')
        if vic>=2:
            db.pohyb.ss.readable=db.pohyb.ss.writable=False
            db.pohyb.nazev_banky.readable=db.pohyb.nazev_banky.writable=False
            db.pohyb.popis.comment = TFu('místo předání, apod.')
            db.pohyb.datum.comment = TFu('skutečné datum předání')
    else:
        db.pohyb.popis.comment = TFu('Zapiš cokoli, co chceš vysvětlit pokladníkovi.')
        if warning:
            db.pohyb.idauth_user.comment=TFu('musí být uvedeno')
            db.pohyb.cislo_uctu.readable=db.pohyb.cislo_uctu.writable=False
        else:
            db.pohyb.idauth_user.comment=TFu('přednostně zde; jen v nouzi v následujícím údaji')
            db.pohyb.cislo_uctu.label = TFu('Nick nereg. uživatele')
            db.pohyb.cislo_uctu.comment = TFu('zadej, jestliže nemůžeš nalézt/vybrat uživatele v předchozím údaji; můžeš zapsat i něco jako "host" nebo "kamarádka Kajouska"')
        #db.pohyb.vs.label = TFu('Symbol uživatele')
        #db.pohyb.vs.comment = TFu('pokud ho náhodou víte, je to ideální (101+ z sa nebo 80111+ přidělené zde); když ne, nevadí')
    db.pohyb.castka.label = TFu('Částka')
    db.pohyb.castka.comment = TFu('kladné číslo')
    db.pohyb.ss.label = TFu('Číslo akce')
    db.pohyb.ss.comment = TFu('číslo akce (fu:9000+, sa:2000+) -- pokud máš doklad, poznamenej na něj tužkou toto číslo')
    db.pohyb.nazev_banky.label = 'Akce'
    db.pohyb.nazev_banky.comment = '(pokud možno..) datum a název akce'
    #db.pohyb.nazev_banky.requires = IS_NOT_EMPTY()
    db.pohyb.castka.requires = IS_DECIMAL_IN_RANGE(0.1, 999999.0)

def _na_konec(row, idx, form, rowid, pozice=-1):
    if row.attributes['_id']==rowid:
        form[0].insert(pozice, row)
        del form[0][idx]

def _set_akce(form):    
    if session.nazev_banky:
        form.vars.nazev_banky = session.nazev_banky
        form.vars.ss = session.ss                 
        form.vars.datum = session.datum.strftime('%d.%m.%Y')                 

def _get_akce(form):    
    session.nazev_banky = form.vars.nazev_banky
    session.ss = form.vars.ss                 
    session.datum = form.vars.datum                 

def st33():
    if len(request.args)>0:
        db(db.pohyb.id==request.args[0]).update(ks='33')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def st30():
    if len(request.args)>0:
        db(db.pohyb.id==request.args[0]).update(ks='30')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))

def st1_():
    if len(request.args)>0:
        stx_(request.args[0], '1')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def st2_():
    if len(request.args)>0:
        stx_(request.args[0], '2')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def st3_():
    if len(request.args)>0:
        stx_(request.args[0], '3')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def stq_():
    if len(request.args)>0:
        stx_(request.args[0], '?')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def stx_(pohyb_id, new):
        rec = db(db.pohyb.id==pohyb_id).select(db.pohyb.id, db.pohyb.ks).first()
        rec.update_record(ks=new+rec.ks[1])

def st_0():
    if len(request.args)>0:
        st_x(request.args[0], '0')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def st_1():
    if len(request.args)>0:
        st_x(request.args[0], '1')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def st_2():
    if len(request.args)>0:
        st_x(request.args[0], '2')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def st_3():
    if len(request.args)>0:
        st_x(request.args[0], '3')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def st_q():
    if len(request.args)>0:
        st_x(request.args[0], '?')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def st_jako_mam():
    if len(request.args)>0:
        st_x(request.args[0], '#')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def st_ztracen():
    if len(request.args)>0:
        st_x(request.args[0], '!')
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
def st_x(pohyb_id, new):
        rec = db(db.pohyb.id==pohyb_id).select(db.pohyb.id, db.pohyb.ks).first()
        rec.update_record(ks=rec.ks[0]+new)

def odstran_chybny():
    if len(request.args)>0:
        pohyb = db.pohyb[request.args[0]]
        if pohyb.idauth_user:                
            uzivatel = db.auth_user[pohyb.idauth_user]
            uzivatel.update_record(zaloha=uzivatel.zaloha - pohyb.castka)                
        pohyb.delete_record()
    redirect(URL('pokladna', args=request.args(1) if request.args(1) else ()))
