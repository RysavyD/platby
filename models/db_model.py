# coding: utf8

import locale
from mz_wkasa_platby import fix_login, Uc_sa
    # Uc_sa - id účtů účtové osnovy - při importu zde je vidí controléry i views

locale.setlocale(locale.LC_ALL, 'cs_CZ.UTF-8')


class IS_IN_DB_(IS_IN_DB):
    def build_set(self):
        super(IS_IN_DB_, self).build_set()
        records = [(lbl, self.theset[pos]) for pos, lbl in enumerate(self.labels)]
        records.sort(key=lambda x: locale.strxfrm(x[0]))
        self.labels = [rec[0] for rec in records]
        self.theset = [rec[1] for rec in records]


db.define_table('ucet',
    Field('ucet', length=7),
    Field('zkratka', length=3),
    Field('nazev', length=100),
    format='%(ucet)s - %(nazev)s'
    )

db.define_table('kategorie',
    Field('idma_dati', db.ucet),
    Field('iddal', db.ucet),
    Field('vyznam', default=''),
    format='%(vyznam)s'
    )

db.define_table('typp',
    Field('zkratka', length=1),
    Field('vyznam', length=40),
    format='%(vyznam)s'
    )

db.define_table('partner',
    Field('idx', 'integer'),  # foxpro id
    Field('typp_id', db.typp),
    Field('ucel', length=40),
    Field('nazev', length=60),
    Field('ulice', length=40),
    Field('psc', length=5),
    Field('misto', length=40),
    Field('ico', length=10),
    Field('kontakt', 'text'),
    Field('poznamka', 'text'),
    format='%(nazev)s, %(misto)s'
    )

db.define_table('fp',
    Field('idx', 'integer'),  # foxpro id
    Field('zauctovana', 'boolean', default=False),
    Field('md', db.ucet, label=TFu('nákladový účet 5..'),
        comment=TFu('pro zaúčtování faktury [MD=5..,Dal=321], pokud ještě nebylo provedeno')),
    Field('partner_id', db.partner, ondelete='SETNULL',),
    Field('ucet', length=20),
    Field('elektronicky', 'boolean', default=True),
    Field('castka', 'decimal(11,2)', default=0.00),
    Field('zaloha', 'decimal(11,2)', default=0.00),
    Field('no_jejich', length=20),
    Field('vystaveno', 'date'),
    Field('prijato', 'date'),
    Field('splatnost', 'date'),
    Field('uhrazeno', 'date'),
    Field('zal_uhrazeno', 'date'),
    Field('datum_akce', 'date'),
    Field('uhrada', length=1),
    Field('zal_uhrada', length=1),
    Field('vs', length=10),
    Field('ss', length=10),
    Field('ks', length=4),
    Field('vs_akce', length=5),
    Field('popis', length=90),
    Field('poznamka', 'text'),
    format='%(vystaveno)s, %(castka)s, %(no_jejich)s'
    )

db.define_table('pohyb',
    Field('idauth_user', 'reference auth_user', label=TFu("Uživatel"),
          requires=IS_EMPTY_OR(IS_IN_DB_(db, db.auth_user.id, '%(nick)s - %(vs)s'))),
    Field('idorganizator', 'reference auth_user', label=TFu("Zadal organizátor"),
          readable=False, writable=False,
          requires=IS_EMPTY_OR(IS_IN_DB(db, db.auth_user.id, '%(nick)s - %(vs)s'))),
    Field('idma_dati', 'reference ucet'),
    Field('iddal', 'reference ucet'),
    Field('fp_id', db.fp,
          requires=IS_EMPTY_OR(IS_IN_DB(db, db.fp.id, db.fp._format)),
          represent=lambda id, r=None: db.fp._format % db.fp(id) if id else '',
          ondelete='SETNULL',
          ),
    Field('partner_id', db.partner,
          requires=IS_EMPTY_OR(IS_IN_DB(db, db.partner.id, db.partner._format)),
          represent=lambda id, r=None: db.partner._format % db.partner(id) if id else '',
          ondelete='SETNULL',
          ),
    Field('datum', 'datetime',
          requires=[IS_NOT_EMPTY(), IS_DATETIME(format=TFu('%d.%m.%Y'))]),
    Field('castka', 'decimal(11,2)'),
    Field('popis', 'text'),
    Field('cislo_uctu', length=30),
    Field('kod_banky', length=10),
    Field('nazev_banky', length=40),
    Field('zakaznik', length=10),
    Field('vs', length=10, default=''),
    Field('ss', length=10, default=''),
    Field('ks', length=4, default=''),
    Field('id_pohybu', length=12),
    Field('id_pokynu', length=12),
    )

db.define_table('systab',
    Field('kod', length=12),
    Field('hodnota', length=100),
    )

db.define_table('loginlog',
    Field('idauth_user', 'reference auth_user'),
    Field('datum', 'date'),
    )

db.define_table('zadost',
    Field('zadost', 'datetime', label="Datum žádosti"),
    Field('idauth_user', 'reference auth_user', label="Uživatel"),
    Field('vyridil_id', 'reference auth_user', label="Vyřídil"),
    Field('vs', length=10, label="Symbol",
          comment="symbol uživatele"),
    Field('ss', length=10, label="Symbol obsol",
          comment=""),
    Field('typ', 'integer', label='Typ žádosti',
          comment='1 sa->wKasa, 2->na BÚ, 3 členství, 4 refundace'),
    Field('cislo_uctu', length=30, label='Číslo účtu'),
    Field('kod_banky', length=10, label='Kód banky'),
    Field('popis', 'text'),
    Field('prevod', 'datetime', label='Datum vyřízení'),
    Field('zadano', 'decimal(11,2)', label='Žádaná částka'),
    Field('prevedeno', 'decimal(11,2)', label='Převedená částka'),
    )

db.define_table('clenstvi',
    Field('user_id', 'reference auth_user', label="Uživatel"),
    Field('group_id', 'reference auth_group', label="Role ve sdružení"),
    Field('ode_dne', 'date', label="Ode dne"),
    Field('do_dne', 'date', label="Do dne"),
    )

fix_login(db, auth, vs_default)  # každému dát osobní symbol, logovat
    
## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
