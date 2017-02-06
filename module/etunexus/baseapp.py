# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
import logging
import traceback

from cas import CAS


class BaseApp(object):
    """ The base class for all etu nexus application API """

    # Constants
    __common_headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Pragma': 'no-cache'
    }

    __post_forms_headers = {
        'Content-type': 'application/x-www-form-urlencoded',
    }

    def __init__(self, cas, app_name, api_host, api_base, shiro_cas_base):
        """ Constructor

        Args:
            cas (object): A valid CAS instance
            app_name (str): The application name
            api_host (str): The host to make API request to
            api_base (str): The API base of the application
            shiro_cas_base (str): The shiro cas base of the application
        """

        assert cas and isinstance(cas, CAS)
        self._cas = cas
        assert app_name
        self._app_name = app_name
        assert api_host
        self._api_host = api_host
        assert api_base
        self._api_base = api_base
        assert shiro_cas_base
        self._shiro_cas_base = shiro_cas_base

        self._st = None
        self._logger = logging.getLogger('etu.nexus')

    @property
    def app_name(self):
        """ Get application name """
        return self._app_name

    @property
    def api_host(self):
        """ Get API Host """
        return self._api_host

    @api_host.setter
    def host(self, api_host):
        self._logger.debug("Set API host (%s)" % api_host)
        self._api_host = api_host

    @property
    def api_base(self):
        """ Get API base"""
        return self._api_base

    @property
    def logger(self):
        """ Get logger """
        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger

    def _resolve_cas_ticket_service(self):
        return 'https://{0}/cas/v1/tickets/{1}'.format(self._cas.cas_host, self._cas.tgt)

    def _resolve_shiro_url(self):
        return 'https://{0}{1}'.format(self._api_host, self._shiro_cas_base)

    def _resolve_shiro_validation_url(self):
        return '{0}?ticket={1}'.format(self._resolve_shiro_url(), self._st)

    def _resolve_api_url(self, api_postfix):
        return 'https://{0}{1}{2}'.format(self._api_host, self._api_base, api_postfix)

    def _request_st(self):
        # Grab a service ticket (ST) for app
        ticket_service = self._resolve_cas_ticket_service()
        raw_params = {
            'service': self._resolve_shiro_url()
        }
        params = urllib.urlencode(raw_params)
        headers = self.__common_headers.copy()
        headers['Content-Length'] = len(params)

        req = urllib2.Request(ticket_service, data=params, headers=headers)
        self._st = urllib2.urlopen(req).read()
        self.logger.debug('cas st (%s) for application (%s)' % (self._st, self._app_name))

        # Login service
        url = self._resolve_shiro_validation_url()
        try:
            urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            if e.getcode() != 403:
                raise e

    def _login_service(self):
        # Login service
        shiro_validation = self._resolve_shiro_validation_url()
        try:
            urllib2.urlopen(shiro_validation)
        except urllib2.HTTPError as e:
            if e.getcode() != 403:
                raise e

    def _check_login(self):
        if not self._st:
            self._logger.error('Please login service before firing API call.')
            raise Exception('Please login service before firing API call.')

    def login(self):
        """ Login service with valid CAS TGT

        Grab the Service Ticket (ST)
        Reference : https://wiki.jasig.org/display/casum/restful+api

        Returns:
            str: The st granted, or None if failed.
        """
        try:
            if not self._st:
                # Ensure login CAS done
                self._cas.login()
                # Make service login
                self._request_st()
                self._login_service()
            return self._st
        except Exception as e:
            self._logger.error(e.message)
            self._logger.debug(traceback.format_exc())
            del self._st
            raise e

    def logout(self):
        """ Logout service with cleaning granted Service Ticket """
        del self._st

    def _request(self, api, data=None, data_serialier=None, file=None, headers=None, method=None):
        if data:
            assert isinstance(data, dict)
        if data_serialier is None:
            data_serialier = json.dumps
        self._check_login()

        # Preparing data and headers if required
        url = self._resolve_api_url(api)

        final_headers = self.__common_headers.copy()
        if headers:
            final_headers.update(headers)

        final_data = None
        if data:
            if file:
                final_data = dict([(k, str(v)) for k, v in data.iteritems() if v is not None])
                # [IMPORTANT] Force transform all values to str while MultipartPostHandler append it with str directly.
                # /Library/Python/2.7/site-packages/MultipartPostHandler-0.1.0-py2.7.egg/MultipartPostHandler.pyc in multipart_encode(vars, files, boundary, buffer)
                # 91             buffer += '--%s\r\n' % boundary
                # 92             buffer += 'Content-Disposition: form-data; name="%s"' % key
                # ---> 93             buffer += '\r\n\r\n' + value + '\r\n'
                # 94         for(key, fd) in files:
                # 95             file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
                #
                # TypeError: cannot concatenate 'str' and 'int' objects

                final_data.update({'file': open(file, 'rb')})
                self._logger.debug('Upload file. The content length is calculated before sending request. Not set here.')
            else:
                final_data = data_serialier(data)
                self._logger.debug('Pure post data. Set content length to %d' % len(final_data))
                final_headers['Content-Length'] = len(final_data)
        else:
            self._logger.debug('No data in request. No content length set.')

        # fire api
        req = urllib2.Request(url, data=final_data, headers=final_headers)
        if method:
            req.get_method = lambda: method
        self._logger.info('%s %s' % (req.get_method(), url))
        self._logger.debug('Request header: %s' % str(req.headers))
        self._logger.debug("Request has body: %s. Request body: %s" %
                            (('Yes' if req.has_data() else 'No'), req.get_data()))

        res = urllib2.urlopen(req).read()
        self._logger.debug('Response: %s' % res)
        try:
            return json.loads(res)
        except ValueError as e:
            self._logger.error('%s error: Illegal response (%s) from server' % (traceback.extract_stack()[-3][2], res))
            raise e

    def request_get(self, api, headers=None):
        return self._request(api, headers=headers)

    def request_post(self, api, data, headers=None):
        return self._request(api, data=data, headers=headers)

    def request_post_form(self, api, data, headers=None):
        headers = {} if headers is None else headers.copy()
        headers.update(self.__post_forms_headers)
        return self._request(api, data=data, headers=headers,
                             data_serialier=lambda x: urllib.urlencode(x))

    def request_del(self, api, headers=None):
        return self._request(api, headers=headers, method='DELETE')

    def request_upload(self, api, data, file, headers=None):
        return self._request(api, data=data, file=file, headers=headers)

