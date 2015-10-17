# coding: utf8

from mz_wkasa_platby import Uc_sa, zpatky, aliases

@auth.requires_membership('vedeni')
def bu2():
    response.view = 'jednoduche/pohyby.html'
    md, dal, org = aliases(db) 
    return dict(sledovany=Uc_sa.bezny,
        pohyby=db((db.pohyb.datum>=zpatky(60))&(
              (db.pohyb.iddal==Uc_sa.bezny)|
              (db.pohyb.idma_dati==Uc_sa.bezny))).select(
          db.pohyb.ALL,
          db.auth_user.nick,
          org.nick,
          md.zkratka, dal.zkratka,
          left=(db.auth_user.on(db.auth_user.id==db.pohyb.idauth_user),
              org.on(org.id==db.pohyb.idorganizator),
              md.on(md.id==db.pohyb.idma_dati),
              dal.on(dal.id==db.pohyb.iddal)),
          orderby=~db.pohyb.datum))

@auth.requires_membership('vedeni')
def bu():
    response.view = 'jednoduche/pohyby.html'
    md, dal, org = aliases(db) 
    return dict(sledovany=Uc_sa.bezny,
        pohyby=db((db.pohyb.iddal==Uc_sa.bezny)|
              (db.pohyb.idma_dati==Uc_sa.bezny)).select(
          db.pohyb.ALL,
          db.auth_user.nick,
          org.nick,
          md.zkratka, dal.zkratka,
          left=(db.auth_user.on(db.auth_user.id==db.pohyb.idauth_user),
              org.on(org.id==db.pohyb.idorganizator),
              md.on(md.id==db.pohyb.idma_dati),
              dal.on(dal.id==db.pohyb.iddal)),
          orderby=~db.pohyb.datum))

@auth.requires_membership('vedeni')
def pokladna():
    response.view = 'jednoduche/pohyby.html'
    md, dal, org = aliases(db) 
    return dict(sledovany=Uc_sa.pokladna,
        pohyby=db((db.pohyb.iddal==Uc_sa.pokladna)|
              (db.pohyb.idma_dati==Uc_sa.pokladna)|
              (db.pohyb.iddal==Uc_sa.org)|
              (db.pohyb.idma_dati==Uc_sa.org)).select(
          db.pohyb.ALL,
          db.auth_user.nick,
          org.nick,
          md.zkratka, dal.zkratka,
          left=(db.auth_user.on(db.auth_user.id==db.pohyb.idauth_user),
              org.on(org.id==db.pohyb.idorganizator),
              md.on(md.id==db.pohyb.idma_dati),
              dal.on(dal.id==db.pohyb.iddal)),
          orderby=~db.pohyb.datum))

@auth.requires_membership('vedeni')
def atm():
    response.view = 'jednoduche/pohyby.html'
    md, dal, org = aliases(db) 
    return dict(sledovany=Uc_sa.pokladna,
        pohyby=db(((db.pohyb.iddal==Uc_sa.pokladna)&
              (db.pohyb.idma_dati==Uc_sa.bezny))|
              ((db.pohyb.iddal==Uc_sa.bezny)&
              (db.pohyb.idma_dati==Uc_sa.pokladna))).select(
          db.pohyb.ALL,
          db.auth_user.nick,
          org.nick,
          md.zkratka, dal.zkratka,
          left=(db.auth_user.on(db.auth_user.id==db.pohyb.idauth_user),
              org.on(org.id==db.pohyb.idorganizator),
              md.on(md.id==db.pohyb.idma_dati),
              dal.on(dal.id==db.pohyb.iddal)),
          orderby=~db.pohyb.datum))

@auth.requires_membership('vedeni')
def vydaje():
    response.view = 'jednoduche/pohyby.html'
    md, dal, org = aliases(db)
    pohyby = db(((db.pohyb.iddal==Uc_sa.pokladna)|
              (db.pohyb.iddal==Uc_sa.bezny)|
              (db.pohyb.iddal==Uc_sa.org))&
              (db.pohyb.idma_dati!=Uc_sa.pokladna)&
              (db.pohyb.idma_dati!=Uc_sa.bezny)&
              (db.pohyb.idma_dati!=Uc_sa.org)).select(
          db.pohyb.ALL,
          db.auth_user.nick,
          org.nick,
          md.zkratka, dal.zkratka,
          left=(db.auth_user.on(db.auth_user.id==db.pohyb.idauth_user),
              org.on(org.id==db.pohyb.idorganizator),
              md.on(md.id==db.pohyb.idma_dati),
              dal.on(dal.id==db.pohyb.iddal)),
          orderby=~db.pohyb.datum)
    return dict(sledovany=None,
        pohyby=pohyby)
