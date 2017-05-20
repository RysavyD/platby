#!/usr/bin/env python
# -*- coding: utf8 -*-

u'''
odešle mail pomocí mandrill
'''

import base64
import os
import mimetypes

#import mandrill
from sparkpost import SparkPost
import vfp

appdir = os.path.join(os.getcwd(), 'applications', 'platby')
#mandrill_key = vfp.filetostr(os.path.join(appdir,
#          'private', 'zvolsky_gmail_mandrill.smtp'))
sparkpost_key = vfp.filetostr(os.path.join(appdir,
          'private', 'sparkpost_zitranavylet_zvolsky.key')).strip()

def mandrill_send(subject, txt, prilohy=[], prijemci=
      [{'email': 'mirek.zvolsky@gmail.com', 'name': u'Mirek Zvolský na Googlu'},
      {'email': 'zvolsky@seznam.cz', 'name': u'Mirek Zvolský na Seznamu'}],
      styl='text'):
    '''
    subject, txt - nejlépe unicode objekty
    prijemci - viz příklad defaultní hodnoty
    styl = 'html'/'text'
    přílohy je třeba uložit přes FTP do mail_attachments/ a po odeslání smazat
    '''

    attachments = []
    for priloha in prilohy:
        attachments.append({
                'filename': priloha,
                'name': os.path.basename(priloha),
                'type': mimetypes.guess_type(priloha)[0] or 'application/octet-stream'
        })
    #pro mandrill bylo:
    #'content': base64.b64encode(open(priloha, 'rb').read()), # pro mandrill bylo 'content'
    #'type': mimetypes.guess_type(priloha) or 'text/plain'

    stylDict = {styl: txt}
    sp = SparkPost(sparkpost_key)
    sp.transmissions.send(
        recipients=[prijemce['email'] for prijemce in prijemci],
        from_email=u'Společné Aktivity <spolecneaktivity@zitranavylet.cz>',
        subject=subject,
        attachments=attachments,
        **stylDict
    )

    # https://mandrillapp.com/api/docs/messages.python.html#method=send
    #m=mandrill.Mandrill(mandrill_key)
    #msg = {
    #     'from_email': 'spolecneaktivityos@gmail.com',
    #     'from_name': u'Společné Aktivity o.s.',
    #     'subject': subject,
    #     styl: txt,
    #     'to': prijemci,
    #     'attachments': attachments,
    #}
        # 'attachments': [{'content': 'ZXhhbXBsZSBmaWxl',
        #                 'name': 'myfile.txt', 'type': 'text/plain'}]
        #
        #    def filetobase64(self, inputfilename):
        # return base64.b64encode(open(inputfilename, 'rb').read())
        
    #m.messages.send(message=msg)

# společné pro plánované maily
#  -v controléru postak.py i ve scriptu pro odesílání scripts/send_plan_maily.py

def __init_plan_maily(): 
    maildir = os.path.join(appdir, 'maily')
    planovany = os.path.join(maildir, 'chystany.hlavicka')
    planovany2 = os.path.join(maildir, 'chystany.obsah')
    return maildir, planovany, planovany2

def __parse_mailheader(hlavicka_filename):
    hlavicka = vfp.filetostr(hlavicka_filename)
    radky_hlavicky = hlavicka.splitlines()
    is_html = True if radky_hlavicky[0][0]=='H' else False
    komu = radky_hlavicky[0][1]  # Z|C|O|A zákazníkům/členům/organizátorům/vedení
    subj = unicode(radky_hlavicky[1], 'utf8')
    return (is_html, komu, subj)
