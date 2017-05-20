# -*- encoding: utf8 -*-

import os
import base64
from datetime import datetime, date, timedelta
from hashlib import md5
import vfp
from mz_wkasa_platby import get_new_vs

first_token = vfp.filetostr(os.path.join(request.folder,
                  'private', 'fungujeme.token'))

mail_subj = Uc_sa.mail_subj
podpis = Uc_sa.podpis

def naklady():
    '''vrací pohyby (výdaje a příjmy) k zadané akci
    ws/naklady/<args>, args:
    token = hash(token+vs_akce)
    vs_akce
    '''
    __log_ws('naklady')

    if len(request.args)==2:
        token = request.args[0]
        vs_akce = request.args[1]
        if token==md5(first_token+vs_akce).hexdigest():
            pohyby = db(db.pohyb.ss==vs_akce).select()
            retval = dict(pohyby=pohyby)
            __log_res('ok')
            return retval
    __log_res('failed')
    raise HTTP(403)

def zakaznici():
    '''vrací přehled zákazníků a jejich záloh
    ws/zakaznici/<args>, args:
    token = hash(token+YYYYmmddHHMMSS)
    dummy
    '''
    __log_ws('zakaznici')

    if len(request.args)==2:
        token = request.args[0]
        dummy = request.args[1]
        if token==md5(first_token+dummy).hexdigest():
            __log_res('ok')
            return retval
    __log_res('failed')
    raise HTTP(403)

def novy():
    '''založí uživatele
    ws/novy/<args>, args:
    token = hash(token+mail)
    mail
    nick
    '''
    __log_ws('novy')

    if len(request.args)==3:
        token = request.args[0]
        mail = request.args[1]
        #nick = request.args[2]  # web2py bug (good in url, bad in args)   %c4%8c = Č
        #nick = request.url.rsplit('/', 2)[-1]
        nick = base64.urlsafe_b64decode(request.args[2])
        regist_token = first_token
        if token==md5(regist_token+mail).hexdigest():
            nickL = nick.lower()
            mailL = mail.lower()
            uzivatel = db(db.auth_user.email.lower()==mailL).select().first()
            if uzivatel:
                retval = dict(vs=uzivatel.vs, problem='email existuje')
                __log_res('mail_dupl')
                return retval
            uzivatel = db(db.auth_user.nick.lower()==nickL).select().first()
            if uzivatel:
                __log_res('nick_dupl-rename (sa_%s)' % uzivatel.nick)
                uzivatel.update_record(nick='sa_' + uzivatel.nick)
            new_vs = get_new_vs(db, vs_default)  # vs_default je definován v db.py
            new_id = db.auth_user.insert(nick=nick, email=mail, vs=new_vs)
            retval = dict(vs=new_vs, problem='')
            __log_res('ok')
            return retval
    __log_res('failed')
    raise HTTP(403)

def udaje():
    '''vrací údaje o uživateli
    ws/udaje/<args>, args:
    token = hash(token+dotaz)
    dotaz (e-mail nebo variabilní symbol)
    '''
    __log_ws('udaje')

    if len(request.args)==2:
        token = request.args[0]
        dotaz = request.args[1]
        regist_token = first_token
        if token==md5(regist_token+dotaz).hexdigest():
            if '@' in dotaz:
                uzivatel = db(db.auth_user.email.lower() == dotaz.lower()).select().first()
            else:
                uzivatel = db(db.auth_user.vs == dotaz).select().first()
            if uzivatel:
                retval = dict(vs=uzivatel.vs or '',
                              email=uzivatel.email or '',
                              zaloha=str(uzivatel.zaloha or 0))
            else:
                retval = dict(vs='', email='', zaloha='0')
            __log_res('ok')
            return retval
    __log_res('failed')
    raise HTTP(403)

def chce():
    '''ws/pohyb/<args>, args:
    token = hash(token+vs+castka)
    vs
    castka>0: připsat
    email
    symbol akce
    popis
    vrací se: provedeno False/True,
              castka if True =zustatek, if False and castka<0 =chybí
    '''
    __log_ws('chce')

    is_valid, castka, popis, uzivatel, akce = __valid_params(request.args, db)
    if is_valid and castka>0:
        db.zadost.insert(zadost=datetime.now(),
                      idauth_user=uzivatel.id,
                      typ=3,
                      zadano=castka,
                      popis=popis,
                      ss=akce)
        mail.send(uzivatel.email, mail_subj % TFu('Přijata žádost o refundaci'),
            ('Přijali jsme Tvoji žádost o refundaci %s Kč.\n'
            'O vrácení peněz bude rozhodnuto po akci, '
                'zejména s ohledem na její finanční výsledek.'%castka)
            + ('\n\nPopis: %s'%popis) + (podpis%uzivatel.email))
        __log_res('ok')
        return dict(provedeno=True)
    __log_res('failed')
    raise HTTP(403)

def pohyb():
    '''ws/pohyb/<args>, args:
    token = hash(token+vs+castka)
    vs
    castka>0: připsat, castka<0 strhnout
    email
    symbol akce
    popis
    vrací se: provedeno False/True,
              castka if True =zustatek, if False and castka<0 =chybí
    '''

    __log_ws('pohyb')

    is_valid, castka, popis, uzivatel, akce = __valid_params(request.args, db)
    if is_valid:
        zustane = castka+float(uzivatel['zaloha'])
        if zustane<0:
            retval = dict(provedeno=False, castka=zustane)
            if not uzivatel.vyzva or (
                            date.today()-timedelta(1)>uzivatel.vyzva):
                            # jednou za 2 dny
                uzivatel.update_record(vyzva=date.today())
                mail.send(uzivatel.email,
                      mail_subj % TFu('Málo peněz na zaplacení'),
                      ('K zaplacení částky %s Kč Ti chybělo %s Kč.\n'
                        'Prosím, pošli proto peníze na účet sdružení nebo se '
                            'odhlaš z akce.'%(-castka, -zustane))
                        + ('\n\nPopis: %s'%popis)
                        + '\n\nPoznámka: Jsi-li přihlášen(a) i na další, zatím '
                          'neuhrazené akce, může být potřeba větší částka.'
                        + (podpis%uzivatel.email))
            __log_res('rejected (%s)'%castka)
        else:
            if castka>0:  # vracíme na os.zálohu
                idmd = Uc_sa.oz_fu
                iddal = Uc_sa.oz
            else:         # vybíráme za akci
                idmd = Uc_sa.oz
                iddal = Uc_sa.oz_fu
            uzivatel.update_record(zaloha=zustane)
            db.pohyb.insert(
                    idauth_user=uzivatel.id,
                    zakaznik=uzivatel.vs,
                    datum=datetime.now(),
                    castka=abs(castka),
                    popis=popis,
                    idma_dati=idmd,
                    iddal=iddal,
                    ss=akce,
                    )
            retval = dict(provedeno=True, castka=zustane)
            mail.send(uzivatel.email,
                mail_subj % 
                    (TFu('Zaplacena účast na akci') if castka<0
                    else TFu('Vráceny peníze na osobní zálohu')),
                ('Osobní záloha Ti byla '
                +('snížena o %s' if castka<0 else 'zvýšena o %s')%abs(castka)+
                ' Kč na úhradu akce.\n'
                'Nyní Ti zbývá na osobní záloze %s Kč.'%zustane)
                  + ('\n\nPopis: %s'%popis)
                  + (podpis%uzivatel.email))
            __log_res('ok')
        return retval
    __log_res('failed')
    raise HTTP(403)

def __valid_params(args, db):
    is_valid = False
    castka = 0
    popis = ''
    uzivatel = None
    akce = ''
    if len(args)>=6:
        token = args[0]
        vs = args[1]
        scastka = args[2]
        if vs and scastka:
            regist_token = first_token
            if token==md5(regist_token+vs+scastka).hexdigest():
                try:
                    castka = round(float(scastka), 2)
                except ValueError:
                    castka = 0
                popis = args[5]
                if popis[:14].lower()=='ucast_na_akci_':
                    popis = popis[14:]
                for za_lomitkem in xrange(6, len(args)):
                    popis += '/' + args[za_lomitkem]
                uzivatel = db(db.auth_user.vs==vs).select().first()
                if (castka and popis and uzivatel
                                    and uzivatel.email.lower()==args[3].lower()):
                    akce = args[4] or ''
                    is_valid = True
    return is_valid, castka, popis, uzivatel, akce

def __log_ws(ws): 
    vfp.strtofile( "%s %s %s" % (
      datetime.now().strftime('%d.%m %H:%M'),
      ws, request.url),
      'logs/ws_call.log', 1)

def __log_res(result): 
    vfp.strtofile( " - %s\n\n" % result,
      'logs/ws_call.log', 1)
