#!/usr/bin/env python
# -*- coding: utf8 -*-

from datetime import datetime, timedelta, time, date

def zpatky(dni):
    datum_od = datetime.now()-timedelta(days=dni)
    return datum_od.combine(datum_od.date(), time(0,0))

def aliases(db):
    return (db.ucet.with_alias('md'), db.ucet.with_alias('dal'),
            db.auth_user.with_alias('org'))

class Uc_sa(object):
    u'''zatím natvrdo podúčty účetnictví Společné Aktivity o.s.'''
    pokladna = 1	# 211	pokladna
    bezny = 2	    # 221	bankovní účet
    dary = 3		  # 684	dary
    oz_sa = 4	    # 379-10 os.zálohy ve správě spolecneaktivity.cz
    pro_sa = 5    # 379-11 os.zálohy připravené k přesunu do správy u spolecneaktivity.cz
    oz_fu = 6	    # 379-12 os.zálohy ve správě Fungujeme
    oz = 7		    # 379-09 os.zálohy spravované centrálně (na wKasa)
    oz_vy = 8 #nepoužívat    # 379-99 os.zálohy (asi už výnosy) z hotovost.příjmů
    oz_presun = 26  # 379-07 dočasný účet pro přesun zálohy mezi 2 zákazníky
    oz_x = 24     # příp. os.zál. neurčeného vlastníka 
    org = 9       # 211-01 pokladna u organizátorů
    akce = 10     # 518-01 náklady akcí
    provoz = 11   # 548-03 náklady provozní
    odmeny = 15   # 58 poskytnuté příspěvky (odměny)
    vynos = 12    # 602 výnos za akce
    vynos_jiny = 13 # 640 výnosy ostatní
    vraceno = 14  # XXX vrácené zálohy
    zaloha = 21   # 314 zálohy
    fp = 22       # 321 faktury přijaté

    gl_ozwk = (5,7,24) # osobní účet ve správě na wKasa
    gl_sdr = (1,2,9)   # účty sdružení

    mail_subj = "Společné Aktivity, o.s. - %s"
    podpis = ('\n\n\nSpolečné Aktivity, o.s.\n'
        'Mirek Zvolský - pokladna/provoz\n'
        '732457966, zvolsky@seznam.cz\n' 
        'Tvůj osobní účet: platby.alwaysdata.net\n'
        '  uživatel: %s\n'
        'Běžný účet sdružení: v zápatí stránky platby.alwaysdata.net')

def je_zakaznik(db, vs, id=None):
    '''testuje v databázi db, zda vs je platný variabilní symbol zákazníka 
    '''
    if vs:
        rec = db(db.auth_user.vs==vs).select().first()
        if rec:
            if id:
                id[0] = rec.id
            return True
        # uznáváme i spolecneaktivity.cz ss-číslo (tam registrován později)
        rec = db(db.auth_user.ss==vs).select().first()
        if rec:
            if id:
                id[0] = rec.id
            return True
    return False

def sa_ss(vs, ss):
    '''podle vyplněného variabilního symbolu určí,
    zda je zákazníkem i na spolecneaktivity.cz
    vrací (sa_platit=False/True, sa_ss)
    '''
    vsi = int(vs)
    if vsi<80111:
        sass = vs
    elif ss:
        sass = ss
    else:
        sass = None
    return not ss, sass

def fix_login(db, auth, vs_default):
    if auth.user_id:    # přihlášený uživatel
        loginlog(db, auth)            # loguje datum použití aplikace
        fix_vs(db, auth, vs_default)  # nemá-li zákazník VS, přidělí mu jej

def fix_vs(db, auth, vs_default):
    '''Nemá-li zákazník variabilní symbol, přidělí mu jej.
    Pozor: Předpokládá existenci záznamu s předchozím přiděleným číslem!
    '''
    if auth.user.vs==vs_default:
        new_vs = get_new_vs(db, vs_default)
        db(db.auth_user.id==auth.user_id).update(vs=new_vs)
        db.commit()
        auth.user.vs = new_vs

def get_new_vs(db, vs_default):
    mx = db.auth_user.vs.max()
    last_vs = db(db.auth_user.vs!=vs_default).select(mx).first()[mx]
    # nejsem si jisty, jak to pracuje pro string, ale v rozsahu 80000-99999 to bude Ok
    return str(int(last_vs) + 1)

def loginlog(db, auth):
    '''loguje datum použití aplikace
    '''
    today = date.today()
    #if auth.user.prihlasen!=today:
    if db.auth_user[auth.user_id].prihlasen!=today:
        db.auth_user[auth.user_id] = dict(prihlasen=today)
        db.loginlog.insert(idauth_user=auth.user_id, datum=today)
        db.commit()
        auth.user.prihlasen = today

def vs2id(db, vs):
    '''převede osobní symbol (ve wKasa variabilní symbol) na id uživatele
    '''
    if vs:
        zakaznik = db(db.auth_user.vs==vs).select(db.auth_user.id).first()
        if zakaznik:
            return zakaznik.id
    return None
