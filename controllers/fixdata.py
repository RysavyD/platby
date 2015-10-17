# -*- coding: utf8 -*-

'''TODO:
308 Ludek - dlouho neaktivni - opravit zalohu na 0 (nyni -290 po chybnem prirazeni platby za hosting)
pridat admin prava Marovi a sebrat je Potapkovi
'''

mail_subj = Uc_sa.mail_subj
podpis = Uc_sa.podpis

def err():
    a = 1/0

'''
def nero():
    db.auth_user[1135] = dict(zaloha=960.0)
    db.commit()
    return 'ok'
'''

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

"""
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
    '''pozor, __setvs() zatím neaktualizuje zálohu, je potřeba upravit!'''
    zakaznik = db(db.auth_user.vs==vs).select().first()
    if zakaznik:
        db.pohyb[pohyb_id] = dict(
                    zakaznik=zakaznik.vs, idauth_user=zakaznik.id)
    return zakaznik

# duplicitně převzato do kontroléru prehledy.py
#                     a také do jednorázového scriptu bb.py 
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
        zakaznik.update_record(zaloha=float(zakaznik.zaloha) + float(castka))
        mail.send(zakaznik.email,
            mail_subj % TFu('Připsána záloha ze spolecneaktivity.cz'),
              ('Byla vynulována Tvoje osobní záloha %s Kč na webu Jiřího Poučka spolecenaktivity.cz.\n'
              'O tuto částku byla navýšena Tvoje osobní záloha v účetním systému sdružení,\n'
              'takže bude možné platit i pro spolecneaktivity.cz i pro fungujeme.aspone.cz.\n\n'
              'Další podrobnosti zjištíš přihlášením se do účetního systému sdružení (přihlašovací údaje jsou uvedeny níže).\n'
              'V případě nejasností kontaktuj pokladníka.' % castka)
              + (podpis%zakaznik.email))

def mikruse():
    from datetime import date
    user_id = db.auth_user.insert(nick='mikruse',
            email='',
            vs='XXXXXXX', ss='XXXXXXXX',
            )
    clen_id = db(db.auth_group.role=='člen sdružení').select().first().id 
    auth.add_membership(clen_id, user_id)
    db.clenstvi.insert(user_id=user_id, group_id=clen_id,
                    ode_dne=date(2013,10,XXXXXXXXXX))

def grps():
    db(db.auth_group.role.startswith('user_')).delete()
    db.auth_group[12] = dict(role='clen sdruzeni')
    db.auth_group[42] = dict(role='hlavni organizator')
    del db.auth_group[47]

def addu():
    db.ucet.insert(ucet='221-01', zkratka='BÚj', nazev="Jmění")
    db.ucet.insert(ucet='221-12', zkratka='d12', nazev="Odklad základu daně 2012")
    db.ucet.insert(ucet='221-13', zkratka='d13', nazev="Odklad základu daně 2013")
    db.ucet[26].update_record(zkratka='X-Y')
    db.commit()

def vetrelci():
    for i in xrange(1275, 1286):
        del db.auth_user[i]
    return 'ok'
def xludek():
    db.pohyb[1448] = dict(idauth_user=None)
    db.pohyb[1449] = dict(idauth_user=None)
    return 'ok'

def katar():
    db.auth_user[1251] = dict(zaloha=500.0)

def dalsiucty():
    db.ucet.insert(ucet='379-03', zkratka='Půj', nazev="Jiné závazky (půjčky, např.dotace pokladny)")
    db.ucet.insert(ucet='379-07', zkratka='Půj', nazev="Os.záloha (převod mezi 2 zákazníky)")
    db.ucet.insert(ucet='213', zkratka='Per', nazev="Ceniny (např. permanentky)")
    db.commit()

def dalsiucty2():
    oda = db.ucet.insert(ucet='520', zkratka='OdA', nazev="Osobní náklady (za akce)")
    odv = db.ucet.insert(ucet='523', zkratka='OdV', nazev="Odměny členů vedení (nedaňový)")
    db.ucet.insert(ucet='543', zkratka='>Da', nazev="Poskytnuté dary (nedaňový)")
    db.ucet.insert(ucet='546', zkratka='xPo', nazev="Odpis pohledávky (nedaňový)")
    db.pohyb[3963].update_record(idma_dati=odv)  # Du-šan
    db.pohyb[3964].update_record(idma_dati=oda)  # Manik
    db.pohyb[3965].update_record(idma_dati=oda)  # Mirek Zv.
    db.pohyb[3966].update_record(idma_dati=odv)  # Nerothar
    db.pohyb[3967].update_record(idma_dati=oda)  # Archon (Roman Č.)
    db.pohyb[3968].update_record(idma_dati=odv)  # Effa
    db.pohyb[3969].update_record(idma_dati=odv)  # potapeni.cz
    db.pohyb[3970].update_record(idma_dati=odv)  # Bobo (a předchozí - na OsZ)
    db.pohyb[2048].update_record(idma_dati=oda)  # Timšel (na BÚ)
    db.ucet.insert(ucet='642', zkratka='+Úr', nazev="Výnosové úroky z banky")
    del db.ucet[8]
    del db.ucet[14]
    del db.ucet[15]
    db.commit()

def fa_ucel():
    db.fp[1].update_record(md=10) # náklady akcí
    db.fp[2].update_record(md=10)
    db.fp[3].update_record(md=10)
    db.fp[4].update_record(md=17) # náklady zveřejnění akcí na webu
    db.fp[5].update_record(md=17)
    db.fp[6].update_record(md=17)
    db.fp[7].update_record(md=17)
    db.fp[8].update_record(md=10)
    db.fp[9].update_record(md=10)
    db.fp[10].update_record(md=10)
    db.fp[11].update_record(md=10)
    db.fp[12].update_record(md=11) # provozní náklady
    db.fp[13].update_record(md=10)
    db.fp[14].update_record(md=10)
    db.fp[15].update_record(md=10)
    db.fp[16].update_record(md=17)
    db.fp[17].update_record(md=17)
    db.fp[18].update_record(md=10)
    db.fp[19].update_record(md=10)
    db.fp[20].update_record(md=10)
    db.fp[21].update_record(md=11)
    db.fp[22].update_record(md=17)
    db.fp[23].update_record(md=10)
    db.fp[24].update_record(md=10)
    db.fp[25].update_record(md=17)
    db.fp[26].update_record(md=10)
    db.fp[27].update_record(md=17)
    db.fp[28].update_record(md=10)
    db.fp[29].update_record(md=17)
    db.fp[31].update_record(md=17)
    db.fp[32].update_record(md=17)
    db.fp[33].update_record(md=17)
    db.fp[34].update_record(md=10)
    db.fp[35].update_record(md=17)
    db.fp[36].update_record(md=17)
    db.fp[37].update_record(md=10)
    db.fp[38].update_record(md=17)
    db.fp[39].update_record(md=17)
    db.fp[40].update_record(md=10)
    db.fp[41].update_record(md=10)
    db.fp[42].update_record(md=17)
    db.fp[43].update_record(md=10)
    db.fp[44].update_record(md=10)
    db.fp[45].update_record(md=10)
    db.fp[46].update_record(md=10)
    db.commit()

def fa_data():
    db.pohyb[2923].update_record(fp_id=1, idma_dati=Uc_sa.fp)
    db.fp[1].update_record(uhrazeno=datetime.date(2013, 3, 10))
    db.pohyb[1891].update_record(fp_id=17, idma_dati=Uc_sa.fp)
    db.pohyb[2882].update_record(fp_id=18, idma_dati=Uc_sa.fp)
    db.pohyb[1708].update_record(idma_dati=Uc_sa.zaloha)
    db.pohyb[1716].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[1788].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[1857].update_record(fp_id=23, idma_dati=Uc_sa.fp)
    db.pohyb[1890].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[2926].update_record(fp_id=26, idma_dati=Uc_sa.fp)
    db.pohyb[1916].update_record(fp_id=26, idma_dati=Uc_sa.zaloha)
    db.pohyb[1996].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[2935].update_record(fp_id=28, idma_dati=Uc_sa.fp)
    db.pohyb[2044].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[2089].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[2119].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[4788].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[2328].update_record(idma_dati=Uc_sa.fp)
    db.fp[34].update_record(md=27) # 213 ceniny
    db.pohyb[2297].update_record(fp_id=34, idma_dati=Uc_sa.fp)
    db.pohyb[3284].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[3176].update_record(fp_id=37, idma_dati=Uc_sa.fp)
    db.pohyb[4787].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[3740].update_record(idma_dati=Uc_sa.fp)
    db.pohyb[3556].update_record(fp_id=40, idma_dati=Uc_sa.fp)
    db.pohyb[3621].update_record(fp_id=41, idma_dati=Uc_sa.fp)
    db.pohyb[3865].update_record(idma_dati=Uc_sa.fp)
    db.commit()

def fa_data2():    
    db.pohyb.insert(idma_dati=Uc_sa.zaloha, iddal=1, castka=900.00, datum=datetime.datetime(2013,9,21),
            fp_id=40, popis='ubyt.Mariánskoh.b.,Těžká romantika na konci léta 20-22/9; dopsal mz podle Fa a doplatku')
    # jiné ID, ale bylo už správně// db.pohyb[4925].update_record(idma_dati=27)  # permice
    db.commit()

def fa_konec():
    db.fp[35].update_record(zauctovana=True) # nepřesná platba Jirkovi
    db.fp[36].update_record(zauctovana=True) # snížená platba Jirkovi
    db.commit()

def mikulaska():
    db.pohyb[3021].update_record(idma_dati=Uc_sa.zaloha, fp_id=45)
    db.pohyb[4790].update_record(idma_dati=Uc_sa.zaloha)
    db.commit()

def otevri():
    zaverkovy = db.ucet.insert(ucet='96', zkratka='Záv', nazev="Závěrkový účet (přenos mezi roky)")
    # pasiva
    db.pohyb.insert(idma_dati=zaverkovy, iddal=Uc_sa.oz_sa, castka=101157.00, datum=datetime.datetime(2013, 1, 1))
    db.pohyb.insert(idma_dati=zaverkovy, iddal=25, castka=70500.00, datum=datetime.datetime(2013, 1, 1))
    db.pohyb.insert(idma_dati=zaverkovy, iddal=22, castka=5850.00, datum=datetime.datetime(2013, 1, 1))
    # aktiva
    db.pohyb.insert(iddal=zaverkovy, idma_dati=Uc_sa.pokladna, castka=1340.00, datum=datetime.datetime(2013, 1, 1))
    db.pohyb.insert(iddal=zaverkovy, idma_dati=Uc_sa.bezny, castka=191226.37, datum=datetime.datetime(2013, 1, 1))
    db.pohyb.insert(iddal=zaverkovy, idma_dati=27, castka=20571.00, datum=datetime.datetime(2013, 1, 1))
    db.pohyb.insert(iddal=zaverkovy, idma_dati=21, castka=1400.00, datum=datetime.datetime(2013, 1, 1))
    db.commit()

def koncime():
    db.ucet[29].update(ucet='521-1')
    db.ucet.insert(ucet='521-2', zkratka='OdF', nazev="odměny za výkon funkcí a činností")
    db.ucet[28].update(ucet='521-3')
    vpo = db.ucet.insert(ucet='383', zkratka='VPo', nazev="výdaje příštích období (nedošla faktura)")
    db.fp[45].update(md=vpo)
    db.pohyb.insert(idma_dati=Uc_sa.akce, iddal=vpo, castka=66468.00,
            datum=datetime.datetime(2013, 12, 31), popis="problematický ubytovatel zdržuje vystavení faktury")
    db.commit()

def koncime2():     # oprava předchozího
    db.ucet[29].update_record(ucet='521-1')
    db.ucet[28].update_record(ucet='521-3')
    db.fp[45].update_record(md=35)
    db.commit()

def neznami():
    db.kategorie[19] = dict(vyznam='vynosy: poplatky z osobniho kreditu')
    db.ucet.insert(ucet='379-08', zkratka='Os?', nazev="Chybné a neurčené platby")
    db.commit()

def typp():
    db.typp.insert(zkratka='U', vyznam='ubytování')
    db.typp.insert(zkratka='S', vyznam='sportoviště')
    db.typp.insert(zkratka='K', vyznam='kulturní zařízení')
    db.typp.insert(zkratka='R', vyznam='restaurace')
    db.typp.insert(zkratka='A', vyznam='zajištění akcí ostatní (exkurze,..)')
    db.typp.insert(zkratka='D', vyznam='drobné nákupy/služby')
    db.typp.insert(zkratka='W', vyznam='weby vlastní')
    db.typp.insert(zkratka='I', vyznam='internetové služby (cizí)')
    db.typp.insert(zkratka='T', vyznam='telekomunikace, pošta')
    db.typp.insert(zkratka='P', vyznam='půjčky pro nás (navýšení pokladny)')
    db.typp.insert(zkratka='G', vyznam='státní orgány (FÚ,..)')
    db.typp.insert(zkratka='J', vyznam='jiné')
    db.commit()

def part():
    import csv
    typy = db(db.typp).select()
    with open('partner.csv', 'r') as f:  # os.getcwd()=='web2py'
        for partner in csv.DictReader(f):
            for k, v in partner.items():
                if k:  # je tam totiž navíc prvek s klíčem None
                    partner[k] = unicode(v, encoding='cp1250')
            typ = typy.find(lambda typ: typ.zkratka==partner['typ'])[0].id
            db.partner.insert(idx=int(partner['id']), typp_id=typ, ucel=partner['ucel'], nazev=partner['nazev'],
                    ulice=partner['ulice'], psc=partner['psc'], misto=partner['misto'], ico=partner['ico'])
    db.commit()

def uct():
    db.ucet[11] = dict(ucet='548-01')
    db.ucet.insert(ucet='518-02', zkratka='-Ad', nazev="Náklady akce doplňkové")
    db.ucet.insert(ucet='518-03', zkratka='-Aw', nazev="Náklady zveřejnění akcí na webu")
    db.ucet.insert(ucet='530', zkratka='-DP', nazev="Daně a polatky (kromě daně z příjmu)")
    db.ucet.insert(ucet='548-03', zkratka='-Bp', nazev="Bankovní poplatky")
    db.ucet.insert(ucet='311', zkratka='Fv', nazev="Faktura vydaná (pohledávka)")
    db.ucet.insert(ucet='314', zkratka='Zál', nazev="Záloha (např. na akci)")
    db.ucet.insert(ucet='321', zkratka='Fp', nazev="Faktura přijatá (závazek)")
    db.ucet.insert(ucet='324', zkratka='Záp', nazev="Záloha přijatá")
    db.commit()

def fakt():
    def _dat_txt(strDat):
        try:
            val = datetime.datetime.strptime(strDat, '%d.%m.%Y')
        except:
            val = None
        return val
    import csv
    partneri = db(db.partner).select()
    with open('faktura.csv', 'r') as f:  # os.getcwd()=='web2py'
        for fp in csv.DictReader(f):
            for k, v in fp.items():
                if k:  # možná je tam jako u partnerů navíc prvek s klíčem None?
                    fp[k] = unicode(v, encoding='cp1250')
            try:
                partner = partneri.find(lambda partner: partner.idx==int(fp['idpartner']))[0].id
            except:
                partner = None
            db.fp.insert(idx=int(fp['id']), partner_id=partner, ucet=fp['ucet'], elektronicky=fp['elektronic'],
                    castka=fp['castka'], zaloha=fp['zaloha'], no_jejich=fp['no_jejich'],
                    vystaveno=_dat_txt(fp['vystaveno']), prijato=_dat_txt(fp['prijato']),
                    splatnost=_dat_txt(fp['splatnost']), uhrazeno=_dat_txt(fp['uhrazeno']),
                    uhrada=fp['uhrada'][:1], zal_uhrada=fp['uhrada'][1:2],
                    vs=fp['vs'], ss=fp['ss'], ks=fp['ks'],
                    datum_akce=_dat_txt(fp['datum_akce']), vs_akce=fp['vsakce'],
                    popis=fp['popis'])
    db.commit()

def kaja():
    del db.auth_user[1261]
    db.commit()

def silv2():       # tomas.zemres
    userid = 757 
    zakaznik = 582 
    castka = 50
    db.pohyb[0] = dict(idauth_user=userid, castka=castka,
                          zakaznik=str(zakaznik), popis='přeplatek Silvestr',
                          datum=datetime.datetime(2013,12,31,11),
                          idma_dati=Uc_sa.oz_fu, iddal=Uc_sa.oz)
    clovek = db.auth_user[userid]
    clovek.update_record(zaloha=clovek.zaloha+castka)
    db.commit()

def silv1():        # Chodovar
    userid = 1252
    zakaznik = 80117
    castka = 50
    db.pohyb[0] = dict(idauth_user=userid, castka=castka,
                          zakaznik=str(zakaznik), popis='přeplatek Silvestr',
                          datum=datetime.datetime(2013,12,31,11),
                          idma_dati=Uc_sa.oz_fu, iddal=Uc_sa.oz)
    clovek = db.auth_user[userid]
    clovek.update_record(zaloha=clovek.zaloha+castka)
    db.commit()

def silv0():         # Voi
    userid = 895 
    zakaznik = 444 
    castka = -2750
    db.pohyb[0] = dict(idauth_user=userid, castka=abs(castka),
                          zakaznik=str(zakaznik),
                          popis='přesun pro spolecneaktivity.cz (Silvestr)',
                          datum=datetime.datetime(2013,12,31,11),
                          idma_dati=Uc_sa.oz, iddal=Uc_sa.oz_sa)
    clovek = db.auth_user[userid]
    clovek.update_record(zaloha=clovek.zaloha+castka)
    db.commit()

def odmeny():
    '''
    1) za weby: du-san 4000 (rozděluje: 3000 on, 1000 Manik), mirek zvolsky 1000
    2) za organizacni cinnost: nerothar 1000 (bdm), roman cervenka 1500 (silvestr)
    3) za praci pro sdruzeni: effa 2000, potapeni.cz 2000, bobo 2000. (Rada), Du-san 1000, Nerothar 1000 (dk)
    '''
    odmenu(1070, 269, 4000)  #du-san
    odmenu(1024, 315, 1000)  #manik
    odmenu(992, 347, 1000)   #mirek zv.
    odmenu(1135, 204, 2000)  #nerothar
    odmenu(1082, 257, 1500)  #roman.cervenka
    odmenu(1044, 295, 2000)  #effa
    odmenu(1018, 321, 2000)  #potapeni.cz
    odmenu(1209, 130, 2000)  #bobo
    db.commit()

def odmenu(userid, zakaznik, castka, popis='odměna za práci pro sdružení'):
    db.pohyb[0] = dict(idauth_user=userid, castka=castka,
                          zakaznik=str(zakaznik), popis=popis,
                          datum=datetime.datetime(2013,12,31,10),
                          idma_dati=Uc_sa.odmeny, iddal=Uc_sa.oz)
    clovek = db.auth_user[userid]
    clovek.update_record(zaloha=clovek.zaloha+castka)
    # db.commit() --- potvrzuji v odmeny()

def ucetodm():
    db.ucet[0] = dict(ucet='58', zkratka='Odm', nazev='Poskytnutí příspěvku')
    db.commit()
    
def zavinac():
    auth.del_membership(12, 1238)
    db.clenstvi[41] = dict(do_dne=datetime.date(2013,11,14)) 
    db.commit()

def mp():                   # MisaP vrácení zálohy, pozdě jsem potvrdil vyřízení
    db.zadost[47] = dict(zadano=475, prevedeno=445) 
    db.pohyb[3882] = dict(castka=30)     # poplatek 
    db.auth_user[959] = dict(zaloha=0)   # MisaP 
    db.commit()

def an():                   # AndreaN platba 18.12. bez VS
    manik = db(db.auth_user.vs=='152').select().first()
    manik.update_record(zaloha=manik.zaloha+1000) 
    db.commit()

def tho():
    db.auth_user[1247] = dict(zaloha=0)   # thorndike 
    db.commit()

def svec():
    db.pohyb[3781] = dict(idauth_user=1223)  # vs 116 roger24@post.cz
    manik = db(db.auth_user.vs=='116').select().first()
    manik.update_record(zaloha=manik.zaloha+150) 
    del db.auth_user[1254]   # vs 80119 id 1254 
    db.commit()

def effa2():
    del db.pohyb[3771] 
    manik = db(db.auth_user.vs=='295').select().first()
    manik.update_record(zaloha=manik.zaloha+440) 
    db.commit()

def effa():
    del db.pohyb[3657] 
    del db.pohyb[3658] 
    manik = db(db.auth_user.vs=='295').select().first()
    manik.update_record(zaloha=manik.zaloha+680) 
    db.commit()

def dup147():
    db(db.pohyb.popis=='Ucast_na_akci_Badminton_c.147_v_Letnanech_Badminton_c.147_v_Letnanech').update(
          popis='Ucast_na_akci_Badminton_c.147_v_Letnanech')
    db.pohyb[3001] = dict(popis='badminton č.139')
    db.pohyb[3113] = dict(popis='badminton č.143')
    db.commit()

def manik():
    del db.pohyb[3724] 
    del db.pohyb[3725] 
    del db.pohyb[3726]
    manik = db(db.auth_user.vs=='315').select().first()
    manik.update_record(zaloha=manik.zaloha-900) 
    db.commit()

def sobin():
    db((db.pohyb.id<3676)&(db.pohyb.idorganizator==992)).update(idorganizator=980)
    db.commit()

def odhlasit():
    db.auth_user[811] = dict(neposilat=True, ne_ostatnim=True) # nahoda.nahoda ahostinska@.. 528
    db.auth_user[905] = dict(neposilat=True, ne_ostatnim=True) # Olina 434
    db.auth_user[1140] = dict(neposilat=True, ne_ostatnim=True) # Kikina kristina.h.kudlova@.. 199
    db.auth_user[1203] = dict(neposilat=True, ne_ostatnim=True) # MajkaN aq2o@yahoo.co.uk 136
    db.commit()

def zaloha():
    db(db.auth_user.zaloha<0).update(zaloha=0)
    db.commit()

def katarinka6():
    db.zadost[43] = dict(vyridil_id=992, zadano=100., prevedeno=100.,
                    prevod=datetime.datetime.now())
    db.commit()

def katarinka():
    user_id = db.auth_user.insert(email='katie.vanova@gmail.com',
            nick='katarinka', ss='694')
    auth.add_membership(12, user_id)
    db.clenstvi.insert(group_id=12, user_id=user_id)
    db.commit()

def katarinka2():
    mx = db.auth_user.vs.max()
    last_vs = db(db.auth_user.vs!=vs_default).select(mx).first()[mx]
    new_vs = str(int(last_vs) + 1)
    db(db.auth_user.id==1251).update(vs=new_vs)
    db.commit()

def katarinka3():
    db.pohyb.insert(idauth_user=1251, castka=100, zakaznik='80116', vs='80116',
          ss='694', id_pokynu='z sa.cz', popis="převod ze spolecneaktivity.cz",
          idma_dati=4, iddal=7)
    db.commit()

def katarinka4():
    db.pohyb[3591] = dict(datum=datetime.datetime.now())
    db.commit()

def katarinka5():
    db.pohyb[3148] = dict(zakaznik='80116', idauth_user=1251,)
    db.pohyb[3152] = dict(zakaznik='80116', idauth_user=1251,
                      popis="pro spolecneaktivity.cz")
    db.commit()

def olina():
    auth.del_membership(12, 905)
    db(db.clenstvi.user_id==905).update(do_dne=datetime.date(2013, 5, 19))
    db.commit()

def marek():
    db.pohyb[2982] = dict(ks='33')
    db.pohyb[2983] = dict(ks='30')
    db.pohyb[2955] = dict(ks='33')
    db.commit()

def pavlovi(): 
    del db.pohyb[3507]
    nerothar = db(db.auth_user.vs=='204').select().first()
    nerothar.update_record(zaloha=nerothar.zaloha+150)
    db.commit()

def bdm_1b():  # navýšení zálohy, kterou nepřidalo __setvs()
    __init(80113, 300)  
    __init(301, 150)
    db.commit()
def bdm_1():
    __setvs(3113, 80113) #pozor, __setvs() neaktualizuje zálohu (ke 20.11.)  
    __setvs(3001, 80113)
    __setvs(3000, 301)
    db.commit()

def pepa():
    del db.zadost[35]
    del db.zadost[36]
    db.commit()

def initsil():     # 14.11.2013 změna Silvestra
    for zakaznik in (
          (490, 50),    # zuzanice 
          (257, 50),    # roman.cervenka
          ):
        __init(zakaznik[0], zakaznik[1])  
    db.commit()

def vraceni2():
    db.zadost[33] = dict(vyridil=auth.user_id, zadano=840.0, prevedeno=840.0,
              prevod=datetime.datetime(2013,11,12,17,30))
    db.commit()
def vraceni():
    del db.pohyb[3207]  # soptik106 - 290
    del db.pohyb[3289]  # standa76 - 430
    db(db.auth_user.vs=='290').update(zaloha=0)
    db(db.auth_user.vs=='430').update(zaloha=0)
    db.commit()

def zadost():
    del db.zadost[28]
    db.commit()

def mailx3():
    db.systab[4] = dict(hodnota='1216')
    db.commit()

def mailx2():
    del db.systab[5]
    db.commit()

def tel():
    db(db.auth_user.telefon==None).update(telefon='')
    db(db.auth_user.tel_ver==None).update(tel_ver=False)
    db(db.auth_user.email_ver==None).update(email_ver=False)
    db.commit()

def mailx():
    del db.systab[3]
    db.commit()

def antipavel_1():
    falesne = db((db.pohyb.datum==datetime.date(2013,11,11))&(
              db.pohyb.id_pokynu=='hotov.příjem')).select()
    for falesny in falesne:
        falesny.update_record(datum=datetime.date(2013,11,6))
    db.commit()
    return len(falesne) 

def antikraken_p146():
    falesne = db((db.pohyb.ss=='9182')&(db.pohyb.idma_dati==Uc_sa.oz)).select()
    for falesny in falesne:
        falesny.update_record(popis=falesny.popis +
                  '_Badminton_c.146_v_Letnanech')
    db.commit()
    return len(falesne) 
def antikraken_p147():
    falesne = db((db.pohyb.ss=='9192')&(db.pohyb.idma_dati==Uc_sa.oz)).select()
    for falesny in falesne:
        falesny.update_record(popis=falesny.popis +
                  '_Badminton_c.147_v_Letnanech')
    db.commit()
    return len(falesne) 
                            
def antikraken_pravidelny():
    falesne = db(db.pohyb.popis.like('%_Pravidelny_badminton%')).select()
    for falesny in falesne:
        falesny.update_record(popis=falesny.popis.replace('Pravidelny_b','B',1))
    db.commit()
    return len(falesne) 
                            
def antikraken_143():
    akce = 'Ucast_na_akci_Badminton_c.143_v_Letnanech' 
    falesne = db(db.pohyb.popis==akce).select()
    for falesny in falesne:
        poskozeny = db(db.auth_user.id==falesny.idauth_user).select().first()
        poskozeny.update_record(zaloha=poskozeny.zaloha + falesny.castka)
    db(db.pohyb.popis==akce).delete()
    db.commit()
    return str(len(falesne))
def antikraken_145():
    akce = 'Ucast_na_akci_Badminton_c.145_v_Letnanech' 
    falesne = db(db.pohyb.popis==akce).select()
    for falesny in falesne:
        poskozeny = db(db.auth_user.id==falesny.idauth_user).select().first()
        poskozeny.update_record(zaloha=poskozeny.zaloha + falesny.castka)
    db(db.pohyb.popis==akce).delete()
    db.commit()
    return str(len(falesne))
def antikraken_144():
    akce = 'Ucast_na_akci_Badminton_c.144_v_Letnanech' 
    falesne = db(db.pohyb.popis==akce).select()
    for falesny in falesne:
        poskozeny = db(db.auth_user.id==falesny.idauth_user).select().first()
        poskozeny.update_record(zaloha=poskozeny.zaloha + falesny.castka)
    db(db.pohyb.popis==akce).delete()
    db.commit()
    return str(len(falesne))

def ucty_1():
    db.ucet.insert(ucet='640', zkratka='+Pr', nazev="výnosy ostatní")    #id=13
    db.ucet.insert(ucet='XXX', zkratka='<Vr', nazev="vrácené os.zálohy") #id=14
    db.commit()

def oprav_zadosti_1():
    db.zadost[1] = dict(prevod=datetime.datetime(2013, 10, 15, 22),
         zadano=570, prevedeno=570) # Du-šan - 269   
    db.zadost[2] = dict(prevod=datetime.datetime(2013, 10, 15, 22),
         zadano=2863, prevedeno=2863, ss=347) # Du-šan -> Mirek Zv. - 347    
    db.zadost[3] = dict(prevod=datetime.datetime(2013, 10, 15, 22),
         zadano=613, prevedeno=613) # petan1961 - 464   
    db.zadost[4] = dict(prevod=datetime.datetime(2013, 10, 15, 22),
         zadano=1292, prevedeno=1292,
         zadost=datetime.datetime(2013, 10, 15, 12)) # Bobo - 130   
    db.zadost[5] = dict(prevod=datetime.datetime(2013, 10, 15, 22),
         zadano=80, prevedeno=80, ss=204,
         zadost=datetime.datetime(2013, 10, 15, 12)) # Manik -> Nerothar - 204   
    db.zadost[0] = dict(typ=1, zadano=445, prevedeno=445, ss=295,
         zadost=datetime.datetime(2013, 10, 15, 12),
         prevod=datetime.datetime(2013, 10, 15, 22)) # ?   
    db.zadost[0] = dict(typ=1, zadano=795, prevedeno=795, ss=321,
         zadost=datetime.datetime(2013, 10, 15, 12),
         prevod=datetime.datetime(2013, 10, 15, 22)) # ?   
    db.zadost[0] = dict(typ=1, zadano=370, prevedeno=370, ss=456,
         zadost=datetime.datetime(2013, 10, 15, 12),
         prevod=datetime.datetime(2013, 10, 15, 22)) # ? hanah?  
    db.zadost[0] = dict(typ=1, zadano=1300, prevedeno=1300, ss=657,
         zadost=datetime.datetime(2013, 10, 15, 12),
         prevod=datetime.datetime(2013, 10, 15, 22)) # ?   
    db.zadost[0] = dict(typ=1, zadano=1005, prevedeno=1005, ss=168,
         zadost=datetime.datetime(2013, 10, 17, 12),
         prevod=datetime.datetime(2013, 10, 17, 22)) # ?   
    db.zadost[0] = dict(typ=1, zadano=400, prevedeno=400, ss=438,
         zadost=datetime.datetime(2013, 10, 25, 12),
         prevod=datetime.datetime(2013, 10, 25, 22)) # ?   
    db.zadost[0] = dict(typ=1, zadano=400, prevedeno=400, ss=130,
         zadost=datetime.datetime(2013, 10, 25, 12),
         prevod=datetime.datetime(2013, 10, 25, 22)) # ? znova Bobo ????  
    db.zadost[6] = dict(prevod=datetime.datetime(2013, 10, 31, 22),
         zadano=816, prevedeno=816) # misulino - 221   
    db.zadost[7] = dict(prevod=datetime.datetime(2013, 10, 31, 22),
         zadano=637, prevedeno=637) # Manik - 315   
    db.zadost[0] = dict(typ=1, zadano=463, prevedeno=463, ss=200,
         zadost=datetime.datetime(2013, 10, 31, 21),
         prevod=datetime.datetime(2013, 10, 31, 23)) # Andrea B. - 200  
    db.zadost[8] = dict(prevod=datetime.datetime(2013, 11, 1, 22),
         zadano=299, prevedeno=299) # Ladik21 - 113   
    db.zadost[10] = dict(prevod=datetime.datetime(2013, 11, 4, 12),
         zadano=412, prevedeno=412) # mnovy - 469   
    db.zadost[11] = dict(prevod=datetime.datetime(2013, 11, 4, 12),
         zadano=145, prevedeno=145) # PetrK - 255   
    db.zadost[12] = dict(prevod=datetime.datetime(2013, 11, 4, 12),
         zadano=290, prevedeno=290) # alicilka - 391   
    db.zadost[13] = dict(prevod=datetime.datetime(2013, 11, 4, 12),
         zadano=80, prevedeno=80) # T0m4s - 296   
    db.zadost[14] = dict(prevod=datetime.datetime(2013, 11, 6, 12),
         zadano=180, prevedeno=180) # tomas.zemres - 582   
    db.zadost[15] = dict(prevod=datetime.datetime(2013, 11, 6, 12),
         zadano=440, prevedeno=440) # KED - 361
    db.zadost[9] = dict(prevod=datetime.datetime(2013, 11, 6, 12),
         zadano=500, prevedeno=500, ss=675) # T0m4s -> Pavlína H. 80113-675    
    db.zadost[16] = dict(prevod=datetime.datetime(2013, 11, 8, 12),
         zadano=316, prevedeno=316) # nijel - 114   
    db.zadost[0] = dict(typ=1, ss=290,
         zadost=datetime.datetime(2013, 11, 8, 12)) # soptik106 - 290  
    db.zadost[0] = dict(typ=2, ss=290,
         zadost=datetime.datetime(2013, 11, 8, 12)) # soptik106 - 290  
    db.commit()

def oprav_zadosti_2():
    pavlina = db(db.auth_user.vs=='80113').select().first()
    if not pavlina.ss:    # Pavlína nemá vyplněno ss, nenajde se podle zadost.ss
        pavlina.update_record(ss='675')   
    zadosti = db(db.zadost.id>0).select(
            db.zadost.ALL, db.auth_user.ALL,
            left=db.auth_user.on(db.auth_user.ss==db.zadost.ss))
    for zadost in zadosti:
        db.zadost[zadost.zadost.id] = dict(idauth_user=zadost.auth_user.id,
                                      vs=zadost.auth_user.vs)
    db.commit()

    Manik/MyNick 315
    mikruse 677
    petan1961 464 petan1961@seznam.cz 
    potapeni.cz 321 f.pudil@seznam.cz
    olina 434 olina.krajska@seznam.cz
    //převedla se jako janine// jvapenikova 540 jvapenikova@seznam.cz
    nerothar 204 pav.dufek@atlas.cz
    ----asi odpovídá zrušeným:
    zr55 22.07.2011
    zr71 28.07.2011
    zr72 06.08.2012
    zr73 16.11.2011
    NEDOŘEŠENO:
    evikd 243 - nelze schválit v Jirkově evidenci - poslán mail/vzkaz 
    katarinka 694 - zatím ji nemáme v evidenci - poslán vzkaz
    mikruse 677 - zatím ji nemáme v evidenci - poslán vzkaz
    nevíme od kdy: petan, potápka, olina, nerothar
    olina asi vystoupila na vlastní žádost 

def oprav_clenove_1():
    auth.add_membership(12, 1024)  # Manik/MyNick 315
    auth.add_membership(12, 1135)  # Nerothar 204
    auth.add_membership(12, 875)   # petan1961 464
    auth.add_membership(12, 1018)  # potapeni.cz 321
    auth.add_membership(12, 905)   # olina 434
    auth.add_membership(12, 1096)  # evikd 243
    db.clenstvi.insert(user_id=1024, group_id=12,
                    ode_dne=datetime.date(2012,3,20))
    db.clenstvi.insert(user_id=1135, group_id=12)
    db.clenstvi.insert(user_id=875, group_id=12)
    db.clenstvi.insert(user_id=1018, group_id=12)
    db.clenstvi.insert(user_id=905, group_id=12)
    db.clenstvi.insert(user_id=1096, group_id=12,
                    ode_dne=datetime.date(2013,11,1))
    db.commit()

def init9():     # 8.11.2013
    for zakaznik in (
          (114, 316),    # nijel 
          ):
        __init(zakaznik[0], zakaznik[1])  
    db.commit()

# python web2py.py -M -S platby/fixdata/oprav_fio_1
def oprav_fio_1():
    from import_fio_sa import import_pohyby_sa
    import_pohyby_sa(db, od='2013-11-05', do='2013-11-08')

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
"""

#if __name__=='__main__':
#    antikraken()
