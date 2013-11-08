# -*- coding: utf8 -*-

mail_subj = Uc_sa.mail_subj
podpis = Uc_sa.podpis

'''zatím nedořešené pohyby:
chybná platba:
(748,),24.2. 3000
(630,),16.1. 300

vrácené přeplatky dodavatelům:
(1675,),18.12. 5984
(1416,),26.9. 675

úroky:
(1600,),30.11. 3.93
(1520,),31.10. 7.31

příspěvky:
(62,),16.6. 20

proplacená faktura:
(1636,),11.12. 366
(1555,),16.11. 2700
'''


def setnick():
    '''doplní zákazníka pohybu podle nicku; nemění zálohu'''
    if len(request.args)==2:
        zakaznik = db(db.auth_user.nick==request.args[1]).select().first()
        if zakaznik:
            db.pohyb[request.args[0]] = dict(
                        zakaznik=zakaznik.vs, idauth_user=zakaznik.id)
            db.commit()
            return (zakaznik.vs, zakaznik.nick)
def setvs():
    '''doplní zákazníka pohybu podle vs; nemění zálohu'''
    if len(request.args)==2:
        zakaznik = __setvs(request.args[0], request.args[1])
        if zakaznik:
            db.commit()
            return (zakaznik.vs, zakaznik.nick)

def __setvs(pohyb_id, vs):
    zakaznik = db(db.auth_user.vs==vs).select().first()
    if zakaznik:
        db.pohyb[pohyb_id] = dict(
                    zakaznik=zakaznik.vs, idauth_user=zakaznik.id)
    return zakaznik

def __init(vs, castka):
    zakaznik = db(db.auth_user.vs==vs).select().first()
    if zakaznik:
        db.pohyb.insert(
              idauth_user=zakaznik.id,
              castka=castka,
              idma_dati=Uc_sa.oz_sa,
              iddal=Uc_sa.oz,
              datum=datetime.datetime.now(),
              popis="převod ze spolecneaktivity.cz",
              zakaznik=vs,
              vs=vs,
              ss=vs,
              id_pokynu='z sa.cz'
              )
        zakaznik.update_record(zaloha=zakaznik.zaloha + castka)
        mail.send(zakaznik.email,
            mail_subj % TFu('Připsána záloha ze spolecneaktivity.cz'),
              ('Byla vynulována Tvoje osobní záloha %s Kč na webu Jiřího Poučka spolecenaktivity.cz.\n'
              'O tuto částku byla navýšena Tvoje osobní záloha v účetním systému sdružení,\n'
              'takže bude možné platit i pro spolecneaktivity.cz i pro fungujeme.aspone.cz.\n\n'
              'Další podrobnosti zjištíš přihlášením se do účetního systému sdružení (přihlašovací údaje jsou uvedeny níže).\n'
              'V případě nejasností kontaktuj pokladníka.' % castka)
              + (podpis%zakaznik.email))

def mikruse():
    pass
    # zadost Pavlina H.
    # doregistrovat mikruse

'''
def clenove():     # selhalo: mikruse MyNick Zrušený 71 Zrušený 72 Zrušený 73
    nicky = ''
    auth.add_group('předseda', '')
    auth.add_group('dočasný předseda', '')
    auth.add_group('člen rady', '')
    auth.add_group('dozorčí komise', '')
    auth.add_group('pokladník', '')
    clen_id = auth.add_group('člen sdružení', '')
    
    from bs4 import BeautifulSoup
    import urllib2
    url = 'file:///' + os.path.join(os.getcwd(), request.folder, 'clenove.htm')
    html = unicode(urllib2.urlopen(url).read(), 'utf8')
    soup=BeautifulSoup(html)
    clenove = soup('table')[5].tbody.find_all('tr')
    for clen in clenove:
        udaje = clen.find_all('td')
        nick = udaje[0].string.strip()
        usr = db(db.auth_user.nick==nick).select().first()
        if usr:
            user_id = usr.id
        else:
            nicky += nick + ' '
            continue
        od_str=udaje[2].string.strip()
        od_datetime=datetime.datetime.strptime(od_str, '%d.%m.%Y')
        od = datetime.date(od_datetime.year, od_datetime.month, od_datetime.day)
        auth.add_membership(clen_id, user_id)
        db.clenstvi.insert(user_id=user_id, group_id=clen_id, ode_dne=od)
    db.commit()
    return nicky.strip()   # selhalo zařazení

def setfalse():
    db(db.auth_user).update(ne_ostatnim=False)
    db.commit()

def init8():     # 4.11.2013
    for zakaznik in (
          (582, 180),    # tomas.zemres 
          (361, 440),    # KED
          (80113, 500),  # Pavlína H. (675)
          ):
        __init(zakaznik[0], zakaznik[1])  
    db.commit()

def init7():     # 4.11.2013
    for zakaznik in (
          (469, 412),  # mnovy
          (296, 80),   # T0m4s
          (255, 145),  # PetrK
          (391, 290),  # alicilka
          ):
        __init(zakaznik[0], zakaznik[1])  
    db.commit()

def init6():     # 1.11.2013 Ladik21
    for zakaznik in (
          (113, 299),
          ):
        __init(zakaznik[0], zakaznik[1])  
    db.commit()

def init5():     # 31.10.2013 Andrea B.
    for zakaznik in (
          (200, 463),
          ):
        __init(zakaznik[0], zakaznik[1])  
    db.commit()

def neposilat():
    db(db.auth_user).update(neposilat=False)
    db.commit()

def init4():     # 31.10.2013
    for zakaznik in (
          (315, 637),
          (221, 816),
          ):
        __init(zakaznik[0], zakaznik[1])  
    db.commit()

def init3():     # 25.10.2013
    for zakaznik in (
          (130, 400),
          (438, 400),
          ):
        __init(zakaznik[0], zakaznik[1])  
    db.commit()

def fix6():
    db.ucet[1].update_record(zkratka='Pok')
    db.ucet[2].update_record(zkratka='BÚ')
    db.ucet[3].update_record(zkratka='Dar')
    db.ucet[4].update_record(zkratka='Sa')
    db.ucet[5].update_record(zkratka='>Sa')
    db.ucet[6].update_record(zkratka='Fu')
    db.ucet[7].update_record(zkratka='OsZ')
    db.ucet[8].update_record(zkratka='xxx')
    db.ucet[9].update_record(zkratka='Org')
    db.ucet[10].update_record(zkratka='-Ak')
    db.ucet[11].update_record(zkratka='-Pr')
    db.ucet[12].update_record(zkratka='+Ak')
    db.commit()

def mz1():
    ja = db(db.auth_user.vs=='347').select().first()
    ja.update_record(zaloha=ja.zaloha+1)
    del db.pohyb[3046]
    db.commit()

def init2():     # 17.10.2013
    for zakaznik in (
          (168, 1005),
          ):
        __init(zakaznik[0], zakaznik[1])  
    db.commit()

def fix5():
    db(db.auth_user.vs=='115').update(zaloha=0.0)
    db(db.pohyb.id==3033).update(idma_dati=Uc_sa.oz_sa)
    db.commit()

def init1():     # 15.10.2013
    for zakaznik in (
          (347, 2863),
          (130, 1292),
          (204, 80),
          (269, 570),
          (295, 445),
          (321, 795),
          (464, 613),
          (456, 370),
          (657, 1300),
          ):
        __init(zakaznik[0], zakaznik[1])  
    db.commit()

def neznami():
    for pohyb in (
          (2283,650),
          (2278,121),
          (2246,603),
          (2165,650),
          (2141,650),
          (1972,396),
          (1955,115),
          (1951,128),
          (1939,577),
          (1933,121),
          (1894,538), #id=801
          (1878,496),
          (1833,590),
          (1821,488),
          (1813,592),
          (1786,602),
          (1727,455),
          (1705,539), #id=800
          (1662,488),
          (1652,567),
          (1442,108),
          (1420,180),
          (1388,115),
          (1374,440),
          (1332,446),
          (1321,424),
          (1265,463), #id=876
          (1215,455),
          (1205,478),
          (1150,155),
          (1005,410),
          (873,372),
          (857,223),
          (848,312),
          (795,321),
          (763,322),
          (664,154),
          (602,348),
          (582,308),
          (548,342),
          (449,186),
          (438,320),
          (427,314),
          (396,304),
          (284,223),
          (252,223),
          (216,200),
          (184,135),
          (179,212),
          (173,220),
          (145,135),
          (141,167),
          (140,167),
          (124,186),
          (20,135),
          (4,108),
          ):
        __setvs(pohyb[0], pohyb[1])
    db.commit()

def adm():
    from mzw2p import add_to_group 
    for user_id in (1209, 1018, 1070, 1044, 1135, 992):
        add_to_group(db, user_id)
    add_to_group(db, 992, role='pokladna')
    db.commit()
    return 'rada,DK,mz přidáni do admin, mz do pokladna'

def fix4():
    db.pohyb[2361] = dict(idauth_user=849)   # vs=490
    db.pohyb[2362] = dict(idauth_user=919)   # vs=420
    db.pohyb[2363] = dict(idauth_user=1082)  # vs=257
    db.commit()
    return 'pohyb.id=2361..2363 doplněn uživatel'

def fix3():
    db(db.pohyb.iddal==Uc_sa.oz_vy).update(iddal=Uc_sa.oz)
    db.commit()
    return '379-99 -> 379-09'

from import_sa_pokladna import import_sa_pokladna 
def pokladna():
    import_sa_pokladna(db)
    return 'hotovo'

def fix2():
    db.ucet.insert(ucet='548-03', nazev='náklady provozní')
    db.ucet.insert(ucet='602', nazev='výnosy za akce')
    db.commit()
    return 'účty 548-03, 602'

def fix1():
    db.ucet.insert(ucet='379-99', nazev='os.záloha/výnos (z hotov.příjmů)')
    db.ucet.insert(ucet='211-01', nazev='pokladna u organizátorů')
    db.ucet.insert(ucet='518-01', nazev='náklady akcí')
    db(db.auth_user).update(organizator=False)
    db(db.auth_user.vs=='111').update(vs='80111')
    db.commit()
    return 'Pepa-změněn VS 111->80111, iniciováno Organizator->False, účty 379-99, 211-01, 518-01'

def init_systab():
    db.systab.update_or_insert(db.systab.kod=='last_csv',
            kod='last_csv', hodnota='29.09.2013')
    db.systab.update_or_insert(db.systab.kod=='csv_czk',
            kod='csv_czk', hodnota='125197.60')
    db.commit()
    return 'systab: nastaveno'
'''
