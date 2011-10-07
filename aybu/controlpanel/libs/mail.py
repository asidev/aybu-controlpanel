#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
