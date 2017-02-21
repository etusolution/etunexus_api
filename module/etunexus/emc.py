# -*- coding: utf-8 -*-

import time
import json

from baseapp import BaseApp
from enum import *


class AppPermission(dict):
    """ Structure of an app permission.

    Fields:
        category (str): Permission category, refer to the valid values of each apps.
        id (str): Permission id, refer to each apps.
        level (int): FORBIDDEN (0), VIEW (1), SAVE (2), DELETE (3)
    """
    def __init__(self, category, id, level):
        assert category and id and level >= 0
        super(AppPermission, self).__init__({
            'category': category,
            'id': id,
            'level': level
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['category'], dict_obj['id'], dict_obj['level'])


class AppRole(dict):
    """ Structure of an app role.

    Fields:
        name (str): Role name, refer to 'AppRoleName' enum for valid values.
        permissions (list): List of AppPermission/dict.
    """
    def __init__(self, name, permissions):
        assert name and permissions and isinstance(permissions, list)
        super(AppRole, self).__init__({
            'name': name,
            'permissions': [x if isinstance(x, AppPermission) else AppPermission.from_dict(x) for x in permissions]
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['name'], dict_obj['permissions'])


class Group(dict):
    """ Structure of a group.

    Fields:
        name (str): The group id/name of.
        displayName (str): The group display name.
        id (int): The auto id of the group.
        createTime (long): The group create time.
    """
    def __init__(self, name, display_name, id=None, create_time=None):
        assert name and display_name
        super(Group, self).__init__({
            'name': name,
            'displayName': display_name,
            'id': id,
            'createTime': create_time
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['name'], dict_obj['displayName'], dict_obj.get('id'), dict_obj.get('createTime'))


class UserRole(dict):
    """ Structure of a user role.

    Fields:
        roleName (str): The role of the user in an application. Refer to 'AppRoleName' enum for valid values.
        appId (str): The application id. Refer to 'AppId' enum for valid values.
    """
    def __init__(self, role, app_id):
        assert role and app_id
        super(UserRole, self).__init__({
            'roleName': role,
            'appId': app_id
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['roleName'], dict_obj['appId'])


class User(dict):
    """ Structure of a user.

    Fields:
        name (str): The user login name (upper, lower, number, and underscore only).
        displayName (str): The user display name (human-readable).
        password (str): The password of the user.
        department (str): The department of the user (human-readable string).
        mail (str): The e-mail address of the user (human-readable string).
        roles (list): A list of UserRole instances representing the user roles in each application.

        id (int): The auto id of the user.
        createTime (long): The create time in Epoch (milliseconds).
        lastUpdateTime (long): The last update time in Epoch (milliseconds).
    """
    def __init__(self, name, display_name, password=None, department=None, mail=None, roles=None,
                 id=None, create_time=None, last_update_time=None):
        assert name and display_name
        if roles is None:
            roles = []
        assert isinstance(roles, list)
        if department is None:
            department = ''
        if mail is None:
            mail = ''
        super(User, self).__init__({
            'name': name,
            'displayName': display_name,
            'password': password,
            'department': department,
            'mail': mail,
            'roles': [x if isinstance(x, UserRole) else UserRole.from_dict(x) for x in roles],
            'id': id,
            'createTime': create_time,
            'lastUpdateTime': last_update_time
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['name'], dict_obj['displayName'], dict_obj.get('password'), dict_obj.get('department'),
                   dict_obj.get('mail'), dict_obj.get('roles'),
                   dict_obj.get('id'), dict_obj.get('createTime'), dict_obj.get('lastUpdateTime'))


class EventCollector(dict):
    """ Structure of Event Collector data source content.

    Fields:
        hostName (str): The host/domain name of the data source. Set wildcard (*) to accept data from all domains.
    """
    def __init__(self, hostname):
        assert hostname
        super(EventCollector, self).__init__({
            'hostName': hostname
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['hostName'])


class DataSource(dict):
    """ Structure of a data source.

    Fields:
        name (str): The data source id/name.
        displayName (str): The data source display name.
        appIds (list[str]): A list of authorized applications, refer to 'AppId' enum for valid values.
        contentType (str): The data source content type, refer to 'DataSourceContentType' enum for valid values
        type (str): The data source type (how to get data), refer to 'DataSourceType' enum for valid values

        eventCollector (obj): An EventCollector object if type is 'EVENT_COLLECTOR'
        importer (obj): An Importer object if type is 'IMPORTER'
        fetch (obj): An Fetch object if type is 'FETCH'
        upload (obj): An Upload object if type is 'UPLOAD'

        id (int): Data source auto id
        groupId (int): Group auto id
    """
    # TODO: importer, fetch, upload not supported yet
    def __init__(self, name, display_name, app_ids, content_type, id=None, group_id=None):
        super(DataSource, self).__init__({
            'name': name,
            'displayName': display_name,
            'appIds': app_ids,
            'contentType': content_type,
            'id': id,
            'groupId': group_id
        })

    def init_event_collector(self, hostname):
        """ Initialize the data source as Event Collector type.

        Arguments:
            hostname (str): The host/domain name of the data source. Set wildcard (*) to accept data from all domains.
        """
        event_collector = EventCollector(hostname)
        self.update({
            'type': DataSourceType.EVENT_COLLECTOR,
            'eventCollector': event_collector
        })

    def init_event_collector_from_dict(self, dict_obj):
        event_collector = EventCollector.from_dict(dict_obj)
        self.update({
            'type': DataSourceType.EVENT_COLLECTOR,
            'eventCollector': event_collector
        })

    @classmethod
    def from_dict(cls, dict_obj):
        new_obj = cls(dict_obj['name'], dict_obj['displayName'], dict_obj['appIds'], dict_obj['contentType'],
                      dict_obj.get('id'), dict_obj.get('groupId'))

        ds_type = dict_obj.get('type')
        if ds_type == DataSourceType.EVENT_COLLECTOR:
            new_obj.init_event_collector_from_dict(dict_obj['eventCollector'])

        return new_obj


class ExporterExtraSchema(dict):
    """ Structure for Extra Schema in Exporter Setting.

    Fields:
        name (str): Name/field of the schema.
        type (str): Type of the schema, e.g. string, int.
        link (str): The tuple key to explode. Set it to '' for first level event collector parameters.
    """

    def __init__(self, name, type, link):
        assert name and type and link is not None
        super(ExporterExtraSchema, self).__init__({
            'name': name,
            'type': type,
            'link': link
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['name'], dict_obj['type'], dict_obj['link'])


class ExporterSetting(dict):
    """ Structure for Exporter setting.

    Fields:
        enabled (bool): The exporter is enabled or not.
        initalConvetTime (long): The initial conversion time in Epoch (milliseconds). Default: now.
        tupleKey (str): The tuple key. Default: ptuple.
        extraSchema (object): The extra schema.
        parsingFormat (str): The input data format. Default: NginxPlusLogParserDriver.
        baseSchema (obj); The base/default schema.
        updateTime (long): The latest data export time in Epoch (milliseconds).

    NOTE:
        initalConvetTime is the legacy typo of "initialConversionTime".
    """
    def __init__(self, enabled, initial_convert_time=None,
                 tuple_key=None, extra_schema=None,
                 parsing_format=None, base_schema=None, update_time=None):
        assert enabled is not None
        if initial_convert_time is None:
            initial_convert_time = long(time.mktime(time.localtime())*1000)
        if not tuple_key:
            tuple_key = 'ptuple'
        if not extra_schema:
            extra_schema = []
        if not parsing_format:
            parsing_format = 'NginxPlusLogParserDriver'
        if not base_schema:
            base_schema = []

        extra_schema_list = [x if isinstance(x, ExporterExtraSchema) else ExporterExtraSchema.from_dict(x) for x in extra_schema]
        extra_schema_str = json.dumps(extra_schema_list)

        base_schema_list = [x if isinstance(x, ExporterExtraSchema) else ExporterExtraSchema.from_dict(x) for x in base_schema]
        base_schema_str = json.dumps(base_schema_list)

        super(ExporterSetting, self).__init__({
            'enabled': enabled,
            'initalConvetTime': long(initial_convert_time),
            'tupleKey': tuple_key,
            'extraSchema': extra_schema_str,
            'parsingFormat': parsing_format,
            'baseSchema': base_schema_str,
            'updateTime': update_time
        })

    @classmethod
    def from_dict(cls, dict_obj):
        extra_schema = None
        if 'extraSchema' in dict_obj:
            extra_schema = json.loads(dict_obj['extraSchema'])
        base_schema = None
        if 'baseSchema' in dict_obj:
            base_schema = json.loads(dict_obj['baseSchema'])
        return cls(dict_obj['enabled'], dict_obj.get('initalConvetTime'),
                   dict_obj.get('tupleKey'), extra_schema,
                   dict_obj.get('parsingFormat'), base_schema, dict_obj.get('updateTime'))


class EMC2(BaseApp):
    """ Encapsulate Etu Management Center (v2) API. """

    __APP_NAME = 'EMC2'
    __HOST = 'emc.online.etunexus.com'
    __API_BASE = '/commsrv/v1'
    __SHIRO_CAS_BASE = '/shiro-cas'

    def __init__(self, cas, host=None, api_base=None, shiro_cas_base=None):
        """ Constructor of EMC2 instance. """

        api_base = api_base if api_base else self.__API_BASE
        super(EMC2, self).__init__(cas, EMC2.__APP_NAME,
                                   api_host=host if host else self.__HOST,
                                   api_base=api_base if api_base else self.__API_BASE,
                                   shiro_cas_base=shiro_cas_base if shiro_cas_base else self.__SHIRO_CAS_BASE)

    # Group #
    def get_groups(self):
        """ Get group list.

        Arguments:
        Return:
            A list of Group instances.
        """
        res = self.request_get('/group')
        return [Group.from_dict(x) for x in res]

    def add_group(self, group):
        """ Add a new group.

        Arguments:
            group (obj): The Group instance to add.
        Return:
            A Group instance as the added one (with fields filled by server, e.g. createTime).
        """
        assert group and isinstance(group, Group)
        res = self.request_post('/group', group)
        return Group.from_dict(res)

    def update_group(self, group):
        """ Update a group.

        Arguments:
            group (obj): The Group instance to update, with valid "id".
        Return:
            A Group instance as the updated one.
        """
        assert group and isinstance(group, Group)
        group_id = group['id']
        res = self.request_post('/group/{0}'.format(group_id), group)
        return Group.from_dict(res)

    def del_group(self, group):
        """ Delete a group.

        Arguments:
            group (obj or int): The Group instance or group id to delete.
        Return:
            The group id deleted. It must be the same as the one in argument.
        """
        assert group
        group_id = group['id'] if isinstance(group, Group) else int(group)
        assert group_id
        res = self.request_del('/group/{0}'.format(group_id))
        assert res['groupId'] == group_id
        return res['groupId']

    # User #
    def me(self):
        """ Get "me" user instance

        Arguments:
        Return:
            A User instance as "me", the login user or simulated user
        """
        res = self.request_get('/user/me')
        return User.from_dict(res)

    def get_users(self, group):
        """ Get user list in a group.

        Arguments:
            group (obj or int): The Group instance or group id to get user list.
        Return:
            A list of User instances.
        """
        assert group
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_get('/group/{0}/user'.format(group_id))
        return [User.from_dict(x) for x in res]

    def add_user(self, group, user):
        """ Add a user into a group.

        Arguments:
            group (obj or int): The Group instance or group id to add the user into.
            user (obj): The User instance to add.
        Return:
            An User instance as the added one (with fields filled by server, e.g. createTime).
        """
        assert group and user and isinstance(user, User)
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_post('/group/{0}/user'.format(group_id), user)
        return User.from_dict(res)

    def update_user(self, user):
        """ Update an user.

        Do not use this method to change user password. Use "change_user_password()" instead.

        Arguments:
            user (obj): The User instance to update, with a valid "id".
        Return:
            An User instance as the updated one.
        """
        assert user and isinstance(user, User)
        user_id = user['id']
        res = self.request_post('/user/{0}'.format(user_id), user)
        return User.from_dict(res)

    def del_user(self, user):
        """ Delete an user.

        Arguments:
            user (obj or int): The User instance or user id to delete.
        Return:
            The user id deleted. It must be the same as the one in argument.
        """
        assert user
        user_id = user['id'] if isinstance(user, User) else int(user)
        res = self.request_del('/user/{0}'.format(user_id))
        assert res['userId'] == user_id
        return res['userId']

    def change_user_password(self, user, password):
        """ Change user password.

        For normal user, the "user" argument should be "me".
        For operator, the "user" can be another user in the same group.
        For admin, The "user" can be anyone in the system.

        Arguments:
            user (obj or int): The User instance or user id to change password.
            password (str): The new password to set.
        Return:
            The user id with password changed. It must be the same as the one in argument.
        """
        assert user and password
        user_id = user['id'] if isinstance(user, User) else int(user)
        params = {
            'password': password
        }
        res = self.request_post('/user/{0}/password'.format(user_id), params)
        assert res['userId'] == user_id
        return res['userId']

    # Apps #
    def get_apps(self):
        """ Get application list supported in the system.

        Arguments:
        Return:
            A list of applications (string), refer to "AppId" enum for the valid values.
        """
        return self.request_get('/app')

    def get_app_permission(self, app_id):
        """ Get application permission settings.

        Arguments:
            app_id (str): An application id, refer to "AppId" enum for the valid values.
        Return:
            A list of AppPermission instances as the setting of the given application.
        """
        assert app_id
        res = self.request_get('/app/{0}/permission'.format(app_id))
        assert (res['appId'] == app_id)
        return [AppPermission.from_dict(x) for x in res['permissions']]

    def get_app_roles(self, app_id):
        """ Get application role and permission settings.

        Arguments:
            app_id (str): An application id, refer to "AppId" enum for the valid values.
        Return:
            A list of AppRole instances as the role setting of the given application.
        """
        assert app_id
        res = self.request_get('/app/{0}/role'.format(app_id))
        return [AppRole.from_dict(x) for x in res]

    def update_app_role(self, app_id, app_role):
        """ Update a role and permission setting in an application.

        Arguments:
            app_id (str): An application id, refer to "AppId" enum for the valid values.
            app_role (obj): The AppRole instance to update.
        Return:
            An AppRole as the as the updated one.
        """
        assert app_id and app_role and isinstance(app_role, AppRole)
        res = self.request_post('/app/{0}/role'.format(app_id), app_role)
        return AppRole.from_dict(res)

    # Data source #
    def get_data_sources(self, group):
        """ Get data source list in a group.

        Arguments:
            group (obj or int): The Group instance or group id to get.
        Return:
            A list of DataSource instances.
        """
        assert group
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_get('/group/{0}/data-source'.format(group_id))
        return [DataSource.from_dict(x) for x in res]

    def add_data_source(self, group, data_source):
        """ Add a data source to a group.

        To add a new data source, first create and initialize a DataSource instance before calling. During initializing
        data source, not only "new" an instance but need to call the proper "init_xxx()" method as requested.

        Arguments:
            group (obj or int): The Group instance or group id to get.
            data_source (object): The DataSource instance to add.
        Return:
            A DataSource instance as the added one.
        """
        assert data_source and isinstance(data_source, DataSource)
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_post('/group/{0}/data-source'.format(group_id), data_source)
        return DataSource.from_dict(res)

    def update_data_source(self, data_source):
        """ Update a data source.

        Arguments:
            data_source (obj): The DataSource instance to update, with valid "id".
        Return:
            A DataSource instance as the updated one.
        """
        assert data_source and isinstance(data_source, DataSource)
        source_id = data_source['id']
        assert source_id
        res = self.request_post('/data-source/{0}'.format(source_id), data_source)
        return DataSource.from_dict(res)

    def del_data_source(self, data_source):
        """ Delete a data source.

        Arguments:
            data_source (obj or int): The DataSource instance or data source id to delete.
        Return:
            The data source id deleted. It must be the same as the one in argument.
        """
        assert data_source
        source_id = data_source['id'] if isinstance(data_source, DataSource) else int(data_source)
        assert source_id
        res = self.request_del('/data-source/{0}'.format(source_id))
        assert res == source_id
        return res

    # Exporter setting #
    def get_exporter_setting(self, data_source):
        """ Get Exporter setting of an event collector type data source.

        As the input argument accepts a generic data source id, this function does not check if the data source is
        really "event collector" type. The caller SHOULD ensure the data source is eligible for configuring exporter.

        Arguments:
            data_source (obj or int): The DataSource instance or data source id to get exporter setting.
        Return:
            An ExporterSetting instance.
        """
        assert data_source
        source_id = data_source['id'] if isinstance(data_source, DataSource) else int(data_source)
        res = self.request_get('/data-source/{0}/exporter'.format(source_id))
        return ExporterSetting.from_dict(res)

    def update_exporter_setting(self, data_source, exporter_setting):
        """ Update Exporter setting of an event collector type data source.

        As the input argument accepts a generic data source id, this function does not check if the data source is
        really "event collector" type. The caller SHOULD ensure the data source is eligible for configuring exporter.

        Arguments:
            data_source (obj or int): The DataSource instance or data source id to get exporter setting.
            exporter_setting (obj): The ExporterSetting instance to apply to the data source.
        Return:
            An ExporterSetting instance as the applied one.
        """
        assert data_source and  exporter_setting and isinstance(exporter_setting, ExporterSetting)
        source_id = data_source['id'] if isinstance(data_source, DataSource) else int(data_source)
        assert source_id
        res = self.request_post('/data-source/{0}/exporter'.format(source_id), exporter_setting)
        return ExporterSetting.from_dict(res)
