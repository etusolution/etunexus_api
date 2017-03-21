# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import ssl
import traceback
import logging
import MultipartPostHandler

from . import API_USER_AGENT
from logger import get_logger


class CAS(object):
    """ Encapsulate CAS SSO authentication
    """

    # Constants
    __sso_cas_host = 'emc.online.etunexus.com'
    __cas_ticket_endpoint = '/cas/v1/tickets'
    __request_common_headers = {
        'Content-type': 'test/html',
        'Accept': 'application/json, text/plain, */*',
        'Pragma': 'no-cache'
    }

    # Methods
    def __init__(self, cas_group, cas_username, cas_password, cas_host=None, secure=True, loglevel=logging.INFO):
        """ Constructor

        Args:
            cas_group (str): The group to authenticate with CAS
            cas_username (str): The username to authenticate with CAS
            cas_password (str): The password to authenticate with CAS
            cas_host (str): The host/IP of the CAS server
            secure (bool): Enable the certificate check or not
            loglevel (int): Log level
        """
        assert cas_group and len(cas_group) > 0
        self._cas_group = cas_group
        assert cas_username and len(cas_username) > 0
        self._cas_username = cas_username
        assert cas_password and len(cas_password) > 0
        self._cas_password = cas_password

        self._cas_host = self.__sso_cas_host if not cas_host else cas_host
        self._tgt = None
        self._logger = get_logger(loglevel)

        # Init urllib2
        self._init_urllib(secure)

        self._logger.debug("CAS object (%s,%s,%s,%s) constructed" % (cas_host, cas_group, cas_username, cas_password))

    def _init_urllib(self, secure, debuglevel=0):
        cj = cookielib.CookieJar()
        no_proxy_support = urllib2.ProxyHandler({})
        cookie_handler = urllib2.HTTPCookieProcessor(cj)
        ctx = None
        if not secure:
            self._logger.info('[WARNING] Skip certificate verification.')
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        https_handler = urllib2.HTTPSHandler(debuglevel=debuglevel, context=ctx)
        opener = urllib2.build_opener(no_proxy_support,
                                      cookie_handler,
                                      https_handler,
                                      MultipartPostHandler.MultipartPostHandler)
        opener.addheaders = [('User-agent', API_USER_AGENT)]
        urllib2.install_opener(opener)

    @property
    def logger(self):
        """ Get logger """
        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger

    @property
    def cas_host(self):
        """ Get CAS host """
        return self._cas_host

    @cas_host.setter
    def cas_host(self, cas_host):
        self._logger.debug("set cas host: %s" % cas_host)
        self._cas_host = cas_host

    @property
    def cas_group(self):
        """ Get CAS group name """
        return self._cas_group

    @cas_group.setter
    def cas_group(self, cas_group):
        self._logger.debug("set cas group: %s" % cas_group)
        self._cas_group = cas_group

    @property
    def cas_username(self):
        """ Get CAS username """
        return self._cas_username

    @cas_username.setter
    def cas_username(self, cas_username):
        self._logger.debug("set cas usernmae: %s" % cas_username)
        self._cas_username = cas_username

    @property
    def cas_password(self):
        """ Get CAS password """
        return self._cas_password

    @cas_password.setter
    def cas_password(self, cas_password):
        self._logger.debug("set cas password: %s" % cas_password)
        self._cas_password = cas_password

    @property
    def tgt(self):
        """ Get Ticket Granting Ticket (TGT) """
        return self._tgt

    def login(self):
        """ Login CAS

        Grab the Ticket Granting Ticket (TGT)
        Reference : https://wiki.jasig.org/display/casum/restful+api

        Returns:
            str: The tgt granted, or None if failed.
        """
        try:
            if not self._tgt:
                self._tgt = self._request_tgt()
            return self._tgt
        except Exception as e:
            self._logger.error(e.message)
            self._logger.debug(traceback.format_exc())
            return None

    def _request_tgt(self):
        """ Get Ticket Grant Ticket
        """

        ticket_service = 'https://%s%s' % (self._cas_host, self.__cas_ticket_endpoint)
        raw_params = {
            'username': '%s\\%s' % (self._cas_group, self._cas_username),
            'password': self._cas_password
        }
        params = urllib.urlencode(raw_params)
        headers = self.__request_common_headers.copy()
        headers['Content-Length'] = len(params)

        req = urllib2.Request(ticket_service, data=params, headers=headers)
        res = urllib2.urlopen(req)

        if not (res.getcode() / 100) == 2:
            raise Exception("Authentication failed. Please check the host and authentication information.")

        location = res.info().getheader('Location')
        self._logger.debug('cas redirect location: %s' % location)

        tgt = location[location.rfind('/') + 1:]
        self._logger.debug('cas tgt: %s' % tgt)

        return tgt
