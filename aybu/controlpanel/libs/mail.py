#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on May 8, 2009

@author:
    Copyright ©2009 Asidev s.r.l.
    Luca Frosini <l.frosini@asidev.com>
'''

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib


class Mail(object):

    def __init__(self, config):
        """Initialize the Mail object creating Root as Multipart MIME Object"""
        self.__msg_root = MIMEMultipart('related')
        self.__msg_root.preamble = 'This is a multi-part message '\
                                   'in MIME format.'
        self.__attach_alternative()
        self.__addresses = []

    def __attach_alternative(self):
        """
        Create the Alternative Object to attach the alternative representation
        of the Mail"""
        self.__msg_alternative = MIMEMultipart('alternative')
        self.__msg_root.attach(self.__msgAlternative)

    def __set_addresses(self, address):
        if address not in self.__addresses:
            self.__addresses.append(address)

    def set_subject(self, subject):
        self.__msg_root['Subject'] = subject

    def set_sender(self, sender):
        self.__msg_root['From'] = sender

    def set_recipient(self, recipient):
        self.__msg_root['To'] = recipient
        self.__set_addresses(recipient)

    def set_cc_recipient(self, cc_recipient):
        self.__msg_root['Cc'] = cc_recipient
        self.__set_addresses(cc_recipient)

    def attach_text_message(self, text_message):
        """Attach a text representation of the Mail"""
        self.__text_message = text_message

    def attach_HTML_message(self, html_message):
        """Attach HTML representation of the Mail"""
        self.__html_message = html_message

    def send(self):
        msg_text = MIMEText(self.__text_message)
        msg_text.set_charset('utf-8')
        self.__msg_alternative.attach(msg_text)

        try:
            msg_HTML = MIMEText(self.__html_message, 'html')
            msg_HTML.set_charset('utf-8')
            self.__msg_alternative.attach(msg_HTML)
        except:
            pass

        smtp_server = self.config.get('smtp_server', 'localhost')
        smtp_port = int(self.config.get('smtp_port', 25))

        smtp = smtplib.SMTP(smtp_server, smtp_port)

        smtp_user = self.config.get('smtp_user', '')
        smtp_password = self.config.get('smtp_password', '')

        if smtp_user != '' and smtp_password != '':
            smtp.login(smtp_user, smtp_password)

        try:
            smtp.sendmail(self.__msg_root['From'], self.__addresses,
                          self.__msg_root.as_string())
        except:
            pass

        smtp.quit()
