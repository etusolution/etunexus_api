#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import logging
import argparse

from etunexus.cas import *
from etunexus.emc import *
from etunexus.ei import *
from etunexus.enum import *


if True:
    # ERIO
    DEF_CAS_HOST = 'emc.online.etunexus.com'
    DEF_EMC2_HOST = 'emc.online.etunexus.com'
    DEF_EI3_HOST = 'eihome.online.etunexus.com'
    SECURITY_CHECK = True
    LOGGING_LEVEL = logging.INFO
else:
    # 219 Testing
    DEF_CAS_HOST = 'ziq.etu.im'
    DEF_EMC2_HOST = 'ziq.etu.im'
    DEF_EI3_HOST = 'ziq.etu.im'
    SECURITY_CHECK = False
    LOGGING_LEVEL = logging.DEBUG


logger = logging.getLogger('ei3_op_update_bands.py')
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(LOGGING_LEVEL)
stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s [EI3 Update Bands] %(message)s'))
logger.addHandler(stream_handler)


class AuthInfo():
    """ Keep the authentication info """

    def __init__(self, group, user, password):
        self.cas_host = DEF_CAS_HOST
        self.emc2_host = DEF_EMC2_HOST
        self.ei3_host = DEF_EI3_HOST
        self.security_check = SECURITY_CHECK
        self.group = group
        self.user = user
        self.password = password
        pass

    @property
    def emc2_host(self):
        return self.emc2_host

    @property
    def ei3_host(self):
        return self.ei3_host

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


# Exceptions
class NotFoundError(RuntimeError):
    """ Resource not found. """
    def __init__(self, message):
        self.message = message


class NotAuthorizedError(RuntimeError):
    """ Resource not authorized. """
    def __init__(self, message):
        self.message = message


# Utilities
def find_default_data_source(emc2, group):
    def_ds_name = '%srec' % group['name']

    dss = emc2.get_data_sources(group)
    def_ds = filter(lambda ds: ds['name'] == def_ds_name, dss)
    if not def_ds:
        raise NotFoundError('...No default data source in the group. Skip it.')
    return def_ds[0]


def _filter_bands(all_bands, band_names, find_all):
    flatted_bands = [band for band_category in all_bands for band in band_category['bands']]
    filtered_bands = filter(lambda band: band['name'] in band_names, flatted_bands)
    if find_all and len(filtered_bands) <> len(band_names):
        raise NotFoundError('...Not all bands (%s) found in the group op. Skip it.' % str(band_names))
    return filtered_bands


def find_default_bands(ei3, data_source, band_names, find_all=True):
    def_band_categories = ei3.get_default_bandcategories(data_source)
    return _filter_bands(def_band_categories, band_names, find_all)


def find_op_bands(ei3, band_names, find_all=True):
    op_bands = ei3.get_band_categories()
    return _filter_bands(op_bands, band_names, find_all)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--group', help='The group of the op user.', required=True)
    parser.add_argument('-u', '--user', help='The name of the op user.', required=True)
    parser.add_argument('-p', '--password', help='The password of the op user.', required=True)

    args = parser.parse_args()
    return args
# End of parseArg


def main():
    args = parse_args()
    auth_info = AuthInfo(args.group, args.user, args.password)

    logger.info('Validating login info...')
    cas = CAS(auth_info.group, auth_info.user, auth_info.password, auth_info.cas_host, secure=auth_info.security_check)
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

    update_band_targets = {
        u'訂單數大於等於平均': 'avg_orders',
        u'訂單數小於平均': 'avg_orders',
        u'消費金額大於等於平均': 'avg_revenue',
        u'消費金額小於平均': 'avg_revenue',
    }

    groups = emc2.get_groups()
    for group in groups:
        logger.info('Checking group: %s' % group['name'])

        su_logged_in = False
        try:
            # Check default data source exists or not, and ensure it is authorized to EI
            def_ds = find_default_data_source(emc2, group)
            if not AppId.EI in def_ds['appIds']:
                raise NotAuthorizedError('...Data source not authorized to EI. Skip it.')

            # SU to default op before further processing
            def_op_name = '%s_DefaultOperator' % group['name']
            ei3.do_su_login(group, def_op_name)
            su_logged_in = True

            # Get all band and summary info to update target bands
            def_band_login_90 = find_default_bands(ei3, def_ds, ['Default_Login_90'])[0]
            op_bands_targets = find_op_bands(ei3, update_band_targets.keys())
            summary_revisit_90 = ei3.get_summary('Summary_Revisit_90', def_ds, def_band_login_90)

            total_order_users = float(summary_revisit_90['total_order_users'])
            logger.info('....total_order_users : %f' % total_order_users)
            total_orders = float(summary_revisit_90['total_orders'])
            logger.info('....total_orders : %f' % total_orders)
            total_revenue_contribution = float(summary_revisit_90['total_revenue_contribution'])
            logger.info('....total_revenue_contribution : %f' % total_revenue_contribution)

            avg_orders = round(total_orders / total_order_users, 2)\
                if total_orders > 0 and total_order_users > 0\
                else 0
            logger.info('....(calculated) avg_orders : %f' % avg_orders)
            avg_revenue = round(total_revenue_contribution / total_order_users, 2)\
                if total_revenue_contribution > 0 and total_order_users > 0\
                else 0
            logger.info('....(calculated) avg_revenue : %f' % avg_revenue)

            if avg_orders > 0 and avg_revenue > 0:
                update_band_values = {
                    'avg_orders': str(avg_orders),
                    'avg_revenue': str(avg_revenue),
                }

                for band_target in op_bands_targets:
                    assert band_target['type'] == BandType.GENE
                    target_value = update_band_values[update_band_targets[band_target['name']]]
                    logger.info('...Update target gene operand of band %s to %s' % (band_target['name'], target_value))
                    band_target['targetGene']['operand'] = target_value
                    ei3.update_band(band_target)
            else:
                logger.warn('...No valid value to update. Skip it.')

        except (NotFoundError, NotAuthorizedError) as e:
            logger.warning(e.message)
        finally:
            if su_logged_in:
                ei3.do_su_logout()

    pass
# End of main

if __name__ == '__main__':
    sys.exit( main() )
