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

# ERIO
DEF_CAS_HOST = 'emc.online.etunexus.com'
DEF_EMC2_HOST = 'emc.online.etunexus.com'
DEF_EI3_HOST = 'eihome.online.etunexus.com'
SECURITY_CHECK = True
LOGGING_LEVEL = logging.INFO
# Testing
# DEF_CAS_HOST = 'sso.etu.im'
# DEF_EMC2_HOST = 'etumaster.etu.im'
# DEF_EI3_HOST = 'etumaster.etu.im'
# SECURITY_CHECK = False
# LOGGING_LEVEL = logging.INFO

app_name = 'Etu Insight'

logger = logging.getLogger('ei3_op_tool')
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
    """ Keep the authentication info """

    def __init__(self):
        self.cas_host = DEF_CAS_HOST
        self.emc2_host = DEF_EMC2_HOST
        self.ei3_host = DEF_EI3_HOST
        self.group = ''
        self.user = ''
        self.password = ''
        pass

    def prompt(self):
        try:
            logger.info('[Input host info]')
            self.cas_host = promise_prompt('Please input single sign-on host [%s]: ' % DEF_CAS_HOST, DEF_CAS_HOST)
            self.emc2_host = promise_prompt('Please input EMC2 host [%s]: ' % DEF_EMC2_HOST, DEF_EMC2_HOST)
            self.ei3_host = promise_prompt('Please input EI3 host [%s]: ' % DEF_EI3_HOST, DEF_EI3_HOST)

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
    def ei3_host(self):
        return self.ei3_host

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

        # Check the user is EI-authorized
        user_roles = user['roles']
        if len(filter(lambda x: x['appId'] == AppId.EI, user_roles)) == 0:
            logger.info('But the user is not ER-authorized. Adding the authorization...')
            user['roles'].append(UserRole(AppRoleName.VIEWER, AppId.EI))
            emc2.update_user(user)
            logger.info('Done.')
        else:
            logger.info('The user is also EI-authorized.')

    else:
        user_password = 'etu_%s' % group['name']
        user_display = group['displayName']
        user_roles = [UserRole(AppRoleName.VIEWER, AppId.EI)]
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


def add_new_bands(ei3, group, user, data_source):
    ei3.do_su_login(group, user)

    # Get all band categories of the simulated user
    categories = ei3.get_band_categories()

    # Add all new band categories with checking existed or not
    new_band_categories = [
        BandCategory(name=u'1.活躍客群統計'),
        BandCategory(name=u'2.潛力消費名單'),
        BandCategory(name=u'3.顧客價值分群'),
        BandCategory(name=u'4.核心關注客群'),
        BandCategory(name=u'客戶解析(7日)'),
        BandCategory(name=u'客戶解析(30日)'),
        BandCategory(name=u'客戶解析(90日)'),
        BandCategory(name=u'客戶消費力'),
    ]
    for category in new_band_categories:
        exist_category = filter(lambda x: x['name'] == category['name'], categories)
        if len(exist_category) > 0:
            logger.info('Category (%s) already exist. No need to add new.' % category['name'])
        else:
            logger.info('Adding category (%s)...' % category['name'])
            ei3.add_band_category(category)
            logger.info('Done.')

    # Re-query categories to get complete info
    categories = ei3.get_band_categories()
    cat_dict = {x['name']: x for x in categories}
    bands = [bands for cat in categories for bands in cat['bands']]

    gene_bands = [
        # 客戶解析(7日)
        Band(category=cat_dict[u'客戶解析(7日)'], name=u'7日內總訪客數', description='',type=BandType.GENE,
             target_gene=BandGene('Login_7', data_source, BandGeneOperator.GE, '1')),
        Band(category=cat_dict[u'客戶解析(7日)'], name=u'7日內曾消費客戶', description='',type=BandType.GENE,
             target_gene=BandGene('Orders_7', data_source, BandGeneOperator.GE, '1')),
        Band(category=cat_dict[u'客戶解析(7日)'], name=u'昨日曾消費', description='',type=BandType.GENE,
             target_gene=BandGene('Orders_1', data_source, BandGeneOperator.GE, '1')),
        # 客戶解析(30日)
        Band(category=cat_dict[u'客戶解析(30日)'], name=u'30日內總訪客數', description='',type=BandType.GENE,
             target_gene=BandGene('Login_30', data_source, BandGeneOperator.GE, '1')),
        Band(category=cat_dict[u'客戶解析(30日)'], name=u'最近30天造訪3次以上', description='',type=BandType.GENE,
             target_gene=BandGene('Session_30', data_source, BandGeneOperator.GE, '3')),
        Band(category=cat_dict[u'客戶解析(30日)'], name=u'30日內曾消費客戶', description='',type=BandType.GENE,
             target_gene=BandGene('Orders_30', data_source, BandGeneOperator.GE, '1')),
        # 客戶解析(90日)
        Band(category=cat_dict[u'客戶解析(90日)'], name=u'90日內總訪客數', description='',type=BandType.GENE,
             target_gene=BandGene('Login_90', data_source, BandGeneOperator.GE, '1')),
        Band(category=cat_dict[u'客戶解析(90日)'], name=u'最近90天造訪3次以上', description='',type=BandType.GENE,
             target_gene=BandGene('Session_30', data_source, BandGeneOperator.GE, '3')),
        Band(category=cat_dict[u'客戶解析(90日)'], name=u'90日內曾消費客戶', description='',type=BandType.GENE,
             target_gene=BandGene('Orders_90', data_source, BandGeneOperator.GE, '1')),
        # 客戶消費力
        Band(category=cat_dict[u'客戶消費力'], name=u'消費力前20%', description='',type=BandType.GENE,
             target_gene=BandGene('RevenueDist_30', data_source, BandGeneOperator.GE, '80')),
        Band(category=cat_dict[u'客戶消費力'], name=u'訂單數大於等於平均', description='',type=BandType.GENE,
             target_gene=BandGene('Orders_90', data_source, BandGeneOperator.GE, '2')),
        Band(category=cat_dict[u'客戶消費力'], name=u'訂單數小於平均', description='',type=BandType.GENE,
             target_gene=BandGene('Orders_90', data_source, BandGeneOperator.LT, '2')),
        Band(category=cat_dict[u'客戶消費力'], name=u'消費金額大於等於平均', description='',type=BandType.GENE,
             target_gene=BandGene('RevenueAvg_90', data_source, BandGeneOperator.GE, '250')),
        Band(category=cat_dict[u'客戶消費力'], name=u'消費金額小於平均', description='',type=BandType.GENE,
             target_gene=BandGene('RevenueAvg_90', data_source, BandGeneOperator.LT, '250')),
        # 1.活躍客群統計
        Band(category=cat_dict[u'1.活躍客群統計'], name=u'昨日訪客數', description='',type=BandType.GENE,
             target_gene=BandGene('Login_7', data_source, BandGeneOperator.GE, '1')),
        # 4.核心關注客群
        Band(category=cat_dict[u'4.核心關注客群'], name=u'高度貢獻客群', description='',type=BandType.GENE,
             target_gene=BandGene('RevenueDist_90', data_source, BandGeneOperator.GE, '95')),
    ]
    for band in gene_bands:
        exist_band = filter(lambda x: x['categoryId'] == band['categoryId'] and x['name'] == band['name'], bands)
        if len(exist_band) > 0:
            logger.info('Band (%s) already exist. No need to add new.' % band['name'])
        else:
            logger.info('Adding band (%s)...' % band['name'])
            ei3.add_band(band)
            logger.info('Done.')

    # Re-query categories to get complete info
    categories = ei3.get_band_categories()
    cat_dict = {x['name']: x for x in categories}
    bands = [bands for cat in categories for bands in cat['bands']]
    band_id_dict = {x['name']: x['id'] for x in bands}

    combine_bands = [
        # 1.活躍客群統計
        Band(category=cat_dict[u'1.活躍客群統計'], name=u'新沉睡戶客群', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'7日內總訪客數'], band_id_dict[u'昨日訪客數']], [BandCombineOperator.EXCEPT])),
        Band(category=cat_dict[u'1.活躍客群統計'], name=u'沉睡客群', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'30日內總訪客數'], band_id_dict[u'7日內總訪客數']], [BandCombineOperator.EXCEPT])),
        Band(category=cat_dict[u'1.活躍客群統計'], name=u'流失客群', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'90日內總訪客數'], band_id_dict[u'90日內總訪客數']], [BandCombineOperator.EXCEPT])),
        # 2.潛力消費名單
        Band(category=cat_dict[u'2.潛力消費名單'], name=u'昨日無消費', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'昨日訪客數'], band_id_dict[u'昨日曾消費']], [BandCombineOperator.EXCEPT])),
        Band(category=cat_dict[u'2.潛力消費名單'], name=u'近7日無消費', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'7日內總訪客數'], band_id_dict[u'7日內曾消費客戶']], [BandCombineOperator.EXCEPT])),
        Band(category=cat_dict[u'2.潛力消費名單'], name=u'近30日無消費', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'30日內總訪客數'], band_id_dict[u'30日內曾消費客戶']], [BandCombineOperator.EXCEPT])),
        Band(category=cat_dict[u'2.潛力消費名單'], name=u'近90日無消費', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'90日內總訪客數'], band_id_dict[u'90日內曾消費客戶']], [BandCombineOperator.EXCEPT])),
        # 3.顧客價值分群
        Band(category=cat_dict[u'3.顧客價值分群'], name=u'優質客群', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'訂單數大於等於平均'], band_id_dict[u'消費金額大於等於平均']], [BandCombineOperator.INTERSECT])),
        Band(category=cat_dict[u'3.顧客價值分群'], name=u'提升客單價客群', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'訂單數大於等於平均'], band_id_dict[u'消費金額小於平均']], [BandCombineOperator.INTERSECT])),
        Band(category=cat_dict[u'3.顧客價值分群'], name=u'提升消費頻次客群', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'訂單數小於平均'], band_id_dict[u'消費金額大於等於平均']], [BandCombineOperator.INTERSECT])),
        Band(category=cat_dict[u'3.顧客價值分群'], name=u'即將流失客群', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'訂單數小於平均'], band_id_dict[u'消費金額小於平均']], [BandCombineOperator.INTERSECT])),
        # 4.核心關注客群
        Band(category=cat_dict[u'4.核心關注客群'], name=u'近期關注客群', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'最近30天造訪3次以上'], band_id_dict[u'90日內曾消費客戶']], [BandCombineOperator.INTERSECT])),
        Band(category=cat_dict[u'4.核心關注客群'], name=u'重要挽留客群', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'消費力前20%'], band_id_dict[u'最近30天造訪3次以上']], [BandCombineOperator.EXCEPT])),
        Band(category=cat_dict[u'4.核心關注客群'], name=u'重點發展客群', description='', type=BandType.COMBINE,
             target_band=BandCombine([band_id_dict[u'消費力前20%'], band_id_dict[u'最近90天造訪3次以上']], [BandCombineOperator.INTERSECT])),
    ]
    for band in combine_bands:
        exist_band = filter(lambda x: x['categoryId'] == band['categoryId'] and x['name'] == band['name'], bands)
        if len(exist_band) > 0:
            logger.info('Band (%s) already exist. No need to add new.' % band['name'])
        else:
            logger.info('Adding band (%s)...' % band['name'])
            ei3.add_band(band)
            logger.info('Done.')

    ei3.do_su_logout()


def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    logger.info('*' * (len(app_name)+4))
    logger.info('* ' + app_name + ' *')
    logger.info('*' * (len(app_name)+4))

    auth_info = AuthInfo()
    if not auth_info.prompt():
        return 1

    logger.info('Validating login info...')
    cas = CAS(auth_info.group, auth_info.user, auth_info.password, auth_info.cas_host, secure=SECURITY_CHECK)
    emc2 = EMC2(cas, auth_info.emc2_host)
    emc2.logger.setLevel(LOGGING_LEVEL)
    ei3 = EI3(cas, auth_info.ei3_host)
    ei3.logger.setLevel(LOGGING_LEVEL)

    try:
        cas.login()
        emc2.login()
        ei3.login()
    except Exception, e:
        logger.error('Failed to connect to EMC or EI server. Please try again later.')
        logger.error('Error message: ' + str(e))
        return 2

    logger.info('Done.')

    try:
        while True:
            new_group = add_new_group(emc2)
            if new_group is not None:
                new_user = add_new_user(emc2, new_group)
                new_ds = add_new_data_source(emc2, new_group)
                add_new_bands(ei3, new_group, new_user, new_ds)

            go_next = promise_prompt('Do you want to create another one (Y/n) [n]? ', 'n')
            if go_next.lower() != 'y':
                break
    except KeyboardInterrupt, ki:
        return 1
    except Exception, e:
        logger.error('Failed to complete the process. Please check the error and try again.')
        logger.error('Error message: ' + str(e))
        return 2

# End of main

if __name__ == '__main__':
    sys.exit( main() )
