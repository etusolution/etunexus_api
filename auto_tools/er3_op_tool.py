#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import logging
import json

from etunexus.cas import *
from etunexus.emc import *
from etunexus.er import *
from etunexus.ei import *
from etunexus.enum import *

# ERIO
DEF_CAS_HOST = 'emc.online.etunexus.com'
DEF_EMC2_HOST = 'emc.online.etunexus.com'
DEF_ER3_HOST = 'erhome.online.etunexus.com'
SECURITY_CHECK = True
LOGGING_LEVEL = logging.INFO
# Testing
# DEF_CAS_HOST = 'sso.etu.im'
# DEF_EMC2_HOST = 'etumaster.etu.im'
# DEF_ER3_HOST = 'etumaster.etu.im'
# SECURITY_CHECK = False
# LOGGING_LEVEL = logging.INFO


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
    return answer if answer else default


class AuthInfo():
    """ The abstract base class for command handlers """

    def __init__(self):
        self.cas_host = DEF_CAS_HOST
        self.emc2_host = DEF_EMC2_HOST
        self.er3_host = DEF_ER3_HOST
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

            logger.info('\n[Input login info]')
            self.group = promise_prompt('Group: ')
            self.user = promise_prompt('User: ')
            self.password = promise_prompt('Password: ')
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
        logger.info('Existing data source. No need to add new user.')
        ds = matched_dss[0]
    else:
        ds_display = u'%s 行為資料' % group['displayName']
        ds_app_ids = [AppId.EMC, AppId.ER]
        ds_domain = '*'
        ds = DataSource(ds_name, ds_display, app_ids=ds_app_ids, content_type=DataSourceContentType.BEHAVIOR)
        ds.init_event_collector(ds_domain)
        logger.info('Adding data source (%s)...' % ds_name)
        ds = emc2.add_data_source(group, ds)
        logger.info('Done.')

    exporter_setting = ExporterSetting(True)
    emc2.update_exporter_setting(ds, exporter_setting)

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
        if len(exist_logic) == 0:
            logger.info('Adding logic (%s)...' % logic['name'])
            er3.add_logic(group, logic)
            logger.info('Done.')
        else:
            logger.info('Logic (%s) already exist. No need to add new.' % logic['name'])


def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    auth_info = AuthInfo()
    if not auth_info.prompt():
        return 1

    logger.info('Validating login info...')
    cas = CAS(auth_info.group, auth_info.user, auth_info.password, auth_info.cas_host, secure=SECURITY_CHECK)
    emc2 = EMC2(cas, auth_info.emc2_host)
    emc2.logger.setLevel(LOGGING_LEVEL)
    er3 = ER3(cas, auth_info.er3_host)
    er3.logger.setLevel(LOGGING_LEVEL)

    try:
        cas.login()
        emc2.login()
        er3.login()
    except:
        logger.error('Failed to connect to EMC or ER server. Please try again later.')
        return 2

    logger.info('Done.')

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
    except:
        logger.error('Failed to complete the process. Please check the error and try again.')
        return 2

# End of main

if __name__ == '__main__':
    sys.exit( main() )