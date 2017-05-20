# coding: utf8

import datetime
from collections import defaultdict

@auth.requires_membership('vedeni')
def obdobi():
    volba_obdobi = '<table>'
    for rok in xrange(datetime.date.today().year, 2010, -1):
        volba_obdobi += '<tr><td><a href="%s"><b>%s</b></a></td>' % (
                    URL('zaverka', args=(rok, 1, 12)),
                    rok)
        for mesic in range(1, 13, 3):
            volba_obdobi += '<td><a href="%s"><small> %s-%s</small></a></td>' % (
                    URL('zaverka', args=(rok, mesic, mesic+2)),
                    mesic, mesic+2)
        volba_obdobi += '</tr>'
    volba_obdobi += '</table>'
    return dict(volba_obdobi=volba_obdobi)

@auth.requires_membership('vedeni')
def zaverka():
    if len(request.args)<3:
        session.flash = TFu("nesprávné parametry volání")
        redirect(URL('obdobi'))
    rok = int(request.args[0])
    mesic_od = int(request.args[1])
    den_od = datetime.date(rok, mesic_od, 1)
    mesic_do = int(request.args[2])
    den_po = datetime.date(rok+1, 1, 1) if mesic_do>=12 else datetime.date(rok, mesic_do+1, 1)

    # součtování podle druhů pohybu
    md = db.ucet.with_alias('md')
    dal = db.ucet.with_alias('dal')
    pocet = db.pohyb.id.count()
    suma = db.pohyb.castka.sum()
    skupiny = db((db.pohyb.datum>=den_od) & (db.pohyb.datum<den_po)
            ).select(db.pohyb.idma_dati, db.pohyb.iddal,
            md.ucet, dal.ucet, db.kategorie.vyznam, pocet, suma,
            left=[md.on(md.id==db.pohyb.idma_dati),
                dal.on(dal.id==db.pohyb.iddal),
                db.kategorie.on((db.kategorie.idma_dati==db.pohyb.idma_dati) & (db.kategorie.iddal==db.pohyb.iddal))],
            groupby=[db.pohyb.idma_dati, db.pohyb.iddal])

    ucty_dict = osnova()

    need_commit = False
    ucty = {}
    protistrana = {}
    for skupina in skupiny:
        # aktualizovat 'kategorie' (druhy pohybů) o dosud nezaznamenané druhy pohybů
        if skupina.kategorie.vyznam==None:
            if skupina.pohyb.idma_dati==None or skupina.pohyb.iddal==None:
                # mám problém, že se nepřipojily záznamy None/platný, platný/None, a dokud to neumím udělat lépe,
                # musím znova zkontrolovat, že v kategoriích nejsou, aby se tam nemnožily
                kategorie = db((db.kategorie.idma_dati==skupina.pohyb.idma_dati) & (db.kategorie.iddal==skupina.pohyb.iddal)
                            ).select(db.kategorie.vyznam)
                if len(kategorie):
                    skupina.kategorie.vyznam = kategorie.first().vyznam
                    continue
            db.kategorie.insert(idma_dati=skupina.pohyb.idma_dati, iddal=skupina.pohyb.iddal)
            need_commit = True

        # podle účtů
        ucty[skupina.md.ucet] = ucty.get(skupina.md.ucet, 0) + skupina[suma]
        if protistrana.get(skupina.md.ucet) is None:
            protistrana[skupina.md.ucet] = {}
        protistrana[skupina.md.ucet][skupina.dal.ucet] = protistrana[skupina.md.ucet].get(skupina.dal.ucet, 0) - skupina[suma]

        ucty[skupina.dal.ucet] = ucty.get(skupina.dal.ucet, 0) - skupina[suma]
        if protistrana.get(skupina.dal.ucet) is None:
            protistrana[skupina.dal.ucet] = {}
        protistrana[skupina.dal.ucet][skupina.md.ucet] = protistrana[skupina.dal.ucet].get(skupina.md.ucet, 0) + skupina[suma]

    if need_commit:
        db.commit()

    naklady = vynosy = 0
    for ucet_cislo, ucet_castka in ucty.items():
        if ucet_cislo:
            if ucet_cislo[0]=='5':
                naklady += ucet_castka
            elif ucet_cislo[0]=='6':
                vynosy -= ucet_castka

    return dict(rok=rok, mesic_od=mesic_od, mesic_do=mesic_do,
            den_od=den_od.strftime('%Y%m%d'), den_po=den_po.strftime('%Y%m%d'),
            skupiny=skupiny, pocet=pocet, suma=suma,
            ucty=ucty, ucty_dict=ucty_dict, protistrana=protistrana,
            naklady=naklady, vynosy=vynosy)

@auth.requires_membership('vedeni')
def prubezne():
    from mz_wkasa_platby import Uc_sa

    def ucty_init(ucty, ucet_id):
        ucty[ucet_id]['stav'] = {}
        ucty[ucet_id]['pohyb'] = {}
        ucty[ucet_id]['md'] = {}
        ucty[ucet_id]['dal'] = {}
        pohyb = ucty[ucet_id]['pohyb']
        md = ucty[ucet_id]['md']
        dal = ucty[ucet_id]['dal']
        stav = ucty[ucet_id]['stav']
        for rok in xrange(2010, letos + 1): # 2010: i pro 2011 vypisujeme předchozí
            pohyb[rok] = 0
            md[rok] = 0
            dal[rok] = 0
            stav[rok] = 0

    letos = datetime.date.today().year
    ucty_rows = db(db.ucet).select()
    ucty = {}

    ucty[0] = {}
    ucty[0]['ucet'] = '?'
    ucty[0]['nazev'] = '<neurčeno>'
    ucty_init(ucty, 0)
    ucty[-1] = {} # ZAL=osobní zálohy (z pohybů)
    ucty[-1]['ucet'] = 'ZAL'  # musí být vyplněno, je to klíč pro třídění
    ucty[-1]['nazev'] = 'závazek: osobní zálohy neumístěné na akce (z pohybů)'
    ucty_init(ucty, -1)

    for ucet in ucty_rows:
        ucty[ucet.id] = {}
        ucty[ucet.id]['ucet'] = ucet.ucet
        ucty[ucet.id]['nazev'] = ucet.nazev
        ucty_init(ucty, ucet.id)

    kredit_pohyb = {}  # zákaznické zálohy podle pohybů
    kredit_soucet = {}
    for rok in xrange(2010, letos + 1): # 2010: i pro 2011 vypisujeme předchozí
        kredit_pohyb[rok] = kredit_soucet[rok] = 0

    pohyby = db(db.pohyb).select(orderby=db.pohyb.datum)
    kasa = 0
    zapor = False
    chybi = ''
    pod = 0
    for pohyb in pohyby:
        # kontrola, zda pokladna není v záporu
        if pohyb.idma_dati==Uc_sa.pokladna:
            kasa += pohyb.castka
            if zapor and kasa>=0:
                zapor = False
                chybi += ' - %s - Kč %s<br />' % (pohyb.datum.strftime('%d.%m.%Y'), -pod)
                pod = 0
        elif pohyb.iddal==Uc_sa.pokladna:
            kasa -= pohyb.castka
            pod = min((pod, kasa))
            if not zapor and kasa<0:
                zapor = True
                chybi += pohyb.datum.strftime('%d.%m.%Y')

        rok = pohyb.datum.year
        ucty[pohyb.idma_dati or 0]['md'][rok] += pohyb.castka
        ucty[pohyb.iddal or 0]['dal'][rok] += pohyb.castka
        ucty[pohyb.idma_dati or 0]['pohyb'][rok] += pohyb.castka
        ucty[pohyb.iddal or 0]['pohyb'][rok] -= pohyb.castka
        if pohyb.idauth_user:
            if pohyb.idma_dati in Uc_sa.gl_ozwk:  # OsZ, >SA
                ucty[-1]['md'][rok] += pohyb.castka
                ucty[-1]['pohyb'][rok] -= pohyb.castka
            if pohyb.iddal in Uc_sa.gl_ozwk:
                ucty[-1]['dal'][rok] += pohyb.castka
                ucty[-1]['pohyb'][rok] += pohyb.castka

    if zapor:  # dotisk načatého řádku
        chybi += ' - %s - Kč %s<br />' % (pohyb.datum.strftime('%d.%m.%Y'), -pod)

    for rok in xrange(2011, letos + 1):
        for rok_b in xrange(2011, rok + 1):
            for ucet in ucty:
                ucty[ucet]['stav'][rok] += ucty[ucet]['pohyb'][rok_b]

    soucet = db.auth_user.zaloha.sum()
    zaloha_ted = db().select(soucet).first()[soucet]

    return dict(ucty=ucty,
        chybi = chybi,
        od_roku=request.args(0) or letos,
        zaloha_zakaznik=zaloha_ted  # < ucty[-1=ZAL], dokud vrácení záloh (None/221) není určeno
        )

@auth.requires_membership('vedeni')
def osnova():
    return dict(ucty = db(db.ucet).select(orderby=db.ucet.ucet))

@auth.requires_membership('vedeni')
def dp():
    def zapis_mesice(akt_rok, akt_mesic, dne, ziskano, ziskano_mesice):
        '''přelité osobní zálohy po měsících
        '''
        if (dne is None) or pohyb.datum.month!=akt_mesic or pohyb.datum.year!=akt_rok:
            if dne is None:
                dnes = datetime.date.today()
                akt_rok = dnes.year
                akt_mesic = dnes.month
            ziskano_mesice.append((akt_rok, akt_mesic, ziskano))
            if dne is not None:
                akt_rok = dne.year
                akt_mesic = dne.month
        return akt_rok, akt_mesic

    preklenovaci_ucet = db(db.ucet.ucet=='702').select().first().id
    #preklenovaci_ucet_2 = db(db.ucet.ucet=='701').select().first().id   # 3.2017 zatím všude nechávám 702
    permice_ucet = db(db.ucet.ucet=='213').select().first().id
    vynosy_akci_ucet = db(db.ucet.ucet=='602').select().first().id
    fungujeme_ucet = db(db.ucet.ucet=='379-12').select().first().id

    expr_max = db.pohyb.datum.max()
    iniciovano_ke_dni = db((db.pohyb.idma_dati==preklenovaci_ucet)|(db.pohyb.iddal==preklenovaci_ucet)).select(expr_max).first()[expr_max]
    if iniciovano_ke_dni is None:
        expr_min = db.pohyb.datum.min()
        iniciovano_ke_dni = db().select(expr_min).first()[expr_min]
        if iniciovano_ke_dni is None:
            iniciovano_ke_dni = datetime.date.today()
    iniciovany_rok = iniciovano_ke_dni.year
    k_datu_default = min(datetime.date(iniciovany_rok, 12, 31), datetime.date.today())

    fungujeme = db((db.pohyb.datum>=iniciovano_ke_dni) & ((db.pohyb.idma_dati==fungujeme_ucet) | (db.pohyb.iddal==fungujeme_ucet))).select(orderby=db.pohyb.datum)
    akt_rok = iniciovano_ke_dni.year
    akt_mesic = iniciovano_ke_dni.month
    ziskano = 0
    ziskano_mesice = []
    prevedeno = 0
    prevedeno_dne = None
    for pohyb in fungujeme:
        akt_rok, akt_mesic = zapis_mesice(akt_rok, akt_mesic, pohyb.datum, ziskano, ziskano_mesice)
        if pohyb.iddal==fungujeme_ucet:
            ziskano += pohyb.castka
        elif pohyb.iddal==vynosy_akci_ucet:
            prevedeno += pohyb.castka
            prevedeno_dne = pohyb.datum
        else:
            ziskano -= pohyb.castka
    else:
        zapis_mesice(akt_rok, akt_mesic, None, ziskano, ziskano_mesice)
    lze_vynosy = int(round(ziskano-prevedeno))

    permice_in = db((db.pohyb.datum>=iniciovano_ke_dni) & (db.pohyb.idma_dati==permice_ucet)).select(orderby=db.pohyb.datum)
    permice_out = db((db.pohyb.datum>=iniciovano_ke_dni) & (db.pohyb.iddal==permice_ucet)).select(orderby=db.pohyb.datum)
    permice_max = 0
    out_celkem = out_do_rozhodneho = 0
    for permice in permice_out:
        permice_max -= permice.castka
        out_celkem += permice.castka
        if datetime.date(permice.datum.year, permice.datum.month, permice.datum.day)<=k_datu_default:
            out_do_rozhodneho += permice.castka
    if auth.has_membership('pokladna'):
        inputy = [Field('zavrit', 'boolean', default=False, label='uzavřít', comment="zapsat převáděcí účet 702/701 do databáze?"),
                Field('zapsat', 'boolean', default=False, label='zapsat', comment="fyzicky zapsat změny 213 a 602 do databáze?")]
    else:
        inputy = []
    inputy.append(Field('k_datu', 'date', default=k_datu_default, label='ke dni'))
    inputy.append(Field('do_vynosu', 'integer', default=lze_vynosy, label='do výnosů'))
    prednastaveno = 0
    for idx, permice in enumerate(permice_in):
        # snížit default hodnoty pro -in textboxy
        if out_do_rozhodneho>permice.castka:
            nastavit = 0
            out_do_rozhodneho -= permice.castka
        else:
            nastavit = permice.castka - out_do_rozhodneho
            out_do_rozhodneho = 0
        nastavit = int(round(nastavit))
        prednastaveno += nastavit
        permice_max += permice.castka
        inputy.append(Field('permice%s'%idx,
                label="Ponechat na perm.",
                comment='z původních %s (%s)' % (int(round(permice.castka)), permice.datum.strftime('%d.%m.%Y')),
                default=nastavit))

    problem = ''
    form = SQLFORM.factory(*inputy)
    if form.process().accepted:
        ucty = {}    # podv.ucet -> id
        ucty2 = {} # id -> podv.ucet
        ucty_rows = db(db.ucet).select()
        for ucty_row in ucty_rows:
            ucty[ucty_row.ucet] = ucty_row.id
            ucty2[ucty_row.id] = ucty_row.ucet
        scitadlo = defaultdict(lambda :[0,0,0])
        scitadlo2 = defaultdict(lambda :[0,0,0])
        if form.vars.do_vynosu>lze_vynosy:
            problem = 'NELZE - výnosy: %s > %s' % (form.vars.do_vynosu, lze_vynosy)
        else:
            zustatek_permic = 0
            for idx in xrange(500):
                zustatek_jedne = form.vars.get('permice%s' % idx)
                if zustatek_jedne is None:
                    break
                zustatek_permic += int(zustatek_jedne or 0)
            if zustatek_permic>permice_max:
                problem = 'NELZE - permanentky: %s > %s' % (zustatek_permic, int(round(permice_max)))
            elif prednastaveno>zustatek_permic:
                castka = prednastaveno-zustatek_permic
                if form.vars.zapsat:
                    db.pohyb.insert(idma_dati=ucty['518-01'], iddal=ucty['213'], datum=form.vars.k_datu, castka=castka)
                else:
                    scitadlo['213'] = [scitadlo['213'][0], scitadlo['213'][1]+castka, scitadlo['213'][2]-castka]
                    scitadlo['518'] = [scitadlo['518'][0]+castka, scitadlo['518'][1], scitadlo['518'][2]+castka]
                    scitadlo2['213'] = [scitadlo2['213'][0], scitadlo2['213'][1]+castka, scitadlo2['213'][2]-castka]
                    scitadlo2['518-01'] = [scitadlo2['518-01'][0]+castka, scitadlo2['518-01'][1], scitadlo2['518-01'][2]+castka]
        if problem:
            response.flash = problem
        else:
            if form.vars.do_vynosu:
                castka = form.vars.do_vynosu
                if form.vars.zapsat:
                    db.pohyb.insert(idma_dati=ucty['379-12'], iddal=ucty['602'], datum=form.vars.k_datu, castka=castka)
                else:
                    scitadlo['379'] = [scitadlo['379'][0]+castka, scitadlo['379'][1], scitadlo['379'][2]+castka]
                    scitadlo['602'] = [scitadlo['602'][0], scitadlo['602'][1]+castka, scitadlo['602'][2]-castka]
                    scitadlo2['379-12'] = [scitadlo2['379-12'][0]+castka, scitadlo2['379-12'][1], scitadlo2['379-12'][2]+castka]
                    scitadlo2['602'] = [scitadlo2['602'][0], scitadlo2['602'][1]+castka, scitadlo2['602'][2]-castka]
            pred_pulnoc = datetime.datetime(form.vars.k_datu.year, form.vars.k_datu.month, form.vars.k_datu.day, 23, 59)
            pohyby = db((db.pohyb.datum>=iniciovano_ke_dni) & (db.pohyb.datum<=pred_pulnoc)).select(orderby=db.pohyb.datum)
            for pohyb in pohyby:
                if pohyb.idma_dati is None or pohyb.iddal is None:
                    return "Nektera transakce nema uveden ucet MD/Dal. Nejprve dopln."
                ucno2 = ucty2[pohyb.idma_dati]
                ucno = ucno2[:3]
                scitadlo[ucno] = scitadlo[ucno][0]+pohyb.castka, scitadlo[ucno][1], scitadlo[ucno][2]+pohyb.castka
                scitadlo2[ucno2] = scitadlo2[ucno2][0]+pohyb.castka, scitadlo2[ucno2][1], scitadlo2[ucno2][2]+pohyb.castka
                ucno2 = ucty2[pohyb.iddal]
                ucno = ucno2[:3]
                scitadlo[ucno] = scitadlo[ucno][0], scitadlo[ucno][1]+pohyb.castka, scitadlo[ucno][2]-pohyb.castka
                scitadlo2[ucno2] = scitadlo2[ucno2][0], scitadlo2[ucno2][1]+pohyb.castka, scitadlo2[ucno2][2]-pohyb.castka
            vypis_uctu = sorted(list(scitadlo))
            vypis_uctu2 = sorted(list(scitadlo2))
            
            if form.vars.zapsat:
                db.commit()
            if form.vars.zavrit:
                dalsi_den = form.vars.k_datu + datetime.timedelta(days=1)  # 3.2017: zatím nepřecházím na 702/701, nechávám 702/702
                for ucet in vypis_uctu2:
                    if ucet[0]>'6':      # divné / nezajímavé ?
                        continue
                    secteny = scitadlo2[ucet]
                    prevod = int(round(secteny[2]))
                    if ucet[0]<'5':      # ne náklady a výnosy
                        sber = '702'
                        next_year = True
                    else:
                        sber = '710'     # 5,6: náklady a výnosy
                        next_year = False
                    if prevod>0:
                        db.pohyb.insert(idma_dati=ucty[sber], iddal=ucty[ucet], datum=form.vars.k_datu, castka=prevod)
                        if next_year:
                            db.pohyb.insert(idma_dati=ucty[ucet], iddal=ucty[sber], datum=dalsi_den, castka=prevod)
                    elif prevod<0:
                        db.pohyb.insert(idma_dati=ucty[ucet], iddal=ucty[sber], datum=form.vars.k_datu, castka= - prevod)
                        if next_year:
                            db.pohyb.insert(idma_dati=ucty[sber], iddal=ucty[ucet], datum=dalsi_den, castka= - prevod)

            response.view = 'zaverky/dp2.html'
            return dict(vypis_uctu=vypis_uctu, scitadlo=scitadlo, vypis_uctu2=vypis_uctu2, scitadlo2=scitadlo2)

    return dict(permice_in=permice_in, permice_out=permice_out,
            ziskano_mesice=ziskano_mesice, ziskano=ziskano,
            prevedeno=prevedeno, prevedeno_dne=prevedeno_dne,
            permice_max=permice_max, out_celkem = out_celkem,
            form=form, problem=problem,
            iniciovano_ke_dni=iniciovano_ke_dni)


@auth.requires_membership('pokladna')
def editovat_osnovu():
    grid = SQLFORM.grid(db.ucet,
                        showbuttontext=False,
                        )
    search_input = grid.element('#w2p_keywords')
    search_input and search_input.attributes.pop('_onfocus')
    return dict(grid=grid)


@auth.requires_membership('vedeni')
def zalohy():
    sum_auth_user = db.auth_user.zaloha.sum()
    zalohy = db().select(sum_auth_user).first()[sum_auth_user]

    ucet_zaloh = db(db.ucet.ucet == '379-09').select().first().id
    sum_pohyby = db.pohyb.castka.sum()
    dal = db(db.pohyb.iddal == ucet_zaloh).select(sum_pohyby).first()[sum_pohyby]
    md = db(db.pohyb.idma_dati == ucet_zaloh).select(sum_pohyby).first()[sum_pohyby]

    preklenovaci_ucet = db(db.ucet.ucet == '702').select().first().id
    prevody0 = db((db.pohyb.iddal == ucet_zaloh) & (db.pohyb.idma_dati == preklenovaci_ucet)).select(sum_pohyby).first()[sum_pohyby]
    prevody1 = db((db.pohyb.idma_dati == ucet_zaloh) & (db.pohyb.iddal == preklenovaci_ucet)).select(sum_pohyby).first()[sum_pohyby]

    return dict(zalohy=zalohy, dal=dal, md=md, prevody=(prevody0, prevody1))


@auth.requires_membership('pokladna')
def zalohy2():
    """
        po jednotlivých uživatelích
    """
    from collections import defaultdict

    pohyby = defaultdict(lambda: [0, 0])   # dal, md
    preklenovaci_ucet = db(db.ucet.ucet == '702').select().first().id

    ucet_zaloh = db(db.ucet.ucet == '379-09').select().first().id

    md = db(db.pohyb.idma_dati == ucet_zaloh).select(db.pohyb.castka, db.pohyb.idauth_user)
    dal = db(db.pohyb.iddal == ucet_zaloh).select(db.pohyb.castka, db.pohyb.idauth_user)
    for pohyb in dal:
        pohyby[pohyb.idauth_user][0] += pohyb.castka
    for pohyb in md:
        pohyby[pohyb.idauth_user][1] += pohyb.castka

    shoda = neshoda = manko = s_user = s_pohyb = 0
    neshodni = []
    uzivatele = db().select(db.auth_user.id, db.auth_user.vs, db.auth_user.nick, db.auth_user.email, db.auth_user.zaloha,
                                 orderby=db.auth_user.id)
    for uzivatel in uzivatele:
        z_pohybu = pohyby[uzivatel.id][0] - pohyby[uzivatel.id][1]
        s_user += uzivatel.zaloha
        s_pohyb += z_pohybu
        if uzivatel.zaloha == z_pohybu:
            shoda += 1
        else:
            neshoda += 1
            manko1 = uzivatel.zaloha - z_pohybu
            manko += manko1
            neshodni.append((uzivatel.id, uzivatel.vs, uzivatel.nick, uzivatel.email, uzivatel.zaloha, z_pohybu, manko1))

    divne = db(((db.pohyb.idauth_user == None) | (db.pohyb.idauth_user <= 0)) &
               ((db.pohyb.idma_dati == ucet_zaloh) | (db.pohyb.iddal == ucet_zaloh)) &
               (db.pohyb.idma_dati != preklenovaci_ucet) & (db.pohyb.iddal != preklenovaci_ucet)).select(
            db.pohyb.id, db.pohyb.datum, db.pohyb.castka, db.pohyb.iddal, db.pohyb.popis, orderby=~db.pohyb.datum)
    castky = []
    for divny in divne:
        if divny.iddal == ucet_zaloh:  # nelze update_record(), protože se commitne
            castky.append(-divny.castka)
        else:
            castky.append(divny.castka)

    neshodni.sort(key=lambda r: r[-1], reverse=True)
    return dict(shoda=shoda, neshoda=neshoda, manko=manko, neshodni=neshodni, s_user=s_user, s_pohyb=s_pohyb, divne=divne, castky=castky)
