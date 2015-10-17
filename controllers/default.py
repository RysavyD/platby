# -*- coding: utf-8 -*-

def index():
    if auth.user_id:
        redirect(URL('info', 'coajak'))
    else:
        return {}

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in 
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    # <!-- mz patch -->
    
    if request.args(0)=='login':
        db.auth_user.email.comment = TFu(
            'e-mail, pod nímž jsi zde registrován (přihlašuješ-li se poprvé na mail z fungujemeaktivne.cz, nejprve si nastav heslo pomocí "Zapomněl jste heslo"/"Nastavit nové heslo")')
    elif request.args(0)=='request_reset_password':
        db.auth_user.email.comment = TFu(
            'e-mail, pod nímž jsi zde registrován (pokud ses ještě nepřihlašoval, vyplň mail z fungujemeaktivne.cz (nebo z registrace na spolecneaktivity.cz před r.2013))')

    #       login z menu jde na úvodní stránku;
    #       správný musí mít další (dummy) parametr 
    if request.args(0)=='register' and len(request.args)<2:
        session.flash = TFu("Prosím, vyber správnou možnost přihlášení ze 3 voleb níže na stránce") 
        redirect(URL('index'))

    return dict(form=auth())

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
