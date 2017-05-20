# -*- coding: utf-8 -*-

aktualita = "Naše Rada: Dandee, cz.Radka, Mára"

response.title = T('wKasa')
response.subtitle = T('webová pokladna')
response.logo = A(B("Společné aktivity o.s.")+' - '+response.subtitle,
                  _class="brand",_href=URL('default', 'index'))

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Mirek Zvolský <mirek.zvolsky@gmail.com>'
response.meta.description = 'webová pokladna, stav banky a pokladny, web cash desk, cash desk and account state'
response.meta.keywords = 'cash desk, account'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = []
if auth.user:
    response.menu.append((T('Zákazník'), False, URL('info', 'coajak'), [
            (T('Přehled a žádost o vrácení os.zálohy'), False, URL('platby', 'prehled'), []),
            (T('Pohyby na záloze'), False, URL('platby', 'pohyby'), []),
            (TFu('Věnovat peníze jiné(mu)'), False, URL('platby', 'venovat'), []),
            (TFu('Darovat peníze sdružení'), False, URL('platby', 'darovat_sdruzeni'), []),
            ]))
else:
    if not (request.controller=='default' and request.function=='index'):
        response.menu.append((T('Před přihlášením'), False,
                URL('default', 'index'), []))
response.menu.append((T('Informace'), False, URL('info', 'coajak'), [
            (T('Jak platit'), False, URL('info', 'coajak'), []),
            (T('Můžu ošidit jedinou platbu?'), False, URL('info', 'poprve'), []),
            (T('O sdružení'), False, URL('info', 'sdruzeni'), []),
            (T('O FungujemeAktivne'), False, URL('info', 'fungujeme'), []),
            (T('O spolecneaktivity.cz'), False, URL('info', 'jp'), []),
            (T('Pro organizátory'), False, URL('info', 'organizatori'), []),
            (T('Pro pokladníka'), False, URL('info', 'pokladnik'), []),
            ]))
subpostak = [
            ]
if auth.has_membership('vedeni'):
    subpostak.append((T('Hromadný mail'), False,
              URL('postak', 'zakaznikum'), []))
response.menu.append((T('Pošťák'), False, None, subpostak))

if auth.user and auth.user.organizator:
    suborganizator = [(T('Záznamy do pokladny'), False, URL('organizator', 'pokladna'), []),]
    if auth.has_membership('vedeni'):
        suborganizator.append((T('Dluhy'), False, URL('organizator', 'dluhy'), []))
    response.menu.append((T('Záznamy do pokladny'), False, URL('organizator', 'pokladna'), suborganizator))

subclenstvi = [
            (T('Členové sdružení'), False, URL('prehledy', 'clenove'), []),
            (T('Hlavní organizátoři'), False, URL('prehledy', 'hlorg'), []),
            (T('Rada'), False, URL('prehledy', 'rada'), []),
            (T('Dozorčí komise'), False, URL('prehledy', 'dk'), []),
            ]
subprehledy = [
            (T('Členství'), False, URL('prehledy', 'clenove'), subclenstvi),
            ]
if auth.has_membership('vedeni'):
    subprehledy.append((T('Zákazníci'), False,
              URL('prehledy', 'zakaznici'), []))
subprehledy.append((T('Čísla a ceny akcí'), False,
        URL('home', 'xml', '', scheme='http', host='www.fungujemeaktivne.cz'), []))        
if auth.user:
    subprehledy.append((T('Podané žádosti'), False,
              URL('prehledy', 'zadosti'), []))        
if auth.has_membership('vedeni'):
    subprehledy.append((T('Jednoduché'), False,
              None, [
              (TFu('všechny výdaje'), False,
                        URL('jednoduche', 'vydaje'), []),
              (TFu('pokladna'), False,
                        URL('jednoduche', 'pokladna'), []),
              (TFu('výběry z bankomatu'), False,
                        URL('jednoduche', 'atm'), []),
              (TFu('BÚ sdružení (2 měsíce)'), False,
                        URL('jednoduche', 'bu2'), []),
              (TFu('BÚ sdružení (vše)'), False,
                        URL('jednoduche', 'bu'), []),
              ]))
    podvojne = [
              (T('používané účty'), False,
                        URL('zaverky', 'osnova'), []),
              (T('všechny pohyby'), False,
                        URL('podvojne', 'vsechny'), []),
              (T('pohyby za 2 měsíce'), False,
                        URL('podvojne', 'nedavne'), []),
              (T('vyhledat částku'), False,
                        URL('podvojne', 'castka'), []),
              (T('navýšení zálohy'), False,
                        URL('podvojne', 'zal_plus'), []),
              (T('za akce Fungujeme'), False,
                        URL('podvojne', 'fungujeme'), []),
              (T('BÚ sdružení'), False,
                        URL('podvojne', 'bu'), []),
              (T('pokladna'), False,
                        URL('podvojne', 'pokladna'), []),
              (T('chybí účet'), False,
                        URL('podvojne', 'chybi'), []),
            ]
    zaverky = [
              (T('roční závěrky (daňová přiznání)'), False,
                        URL('zaverky', 'dp'), []),
              (T('závěrky (původní verze)'), False,
                        URL('zaverky', 'obdobi'), []),
              (T('zálohy'), False,
                        URL('zaverky', 'zalohy'), []),
            ]
    if auth.has_membership('pokladna'):
        podvojne.append((TFu('Přidat záznam'), False, URL('prehledy', 'pridat_pohyb'), []))
    subprehledy.append((TFu('Podvojné'), False, None, podvojne))
    subprehledy.append((TFu('Závěrky'), False, None, zaverky))
    subprehledy.append((TFu('Partneři'), False, URL('partneri', 'prehled'), []))
    subprehledy.append((TFu('Faktury'), False,
              None, [
              (T('přijaté'), False,
                        URL('fp', 'prehled'), []),
              ]))
response.menu.append((T('Přehledy'), False, None, subprehledy))

DEVELOPMENT_MENU = False

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu += [
        (SPAN('web2py', _class='highlighted'), False, 'http://web2py.com', [
        (T('My Sites'), False, URL('admin', 'default', 'site')),
        (T('This App'), False, URL('admin', 'default', 'design/%s' % app), [
        (T('Controller'), False,
         URL(
         'admin', 'default', 'edit/%s/controllers/%s.py' % (app, ctr))),
        (T('View'), False,
         URL(
         'admin', 'default', 'edit/%s/views/%s' % (app, response.view))),
        (T('Layout'), False,
         URL(
         'admin', 'default', 'edit/%s/views/layout.html' % app)),
        (T('Stylesheet'), False,
         URL(
         'admin', 'default', 'edit/%s/static/css/web2py.css' % app)),
        (T('DB Model'), False,
         URL(
         'admin', 'default', 'edit/%s/models/db.py' % app)),
        (T('Menu Model'), False,
         URL(
         'admin', 'default', 'edit/%s/models/menu.py' % app)),
        (T('Database'), False, URL(app, 'appadmin', 'index')),
        (T('Errors'), False, URL(
         'admin', 'default', 'errors/' + app)),
        (T('About'), False, URL(
         'admin', 'default', 'about/' + app)),
        ]),
            ('web2py.com', False, 'http://www.web2py.com', [
             (T('Download'), False,
              'http://www.web2py.com/examples/default/download'),
             (T('Support'), False,
              'http://www.web2py.com/examples/default/support'),
             (T('Demo'), False, 'http://web2py.com/demo_admin'),
             (T('Quick Examples'), False,
              'http://web2py.com/examples/default/examples'),
             (T('FAQ'), False, 'http://web2py.com/AlterEgo'),
             (T('Videos'), False,
              'http://www.web2py.com/examples/default/videos/'),
             (T('Free Applications'),
              False, 'http://web2py.com/appliances'),
             (T('Plugins'), False, 'http://web2py.com/plugins'),
             (T('Layouts'), False, 'http://web2py.com/layouts'),
             (T('Recipes'), False, 'http://web2pyslices.com/'),
             (T('Semantic'), False, 'http://web2py.com/semantic'),
             ]),
            (T('Documentation'), False, 'http://www.web2py.com/book', [
             (T('Preface'), False,
              'http://www.web2py.com/book/default/chapter/00'),
             (T('Introduction'), False,
              'http://www.web2py.com/book/default/chapter/01'),
             (T('Python'), False,
              'http://www.web2py.com/book/default/chapter/02'),
             (T('Overview'), False,
              'http://www.web2py.com/book/default/chapter/03'),
             (T('The Core'), False,
              'http://www.web2py.com/book/default/chapter/04'),
             (T('The Views'), False,
              'http://www.web2py.com/book/default/chapter/05'),
             (T('Database'), False,
              'http://www.web2py.com/book/default/chapter/06'),
             (T('Forms and Validators'), False,
              'http://www.web2py.com/book/default/chapter/07'),
             (T('Email and SMS'), False,
              'http://www.web2py.com/book/default/chapter/08'),
             (T('Access Control'), False,
              'http://www.web2py.com/book/default/chapter/09'),
             (T('Services'), False,
              'http://www.web2py.com/book/default/chapter/10'),
             (T('Ajax Recipes'), False,
              'http://www.web2py.com/book/default/chapter/11'),
             (T('Components and Plugins'), False,
              'http://www.web2py.com/book/default/chapter/12'),
             (T('Deployment Recipes'), False,
              'http://www.web2py.com/book/default/chapter/13'),
             (T('Other Recipes'), False,
              'http://www.web2py.com/book/default/chapter/14'),
             (T('Buy this book'), False,
              'http://stores.lulu.com/web2py'),
             ]),
            (T('Community'), False, None, [
             (T('Groups'), False,
              'http://www.web2py.com/examples/default/usergroups'),
                        (T('Twitter'), False, 'http://twitter.com/web2py'),
                        (T('Live Chat'), False,
                         'http://webchat.freenode.net/?channels=web2py'),
                        ]),
                (T('Plugins'), False, None, [
                        ('plugin_wiki', False,
                         'http://web2py.com/examples/default/download'),
                        (T('Other Plugins'), False,
                         'http://web2py.com/plugins'),
                        (T('Layout Plugins'),
                         False, 'http://web2py.com/layouts'),
                        ])
                ]
         )]
if DEVELOPMENT_MENU: _()

# if "auth" in locals(): auth.wikimenu()
