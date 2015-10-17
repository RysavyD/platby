# coding: utf8

from datetime import datetime, date, timedelta, time
from mz_wkasa_platby import sa_ss, Uc_sa, vs2id
from bs4 import BeautifulSoup
from spolecneaktivity_cz import unformat_castka

@auth.requires_login()
def prehled():
    ss = sa_ss(auth.user.vs, auth.user.ss)[1] # spec.sym. na Jirkově
    sa_zal = __get_zaloha(ss)
    ja = db.auth_user[auth.user_id]
    txt_clen = 'clen sdruzeni'
    clen_id = db(db.auth_group.role==txt_clen).select().first().id
    clenstvi = db((db.clenstvi.user_id==auth.user_id)&
          (db.clenstvi.group_id==clen_id)
          ).select(orderby=~db.clenstvi.ode_dne).first()
    return dict(zaloha=ja.zaloha, sa_ss=ss, sa_zal=sa_zal,
          clen=auth.has_membership(txt_clen),
          clenstvi=clenstvi)

@auth.requires_membership('pokladna')
def nulovat_zalohu():
    '''/id/vs/zustatek, pokud zustatek chybi, tak vynuluje'''
    zakaznik_id = request.args(0)
    zakaznik_vs = request.args(1)
    zustatek = int(request.args(2) or 0)
    if zakaznik_id and zakaznik_vs:
        zakaznik = db.auth_user[zakaznik_id]
        zakaznik.update_record(zaloha=zustatek)
        redirect(URL('pohyby', args=zakaznik_vs))
    else:
        session.flash = 'Chybné volání'
        redirect(URL('default', 'index'))

@auth.requires_login()
def pohyby():
    class Celkem(object):
        vlozeno=vraceno=sa_vlozeno=z_sa_prevedeno=ozwk_vlozeno=ozwk_cerpano = 0
    uzivatel_id = auth.has_membership('vedeni'
        ) and vs2id(db, request.args(0)) or auth.user_id  # lze zadat parametrem
    pohyby = db(db.pohyb.idauth_user==uzivatel_id
                      ).select(orderby=~db.pohyb.datum)
    uzivatel = db.auth_user[uzivatel_id]
    nick = uzivatel.nick if request.args(0) else '' # promítání cizích adminem
    zaloha = uzivatel.zaloha
            # nelze auth.user.zaloha, když jsem připustil zadání id parametrem
    for pohyb in pohyby:
        if pohyb.idma_dati in Uc_sa.gl_ozwk and pohyb.iddal in Uc_sa.gl_ozwk:
            pohyb.castka = 0  # interní převod mezi 379 ve správě wKasa
        else:       # zobrazit uživateli
                 # gl_ozwk = (5,7)   # osobní účet ve správě na wKasa (OsZ 379-09, >SA 379-11)
                 # gl_sdr = (1,2,9)  # účty sdružení (pokladna a BÚ)
                 # oz_sa             # osobní účet u sa.cz
            # vložení a vrácení celkově
            ukaz_minus = False
            if pohyb.idma_dati in Uc_sa.gl_sdr:
                Celkem.vlozeno += pohyb.castka
            elif pohyb.iddal in Uc_sa.gl_sdr: 
                Celkem.vraceno += pohyb.castka
                ukaz_minus = True
            
            # vložení a převedení z sa.cz (vrácení nelze určit, dokud MD==None)
            if pohyb.iddal==Uc_sa.oz_sa:
                Celkem.sa_vlozeno += pohyb.castka
            elif pohyb.idma_dati==Uc_sa.oz_sa and pohyb.iddal in Uc_sa.gl_ozwk:
                Celkem.z_sa_prevedeno += pohyb.castka
            
            # vložení a čerpání z wKasa (vrácení nelze určit, dokud MD==None)
            if pohyb.iddal in Uc_sa.gl_ozwk:
                Celkem.ozwk_vlozeno += pohyb.castka
            # zde bylo elif, změnil jsem na if, což je správně i při převodu OsZ <-> >SA
            #  ale protože takový převod v datech není, tak to v reálu nic neovlivní
            if pohyb.idma_dati in Uc_sa.gl_ozwk:      
                Celkem.ozwk_cerpano += pohyb.castka
                ukaz_minus = True
                if pohyb.iddal in Uc_sa.gl_ozwk:
                    pohyb.castka = 0  # vnitřní převod, záloha se nemění
                    # takové pohyby v reálu nejsou (viz výše), ale pro případ zjemnění analytiky

            # obrácení znaménka pro zobrazení
            if ukaz_minus:                
                pohyb.castka = -pohyb.castka
    return dict(zaloha=zaloha, pohyby=pohyby, Celkem=Celkem,
            Uc_sa=Uc_sa, nick=nick, uzivatel_id=uzivatel_id)

@auth.requires_membership('vedeni')
def vse():
    return dict(pohyby=db().select(db.pohyb.ALL))

@auth.requires_login()
def seber_jirkovi():
    if len(request.args)>0:
        usr = db(db.auth_user.vs==request.args[0]).select().first()
    else:
        usr = auth.user
    db.zadost.insert(zadost=datetime.now(),
                    idauth_user=usr.id, vs=usr.vs, typ=1)
    return {}

@auth.requires_login()
def zadam_clenstvi():
    db.zadost.insert(zadost=datetime.now(),
                    idauth_user=auth.user_id, vs=auth.user.vs, typ=3)
    return {}

@auth.requires_login()
def vratit_zalohu():
    if len(request.args)>0:
        usr = db(db.auth_user.vs==request.args[0]).select().first()
    else:
        usr = auth.user
    pohyb = db((db.pohyb.zakaznik==usr.vs)
            &(db.pohyb.cislo_uctu!=None)
            &(db.pohyb.cislo_uctu!='')
            &(db.pohyb.idma_dati==Uc_sa.bezny)
            ).select(orderby=~db.pohyb.datum).first()
    form = SQLFORM.factory(
            Field('cislo_uctu', length=30,
                    label = TFu("Číslo účtu"),
                    default=pohyb.cislo_uctu if pohyb else None,
                    requires=IS_NOT_EMPTY()),
            Field('kod_banky', length=10,
                    label = '/ ' + TFu("Kód banky"),
                    default=pohyb.kod_banky if pohyb else None,
                    requires=IS_NOT_EMPTY()),
            )
    if form.process().accepted:
        if sa_ss(usr.vs, usr.ss):
            pass
            '''
            db.zadost.insert(zadost=datetime.now(),
                        idauth_user=usr.id, vs=usr.vs, typ=1)
            '''
        db.zadost.insert(zadost=datetime.now(), 
                        idauth_user=usr.id, vs=usr.vs, ss=usr.ss, typ=2,
              cislo_uctu=form.vars.cislo_uctu, kod_banky=form.vars.kod_banky)
        db.commit()
        session.flash = TFu('zálohu po odečtení poplatku zašleme na %s/%s'
              %(form.vars.cislo_uctu, form.vars.kod_banky))
        redirect(URL('prehled'))
    return dict(form=form)

@auth.requires_membership('vedeni')
def vyridit():
    if len(request.args)==3: # 1/2=z_SA/na_BÚ, ss, castka po odečtu poplatku
        zadosti = db((db.zadost.ss==request.args[1])
                  &(db.zadost.typ==request.args[0])).select()
        for kolikata, zadost in enumerate(zadosti):
            if zadost.prevod is None:
                prevedeno = (request.args[2]
                            if kolikata==len(zadosti)-1
                            else 0.0)
                zadost.update_record(prevod=datetime.now(), prevedeno=prevedeno)
        db.commit()
        return "ok" 
    else:
        return "selhalo"

@auth.requires_login()
def venovat():
    ja = db.auth_user[auth.user.id]
    if ja.zaloha<=0:
        session.flash = TFu("Momentálně na záloze nemáš žádné peníze.")
        redirect(URL('platby', 'prehled'))
    form = SQLFORM.factory(
            Field('zaloha', 'decimal(11,2)', default=ja.zaloha,
                    writable=False, label=TFu("Stav Tvé zálohy")),
            Field('venovat', 'decimal(11,2)', default=min((400.0, ja.zaloha)),
                    requires=IS_DECIMAL_IN_RANGE(1.0, ja.zaloha),
                    label=TFu("Převést Kč")),
            Field('komu', db.auth_user,
                    requires = IS_IN_DB(db, db.auth_user.id, db.auth_user._format),
                    label=TFu("komu"))
            )
    if form.validate():
        dnes = date.today()
        prijemce = db.auth_user[form.vars.komu]
        ja.update_record(zaloha=ja.zaloha - form.vars.venovat)
        db.pohyb.insert(idauth_user=auth.user.id, idma_dati=Uc_sa.oz, iddal=Uc_sa.oz_presun,
                castka=form.vars.venovat, datum=dnes,
                popis=TFu("předává kredit pro %s (VS=%s, id=%s)") % (
                        prijemce.nick, prijemce.vs, prijemce.id))
        db.pohyb.insert(idauth_user=prijemce.id, idma_dati=Uc_sa.oz_presun, iddal=Uc_sa.oz,
                castka=form.vars.venovat, datum=dnes,
                popis=TFu("kredit věnoval/a %s (VS=%s, id=%s)") % (
                        auth.user.nick, auth.user.vs, auth.user.id))
        prijemce.update_record(zaloha=prijemce.zaloha + form.vars.venovat)
        session.flash = TFu("Příjemci bylo úspěšně předáno %s.") % (
                        form.vars.venovat)
        redirect(URL('platby', 'prehled'))
    return dict(form=form)

@auth.requires_login()
def darovat_sdruzeni():
    zakaznik_id = request.args(0)
    zakaznik_vs = request.args(1)
    if zakaznik_id and zakaznik_vs and auth.has_membership('pokladna'):
        ja = db.auth_user[zakaznik_id]
        if ja.vs!=zakaznik_vs:
            raise HTTP(403)
        nick = ja.nick
    else:
        ja = db.auth_user[auth.user.id]
        nick = None
    if ja.zaloha<=0:
        session.flash = TFu("Momentálně na záloze nemáš žádné peníze.")
        redirect(URL('platby', 'prehled'))
    form = SQLFORM.factory(
            Field('zaloha', 'decimal(11,2)', default=ja.zaloha,
                    writable=False, label=TFu("Stav Tvé zálohy")),
            Field('venovat', 'decimal(11,2)', default=min((400.0, ja.zaloha)),
                    requires=IS_DECIMAL_IN_RANGE(1.0, ja.zaloha),
                    label=TFu("Darovat pro sdružení Kč")),
            )
    if form.validate():
        dnes = date.today()
        ja.update_record(zaloha=ja.zaloha - form.vars.venovat)
        db.pohyb.insert(idauth_user=ja.id, idma_dati=Uc_sa.oz, iddal=Uc_sa.dary,
                castka=form.vars.venovat, datum=dnes,
                popis=TFu("dar sdružení"))
        session.flash = TFu("Sdružení jsi daroval %s Kč. Děkujeme.") % (
                        form.vars.venovat)
        redirect(URL('platby', 'prehled'))
    return dict(form=form, nick=nick)

@auth.requires_membership('pokladna')
def zaloha():  # nastaví požadovanou zálohu
    if len(request.args)==2:
        db(db.auth_user.vs==request.args(0)).update(
                                    zaloha=float(request.args(1)))
        redirect(URL('pohyby', args=request.args(0)))
    return 'bad parameters'

@auth.requires_membership('pokladna')
def zrus():    # volba del v platby/pohyby - zruší pohyb a změní zálohu
    if len(request.args)==2:
        uzivatel = db.auth_user[request.args(0)]
        if uzivatel:
            pohyb = db.pohyb[request.args(1)] 
            if pohyb.idauth_user==db.auth_user.id:  # jistota
                zmena = 0
                if pohyb.iddal==Uc_sa.oz:  
                    zmena = -pohyb.castka
                elif pohyb.idma_dati==Uc_sa.oz:
                    zmena = pohyb.castka
                if zmena:  
                    uzivatel.update_record(zaloha=uzivatel.zaloha+zmena)
                del db.pohyb[request.args(1)]
                session.flash = "Změna zálohy o: %s"%zmena
        redirect(URL('pohyby', args=uzivatel.vs))
    return 'bad parameters'

def __get_zaloha(ss):
    '''zjistí zákazníkovu nedávnou zálohu parsováním uloženého zakaznici.html
    '''
    # duplicitní s export_csv.predej_dluzne, odkud jsem to oprásknul
    zaloha = fdate = None
    try:
        fname = os.path.join(request.folder, 'downloads', 'zakaznici.html')
        fdate = datetime.fromtimestamp(os.stat(fname).st_ctime)
        jirkovo = vfp.filetostr(fname)
        soup = BeautifulSoup(jirkovo)
        for zakaznik in soup.table('tr'):
            if str(zakaznik.td.a.string).strip().lstrip('0')==ss:
                zaloha = unformat_castka(zakaznik('td')[-4].string) 
                break
    except:
        pass
    return fdate, zaloha
