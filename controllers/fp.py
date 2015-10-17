# coding: utf8

@auth.requires_membership('pokladna')
def edit():
    fp = db.fp(request.args(0)) or redirect('fp', 'prehled')
    form = SQLFORM(db.fp, fp)
    if form.process().accepted:
        redirect('fp', 'prehled')
    return dict(form=form)

@auth.requires_membership('vedeni')
def prehled():
    return dict(grid=SQLFORM.grid(db.fp,
              left=db.partner.on(db.fp.partner_id==db.partner.id),
              fields=[db.fp.id, db.fp.zauctovana, db.fp.vystaveno, db.fp.uhrazeno,
                  db.fp.no_jejich, db.fp.castka, db.partner.nazev, db.fp.poznamka
                  ],
              #links=dict(header='pohyby',
              #    body=lambda row: A('v', _href=URL('pohyby', args=row.fp.id))),
              deletable=False,
              editable=auth.has_membership('pokladna'),
              create=auth.has_membership('pokladna'),
              csv=auth.has_membership('vedeni'),
              paginate=100,
              orderby=db.fp.vystaveno,
              showbuttontext=False,
              maxtextlengths={'fp.poznamka' : 40}
              ))

@auth.requires_membership('pokladna')
def zauctovani():
    from mz_wkasa_platby import Uc_sa
    
    ucet_fp = db(db.ucet.ucet=='321').select().first().id # = Uc_sa.fp
    protokol = ''

    nezauctovane1 = db(db.fp.zauctovana==False).select()
    prijate1 = db(db.pohyb.iddal==ucet_fp).select()
    platby1 = db(db.pohyb.idma_dati==ucet_fp).select()
    
    protokol = ''
    for faktura in nezauctovane1:
        if faktura.castka>0:
            problem = False
            protokol += '<a href="%s">id %s</a>: %s %s' % (
                        URL('fp', 'edit', args=faktura.id), faktura.id,
                        faktura.prijato and faktura.prijato.strftime('%d.%m.%Y') or '??', faktura.castka)
            
            # uplatněna do nákladů? je evidována záznamem 5../321 ?
            prijata = db((db.pohyb.fp_id==faktura.id) & (db.pohyb.iddal==Uc_sa.fp)).select()
            if len(prijata)==0:
                # ne: záznam se vytvoří jako náklad podle fp.md
                if faktura.md:
                    db.pohyb.insert(idma_dati=faktura.md, iddal=Uc_sa.fp,
                            castka=faktura.castka, datum=faktura.prijato,
                            fp_id=faktura.id, partner_id=faktura.partner_id)
                    protokol += ' +5../321'
                else:
                    problem = True
                    protokol += ' <b>nelze přidat 5../321, neznám fp.md 5..</b>'
            # ano: zkontroluj zda 5../321 záznam není problematický 
            elif len(prijata)>1:
                problem = True
                protokol += ' <b>vícekrát:5../321</b>'
            else:
                prijata = prijata.first()
                if prijata.castka!=faktura.castka:
                    problem = True
                    protokol += ' <b>castka?:5../321</b>'
                if prijata.datum.date()!=faktura.prijato:
                    problem = True
                    protokol += ' <b>datum?:5../321</b>'
                if prijata.idma_dati!=faktura.md:
                    if prijata.idma_dati:
                        problem = True
                        protokol += ' <b>md?:5../321</b>'
                    else:
                        prijata.update_record(idma_dati=faktura.md)
                if prijata.partner_id!=faktura.partner_id:
                    if prijata.partner_id:
                        problem = True
                        protokol += ' <b>partner?:5../321</b>'
                    else:
                        prijata.update_record(partner_id=faktura.partner_id)
                        
            # je-li k ní proplacena záloha, existuje její zúčtování 321/314?
            srovnano = datetime.datetime(1980,1,1)
            zaplaceno = 0
            zalohy = db((db.pohyb.fp_id==faktura.id) & (db.pohyb.idma_dati==Uc_sa.zaloha)).select()
            for zaloha in zalohy:
                zaplaceno += zaloha.castka
                srovnano = max(srovnano, zaloha.datum)
            if zaplaceno:
                zuctovani = db((db.pohyb.fp_id==faktura.id) & (db.pohyb.idma_dati==Uc_sa.fp)
                             & (db.pohyb.iddal==Uc_sa.zaloha)).select()
                if len(zuctovani)==0:
                    # ne: záznam 321/314 se vytvoří
                    db.pohyb.insert(idma_dati=Uc_sa.fp, iddal=Uc_sa.zaloha,
                            castka=zaplaceno, datum=faktura.prijato,
                            fp_id=faktura.id, partner_id=faktura.partner_id)
                    protokol += ' +321/314'
                # ano: zkontroluj zda 321/314 záznam není problematický 
                elif len(zuctovani)>1:
                    problem = True
                    protokol += ' <b>vícekrát:321/314</b>'
                else:
                    zuctovani = zuctovani.first()
                    if zuctovani.castka!=zaplaceno:
                        problem = True
                        protokol += ' <b>castka?:321/314</b>'
                    if zuctovani.datum.date()!=faktura.prijato:
                        problem = True
                        protokol += ' <b>datum?:321/314</b>'
                    if zuctovani.partner_id!=faktura.partner_id:
                        if zuctovani.partner_id:
                            problem = True
                            protokol += ' <b>partner?:321/314</b>'
                        else:
                            zuctovani.update_record(partner_id=faktura.partner_id)

            # zda je proplacena - sečtením částek md=321 (dal!=314)
            doplatky = db((db.pohyb.fp_id==faktura.id) & (db.pohyb.idma_dati==Uc_sa.fp)
                        & (db.pohyb.iddal!=Uc_sa.zaloha)).select()
            for doplatek in doplatky:
                zaplaceno += doplatek.castka
                srovnano = max(srovnano, doplatek.datum)
            if zaplaceno==faktura.castka:
                if not faktura.uhrazeno or not faktura.uhrazeno==srovnano.date():
                    faktura.update_record(uhrazeno=srovnano)
                    protokol += ' +datum-uhrady'
                protokol += ' plac-OK'
            else:
                problem = True
                protokol += ' <b>chybí %s (%s)?</b>' % (faktura.castka-zaplaceno,
                            faktura.uhrazeno and faktura.uhrazeno.strftime('%d.%m.%Y') or '?')

            if not problem:
                faktura.update_record(zauctovana=True)
                                                                        
            protokol += '<br />'
    
    nezauctovane2 = db(db.fp.zauctovana==False).select()
    prijate2 = db(db.pohyb.iddal==ucet_fp).select()
    platby2 = db(db.pohyb.idma_dati==ucet_fp).select()

    return dict(prijate1=prijate1, platby1=platby1,
            prijate2=prijate2, platby2=platby2,
            nezauctovane1=nezauctovane1, nezauctovane2=nezauctovane2,
            protokol=protokol)
