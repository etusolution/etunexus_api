#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import logging
import json
import getpass

from etunexus.cas import *
from etunexus.emc import *
from etunexus.er import *
from etunexus.ei import *
from etunexus.enum import *

if False:
    # ERIO
    DEF_CAS_HOST = 'emc.online.etunexus.com'
    DEF_EMC2_HOST = 'emc.online.etunexus.com'
    DEF_ER3_HOST = 'erhome.online.etunexus.com'
    SECURITY_CHECK = True
    LOGGING_LEVEL = logging.INFO
else:
    # 219 Testing
    DEF_CAS_HOST = 'sso.etu.im'
    DEF_EMC2_HOST = 'etumaster.etu.im'
    DEF_ER3_HOST = 'etumaster.etu.im'
    SECURITY_CHECK = False
    LOGGING_LEVEL = logging.INFO

app_name = 'Etu Recommender'

logger = logging.getLogger('er3_op_tool')
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(stream_handler)


def promise_prompt(prompt, default=None):
    answer = None
    while answer is None or (not answer and not default):
        answer = raw_input(prompt)
    return unicode(answer, encoding=sys.stdin.encoding) if answer else default


class AuthInfo():
    """ Keep the authentication info """

    def __init__(self):
        self.cas_host = DEF_CAS_HOST
        self.emc2_host = DEF_EMC2_HOST
        self.er3_host = DEF_ER3_HOST
        self.security_check = SECURITY_CHECK
        self.group = ''
        self.user = ''
        self.password = ''
        pass

    def prompt(self):
        try:
            logger.info('[Input host info]')
            self.cas_host = promise_prompt('Please input single sign-on host [%s]: ' % DEF_CAS_HOST, DEF_CAS_HOST)
            self.emc2_host = promise_prompt('Please input EMC2 host [%s]: ' % DEF_EMC2_HOST, DEF_EMC2_HOST)
            self.er3_host = promise_prompt('Please input ER3 host [%s]: ' % DEF_ER3_HOST, DEF_ER3_HOST)

            if self.cas_host != DEF_CAS_HOST:
                skip_security_check = promise_prompt('Skip security check (Y/n) [n]?', 'n')
                if skip_security_check.lower() == 'y':
                    self.security_check = False

            logger.info('\n[Input login info]')
            self.group = promise_prompt('Group: ')
            self.user = promise_prompt('User: ')
            self.password = getpass.getpass('Password: ')
            return True
        except KeyboardInterrupt, ki:
            return False

    @property
    def emc2_host(self):
        return self.emc2_host

    @property
    def er3_host(self):
        return self.er3_host

    @property
    def security_check(self):
        return self.security_check

    @property
    def group(self):
        return self.group

    @property
    def user(self):
        return self.user

    @property
    def password(self):
        return self.password


def add_new_group(emc2):
    group_name = promise_prompt('Please input customer group name: ')

    groups = emc2.get_groups()
    matched_groups = filter(lambda x: x['name'] == group_name, groups)
    if len(matched_groups) > 0:
        answer = promise_prompt('There has been a group named (%s) exist. Do you want to continue to use it (Y/n) [n]? '
                                % group_name, 'n')
        if answer.lower() != 'y':
            return None

        logger.info('Using existing group.')
        group = matched_groups[0]
    else:
        group_display_name = promise_prompt('Please input group display name: ')

        group = Group(group_name, group_display_name)
        logger.info('Adding new group (%s)...' % group_name)
        group = emc2.add_group(group)
        logger.info('Done.')

    return group


def add_new_user(emc2, group):
    user_name = '%s_user' % group['name']

    users = emc2.get_users(group)
    matched_users = filter(lambda x: x['name']==user_name, users)

    if len(matched_users) > 0:
        logger.info('Existing user. No need to add new user.')
        user = matched_users[0]

        # Check the user is ER-authorized
        user_roles = user['roles']
        if len(filter(lambda x: x['appId'] == AppId.ER, user_roles)) == 0:
            logger.info('But the user is not ER-authorized. Adding the authorization...')
            user['roles'].append(UserRole(AppRoleName.VIEWER, AppId.ER))
            emc2.update_user(user)
            logger.info('Done.')
        else:
            logger.info('The user is also ER-authorized.')

    else:
        user_password = 'etu_%s' % group['name']
        user_display = group['displayName']
        user_roles = [UserRole(AppRoleName.VIEWER, AppId.ER)]
        user = User(user_name, user_display, user_password, roles=user_roles)
        logger.info('Adding new user (%s)...' % user_name)
        user = emc2.add_user(group, user)
        logger.info('Done.')

    return user


def add_new_data_source(emc2, group):
    ds_name = '%srec' % group['name']

    dss = emc2.get_data_sources(group)
    matched_dss = filter(lambda x: x['name']==ds_name, dss)
    if len(matched_dss) > 0:
        logger.info('Existing data source. No need to add new one.')
        ds = matched_dss[0]

        # Check the data source is ER-authorized
        ds_app_ids = ds['appIds']
        if len(filter(lambda x: x == AppId.ER, ds_app_ids)) == 0:
            logger.info('But the data source is not ER-authorized. Adding the authorization...')
            ds['appIds'].append(AppId.ER)
            emc2.update_data_source(ds)
            logger.info('Done.')
        else:
            logger.info('The data source is also ER-authorized.')

    else:
        ds_display = u'%s 行為資料' % group['displayName']
        ds_app_ids = [AppId.EMC, AppId.ER]
        ds_domain = '*'
        ds = DataSource(ds_name, ds_display, app_ids=ds_app_ids, content_type=DataSourceContentType.BEHAVIOR)
        ds.init_event_collector(ds_domain)
        logger.info('Adding data source (%s)...' % ds_name)
        ds = emc2.add_data_source(group, ds)
        logger.info('Done.')

    logger.info('Setting exporter...')
    exporter_setting = ExporterSetting(True)
    emc2.update_exporter_setting(ds, exporter_setting)
    logger.info('Done.')

    return ds


def add_new_logics(er3, group, data_source):
    logics = er3.get_logics(group)

    # Add all new logics with checking existed or not
    group_name = group['name']
    new_logics = [
        Logic(name='%s_rank-cat' % group_name,
              display_name='%s rank-cat' % group_name,
              active=True,
              rec_count=20,
              alg_type=LogicAlgType.RANK,
              alg_instances=[
                  Alg_RANKING(1, data_source, 3, [EventAction.VIEW, EventAction.ORDER])
              ]),
        Logic(name='%s_user' % group_name,
              display_name='%s user' % group_name,
              active=True,
              rec_count=20,
              alg_type=LogicAlgType.USER_BASE,
              alg_instances=[
                  Alg_USER_BASED_CF(1, data_source, 3, [EventAction.VIEW, EventAction.ORDER])
              ],
              complementary_logics='%s_rank-cat' % group_name
              ),
        Logic(name='%s_item' % group_name,
              display_name='%s item' % group_name,
              active=True,
              rec_count=20,
              alg_type=LogicAlgType.ITEM_BASE,
              alg_instances=[
                  Alg_ITEM_BASED_CF(1, data_source, 3, [EventAction.VIEW, EventAction.ORDER])
              ],
              complementary_logics='%s_rank-cat' % group_name
              )
    ]
    for logic in new_logics:
        exist_logic = filter(lambda x: x['name'] == logic['name'], logics)
        if len(exist_logic) > 0:
            logger.info('Logic (%s) already exist. No need to add new one.' % logic['name'])

            # The filter result is a list. get the first element for further check.
            exist_logic = exist_logic[0]

            # Check if the logic is enabled.
            if not exist_logic['active']:
                logger.info('Logic (%s) is not enabled. Active it...' % exist_logic['name'])
                exist_logic['active'] = True
                er3.update_logic(exist_logic)
                logger.info('Done.')
        else:
            logger.info('Adding logic (%s)...' % logic['name'])
            er3.add_logic(group, logic)
            logger.info('Done.')


def func_new_customer(emc2, er3):
    try:
        while (True):
            new_group = add_new_group(emc2)
            if new_group is not None:
                new_user = add_new_user(emc2, new_group)
                new_ds = add_new_data_source(emc2, new_group)
                add_new_logics(er3, new_group, new_ds)

            go_next = promise_prompt('Do you want to create another one (Y/n) [n]? ', 'n')
            if go_next.lower() != 'y':
                break
    except KeyboardInterrupt, ki:
        return 1
    except Exception, e:
        logger.error('Failed to complete the process. Please check the error and try again.')
        logger.error('Error message: ' + str(e))
        return 2

    return 0


def get_exist_group(emc2):
    group_name = promise_prompt('Please input customer group name: ')
    groups = emc2.get_groups()
    matched_groups = filter(lambda x: x['name'] == group_name, groups)
    if len(matched_groups) == 0:
        logger.warn('Group (%s) does not exist. Please check and try again.' % group_name)
        return None

    group = matched_groups[0]
    return group


def suspend_logics(er3, suspend_group):
    logics = er3.get_logics(suspend_group)
    for logic in logics:
        logic['active'] = False
        logger.info('Suspend recommendation Logic (%s)...' % logic['name'])
        er3.update_logic(logic)
        logger.info('Done.')


def suspend_datasource(emc2, suspend_group):
    dss = emc2.get_data_sources(suspend_group)
    for ds in dss:
        logger.info('Checking data source (%s)...' % ds['name'])

        if AppId.ER in ds['appIds']:
            ds['appIds'].remove(AppId.ER)
            logger.info('Removing ER authorization for data source (%s)...' % ds['name'])
            emc2.update_data_source(ds)
            logger.info('Done.')
        else:
            logger.info('Data source (%s) is not ER authorized.' % ds['name'])

        disable_exporter = True if len(ds['appIds']) == 0 \
            else True if len(ds['appIds']) == 1 and ds['appIds'][0] == AppId.EMC \
            else False
        if disable_exporter:
            exporter_setting = emc2.get_exporter_setting(ds)
            exporter_setting['enabled'] = False
            logger.info('No other application uses it. Disabling exporter for data source (%s)...' % ds['name'])
            emc2.update_exporter_setting(ds, exporter_setting)
            logger.info('Done.')
        else:
            logger.info('Other application is still using it. Do not disable exporter.')


def remove_user(emc2, suspend_group):
    users = emc2.get_users(suspend_group)
    for user in users:
        logger.info('Removing ER authorization from user (%s).' % user['name'])
        user['roles'] = filter(lambda x: x['appId'] != AppId.ER, user['roles'])
        if len(user['roles']) == 0:
            logger.info('No other application authorization. Removing user (%s)...' % user['name'])
            emc2.del_user(user)
            logger.info('Done.')
        else:
            logger.info('Updating user (%s)...' % user['name'])
            emc2.update_user(user)
            logger.info('Done.')


def func_suspend_customer(emc2, er3):
    try:
        while True:
            suspend_group = get_exist_group(emc2)
            if suspend_group is not None:
                suspend_logics(er3, suspend_group)
                suspend_datasource(emc2, suspend_group)
                remove_user(emc2, suspend_group)

            go_next = promise_prompt('Do you want to suspend another one (Y/n) [n]? ', 'n')
            if go_next.lower() != 'y':
                break
    except KeyboardInterrupt, ki:
        return 1
    except Exception, e:
        logger.error('Failed to complete the process. Please check the error and try again.')
        logger.error('Error message: ' + str(e))
        return 2

    return 0


def func_exit():
    return 0


class Menu(object):

    class Option(object):
        def __init__(self, menu_key, menu_display, menu_func, func_args=None):
            self._menu_key = menu_key
            self._menu_display = menu_display
            self._menu_func = menu_func
            self._func_args = func_args if func_args is not None else []

        @property
        def menu_key(self):
            return self._menu_key

        @property
        def menu_display(self):
            return self._menu_display

        @property
        def menu_func(self):
            return self._menu_func

        @property
        def func_args(self):
            return self._func_args

    def __init__(self, title):
        self._title = title
        self._options = []
        self._indicator = ">>> "

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def indicator(self):
        return self._indicator

    @indicator.setter
    def indicator(self, value):
        self._indicator = value

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self._options = value

    @staticmethod
    def cls():
        os.system('cls' if os.name == 'nt' else 'clear')

    def show(self):
        print self.title
        print
        for option in self.options:
            print '{0}) {1}'.format(option.menu_key, option.menu_display)
        print

    def input(self):
        selected = promise_prompt(self.indicator)
        for option in self.options:
            if option.menu_key.lower() == selected.lower():
                return option

        return None

    def open(self):
        option = None

        ret = None
        while option is None:
            self.show()
            option = self.input()
            if option is not None:
                ret = option.menu_func(*option.func_args)

        return ret


def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    logger.info('*' * (len(app_name)+4))
    logger.info('* ' + app_name + ' *')
    logger.info('*' * (len(app_name)+4))

    auth_info = AuthInfo()
    if not auth_info.prompt():
        return 1

    logger.info('Validating login info...')
    cas = CAS(auth_info.group, auth_info.user, auth_info.password, auth_info.cas_host, secure=auth_info.security_check)
    emc2 = EMC2(cas, auth_info.emc2_host)
    emc2.logger.setLevel(LOGGING_LEVEL)
    er3 = ER3(cas, auth_info.er3_host)
    er3.logger.setLevel(LOGGING_LEVEL)

    try:
        cas.login()
        emc2.login()
        er3.login()
    except Exception, e:
        logger.error('Failed to connect to EMC or ER server. Please try again later.')
        logger.error('Error message: ' + str(e))
        return 2

    logger.info('Done.')

    main_menu = Menu('Please select the function to proceed: ')
    main_menu.options = [
        Menu.Option('1', 'Add/Resume a customer', func_new_customer, [emc2, er3]),
        Menu.Option('2', 'Suspend a customer', func_suspend_customer, [emc2, er3]),
        Menu.Option('E', 'Exit', func_exit)
    ]
    return main_menu.open()


# End of main

if __name__ == '__main__':
    sys.exit( main() )
