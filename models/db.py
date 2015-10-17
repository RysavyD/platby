# -*- coding: utf-8 -*-

import os
import datetime
import locale
import platform
from decimal import Decimal
import vfp

def TFu(txt):
    return txt # překlad zatím ne, a nezapisovat do překladové tabulky

class SOUHLAS_S_VS(object):
    '''validátor pro auth_user.ss
    '''
    def __init__(self, vs):
        self.vs = vs
    def __call__(self, value):
        value = value.strip().lstrip('0')
        if not value:
            return ('', None)
        try:
            intss = int(value)
        except:
            intss = None
        if not intss:
            return (value, 'Je třeba zadat pouze číslo.')
        try:
            intvs = int(self.vs)
        except:
            intvs = 0
        if 101<=intvs<=674:  # registrovaní při převodu
            if self.vs!=value:
                return ('', 'Lze zadat jen %s nebo ponechat prázdné' % intvs)
        else:                # registrovaní později
            if intss<675:
                return ('', 'Zadané číslo uživatele není přípustné')
        return (value, None)

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
if request.is_local:
    from gluon.custom_import import track_changes
    track_changes(True)    # auto-reload modules
else:
    request.requires_https()

if 'windows' in platform.system().lower():
    locale.setlocale(locale.LC_ALL, 'Czech_Czech republic.1250')
else:
    locale.setlocale(locale.LC_ALL, 'cs_CZ.utf8')
if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://platby.sqlite',pool_size=1,check_reserved=['all'])
    db._adapter.connection.create_collation("lexical", locale.strcoll)
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.settings.create_user_groups = None
vs_default = TFu('dostaneš..') # max 10 znaků
auth.settings.extra_fields['auth_user'] = [
    Field('email_ver', 'boolean', default=False, label=TFu("Mail není tajný"),
          comment=TFu('zaškrtni, pokud si myslíš, že případné zobrazení Tvé e-mailové adresy někde na stránkách sdružení a v korespondenci sdružení nemůže vadit')),
    Field('telefon', length=32, default='', label=TFu("Telefon"),
          comment=TFu('vyplň, chceš-li vedení sdružení dát možnost Ti v důležitých případech zavolat')),
    Field('tel_ver', 'boolean', default=False, label=TFu("Tel. není tajný"),
          comment=TFu('zaškrtni, pokud si myslíš, že případné zobrazení Tvého telefonu někde na stránkách sdružení a v korespondenci sdružení nemůže vadit')),
    Field('nick', length=100, default='',
          comment=TFu('přezdívka; lze napsat např Manik/MyNick; jde o to, abychom mohli správně zadat Tvoji platbu v hotovosti - jinak Tvé zaplacení nevyrovná úhradu a může Ti vzniknout (evidenční) dluh')),
    Field('organizator', 'boolean', default=False,
          label=TFu('Organizátor akcí'),
          comment=TFu('zaškrtni, pokud organizuješ nebo chceš organizovat akce - zpřístupní menu Záznamy do pokladny')),
    Field('vs', length=10, writable=False, default=vs_default,
          label=TFu('Osobní symbol (VS)'),
          comment=TFu('tento variabilní symbol (osobní symbol) používej pro platby; preferujeme variabilní symbol, ale s ohledem na spolecneaktivity.cz bude číslo rozpoznáno i ve specifickém symbolu')),
    Field('ss', length=10, default='', readable=False, writable=False,
          label=TFu('Symbol pro spolecneaktivity.cz (SS)'),
          comment=TFu('uveď, chceš-li hradit akce pro tento specifický symbol na spolecneaktivity.cz; pozor: nesprávné zadání způsobí úhradu někomu jinému')),
    Field('zaloha', 'decimal(11,2)', label=TFu('Záloha'),
        writable=False, default=0),
    Field('ode_dne', 'date', readable=False, writable=False,
        default=datetime.date.today(), label=TFu('Ode dne'),
        comment=TFu('jako zákazník Sdružení jsem registrován(a) ode dne')),
    Field('prihlasen', 'date', label='Přihlášen',
        readable=False, writable=False),
    Field('vyzva', 'date', readable=False, writable=False),
    Field('neposilat', 'boolean', default=False, label=TFu('Neposílat info'),
        comment=TFu('zaškrtnutím zabráníš zasílání informačních mailů - vzhledem k tomu, že jde o Tvé peníze, toto nedoporučujeme')),
    Field('ne_ostatnim', 'boolean', default=False,
        label=TFu("Stop ostatním"),
        comment=TFu("zaškrtnutím znemožníš všem ostatním účastníkům akcí poslat Ti vzkaz (rozumí se výběrem Tvého nicku - jiný údaj, jako jméno nebo mail jim neposkytneme)")),
    ]
'''
Field('clen', 'boolean', writable=False, default=False,
    label=TFu("Člen sdružení"),
    comment=TFu("členství ve sdružení Společné Aktivity, o.s.")),
'''

auth.define_tables(username=False, signature=False)
db.auth_user.ss.requires=[
      SOUHLAS_S_VS(auth.user and auth.user.vs or ''),
      IS_EMPTY_OR(IS_NOT_IN_DB(db, db.auth_user.ss)),
      ]
db.auth_user._format = '%(nick)s - %(vs)s'
db.auth_user.email.comment = TFu('zapiš mail z registrace na fungujemeaktivne.cz (případně z registrace na spolecneaktivity.cz před rokem 2013)')
name_comment = TFu('údaj nepředáme třetí straně - pomáhá nám identifikovat platby')
db.auth_user.first_name.comment = name_comment
db.auth_user.last_name.comment = name_comment
db.auth_user.password.comment = TFu("raději NEPOUŽÍVEJ stejné heslo jako na jiných serverech")

## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'  # 'logging' or ...
mail.settings.sender = 'spolecneaktivityos@gmail.com'
mail.settings.login = 'spolecneaktivityos@gmail.com:'+vfp.filetostr(
        os.path.join(request.folder, 'private', 'saos_gmail.smtp'))
#mail.settings.server = 'smtp.mandrillapp.com:587'
#mail.settings.sender = 'mirek@zvolsky@gmail.com'
#mail.settings.login = 'mirek@zvolsky@gmail.com:'+vfp.filetostr(
#        os.path.join(request.folder, 'private', 'zvolsky_gmail_mandrill.smtp'))

## configure auth policy
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = False

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.rpx_account import use_janrain
#use_janrain(auth, filename='private/janrain.key')
