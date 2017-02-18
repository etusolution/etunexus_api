# -*- coding: utf-8 -*-

from datetime import date

from baseapp import BaseApp
from enum import *
from emc import Group, DataSource, User


class Gene(dict):
    """ Structure for (aggregation) gene

    Fields:
        id (str): The id of the gene. It should be unique in a subcategory
        name (str); Gene name
        timerange (int): Gene time range
        type (str): Gene type, refer to GeneType for valid values
        chartType (str): Gene chart type, refer to GeneChartType for valid values
        uiInfo (obj): Gene UI info
    """

    def __init__(self, id, name, time_range, type, chart_type, ui_info):
        assert id and name and time_range is not None and type and chart_type and ui_info
        super(Gene, self).__init__({
            'id': id,
            'name': name,
            'timerange': time_range,
            'type': type,
            'chartType': chart_type,
            'uiInfo': ui_info if isinstance(ui_info, GeneUIInfo) else GeneUIInfo.from_dict(ui_info)
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['id'], dict_obj['name'], dict_obj['timerange'], dict_obj['type'], dict_obj['chartType'],
                   dict_obj['uiInfo'])


class GeneCategory(dict):
    """ Structure for (aggregation) gene category

    Fields:
        name (str): Fixed gene name
        subcategories (list): A list of FixedGeneCategory as subcategories
        genes (list): A list of

        id (int): The auto id
    """

    def __init__(self, name, subcategories, genes, id=None):
        assert name and subcategories is not None and isinstance(subcategories,
                                                                 list) and genes is not None and isinstance(genes, list)
        super(GeneCategory, self).__init__({
            'name': name,
            'subcategories': [x if isinstance(x, FixedGeneCategory) else FixedGeneCategory.from_dict(x) for x in
                              subcategories],
            'genes': [x if isinstance(x, FixedGene) else FixedGene.from_dict(x) for x in genes],
            'id': id
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['name'], dict_obj['subcategories'], dict_obj['genes'], dict_obj.get('id'))


class BandGene(dict):
    """ Structure for a gene-based band

    Fields:
        geneId (str): The gene id
        cid (int): The data source to calculate the band
        operator (str): The band operator to calculate the band
        operand (str): The operands to calculate the band
    """

    def __init__(self, gene_id, data_source, operator, operand):
        assert gene_id and data_source and operator and operand
        super(BandGene, self).__init__({
            'geneId': gene_id,
            'cid': data_source['id'] if isinstance(data_source, DataSource) else data_source,
            'operator': operator,
            'operand': operand
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['geneId'], dict_obj['cid'], dict_obj['operator'], dict_obj['operand'])


class BandCombine(dict):
    """ Structure for a combined band

    Fields:
        bandIds (list): List of band ids to combine
        operators (list): List of operators using to combine the bands (only the first element is used yet)
    """

    def __init__(self, bands, operators):
        assert bands and operators
        super(BandCombine, self).__init__({
            'bandIds': [x['id'] if isinstance(x, Band) else x for x in bands],
            'operators': operators
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['bandIds'], dict_obj['operators'])


class Band(dict):
    """ Structure for a band
    
    Fields:
        categoryId (int): The band category of the band belongs to
        name (str): Band name
        description (str): Band description
        type (str): Band type, refer to 'BandType' for valid values
        targetGene (obj): Gene setting if type=gene or type=fixedgene
        targetBand (obj): Combine bands if type=combine

        needRefresh (bool): Need to refresh the band or not
        snapshotInfo (obj): Snapshot info (if a snap-shot band), or None for pure band

        id (int): The auto id
        amount (int): Amount of users in the band
        updateTime (long): The band update time in Epoch (milliseconds)
    """

    def __init__(self, category, name, description,
                 type, target_gene=None, target_band=None,
                 need_refresh=True, snapshot_info=None,
                 id=None, amount=None, update_time=None):
        super(Band, self).__init__({
            'categoryId': category['id'] if isinstance(category, BandCategory) else category,
            'name': name,
            'description': description,
            'needRefresh': need_refresh,
            'type': type,
            'targetGene': target_gene,
            'targetBand': target_band,
            'snapshotInfo': snapshot_info,
            'id': id,
            'amount': amount,
            'updateTime': update_time
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['categoryId'], dict_obj['name'], dict_obj['description'],
                   dict_obj['type'], dict_obj.get('targetGene'), dict_obj.get('targetBand'),
                   dict_obj['needRefresh'], dict_obj.get('snapshotInfo'),
                   dict_obj.get('id'), dict_obj.get('amount'), dict_obj.get('updateTime'))

    @classmethod
    def from_dict_with_ext_cat(cls, dict_obj, category):
        assert dict_obj and category
        category_id = category['id'] if isinstance(category, BandCategory) else int(category)
        return cls(category_id, dict_obj['name'], dict_obj['description'],
                   dict_obj['type'], dict_obj.get('targetGene'), dict_obj.get('targetBand'),
                   dict_obj['needRefresh'], dict_obj.get('snapshotInfo'),
                   dict_obj.get('id'), dict_obj.get('amount'), dict_obj.get('updateTime'))


class GeneUIInfo(dict):
    """ Structure for gene UI info

    Fields:
        Xaxis_id (str): The string id of gene chart x-axis
        Yaxis_id (str): The string id of gene chart y-axis
        unit (str): The string id of gene unit (used on gene filter UI, etc.)
        Xaxis (str): The (localized) string of gene chart x-axis directly set by system operator
        Xaxis (str): The (localized) string of gene chart y-axis directly set by system operator
    """

    def __init__(self, x_axis_id=None, y_axis_id=None, unit=None, x_axis=None, y_axis=None):
        super(GeneUIInfo, self).__init__({
            'Xaxis_id': x_axis_id,
            'Yaxis_id': y_axis_id,
            'unit': unit,
            'Xaxis': x_axis,
            'Yaxis': y_axis
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj.get('Xaxis_id'), dict_obj.get('Yaxis_id'), dict_obj.get('unit'),
                   dict_obj.get('Xaxis'), dict_obj.get('Yaxis'))


class FixedGene(dict):
    """ Structure for fixed (external) gene

    Fields:
        id (str): The id of the fixed gene. It should be unique in a fixed subcategory
        name (str); Gene name
        timerange (int): Gene time range
        type (str): Gene type, refer to GeneType for valid values
        chartType (str): Gene chart type, refer to GeneChartType for valid values
        uiInfo (obj): Gene UI info
    """

    def __init__(self, id, name, time_range, type, chart_type, ui_info):
        assert id and name and time_range is not None and type and chart_type and ui_info
        super(FixedGene, self).__init__({
            'id': id,
            'name': name,
            'timerange': time_range,
            'type': type,
            'chartType': chart_type,
            'uiInfo': ui_info if isinstance(ui_info, GeneUIInfo) else GeneUIInfo.from_dict(ui_info)
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['id'], dict_obj['name'], dict_obj['timerange'], dict_obj['type'], dict_obj['chartType'],
                   dict_obj['uiInfo'])


class FixedGeneCategory(dict):
    """ Structure for fixed (external) gene categories

    Fields:
        name (str): Fixed gene name
        subcategories (list): A list of FixedGeneCategory as subcategories
        genes (list): A list of

        id (int): The auto id
    """

    def __init__(self, name, subcategories, genes, id=None):
        assert name and subcategories is not None and isinstance(subcategories,
                                                                 list) and genes is not None and isinstance(genes, list)
        super(FixedGeneCategory, self).__init__({
            'name': name,
            'subcategories': [x if isinstance(x, FixedGeneCategory) else FixedGeneCategory.from_dict(x) for x in
                              subcategories],
            'genes': [x if isinstance(x, FixedGene) else FixedGene.from_dict(x) for x in genes],
            'id': id
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['name'], dict_obj['subcategories'], dict_obj['genes'], dict_obj.get('id'))


class BandCategory(dict):
    """ Structure for a band category

    Fields:
        name (str): The band category name
        bands (list): A list of Bands
        id (int): The auto id
    """

    def __init__(self, name, bands=None, id=None):
        assert name
        if bands is None:
            bands = []
        assert isinstance(bands, list)
        super(BandCategory, self).__init__({
            'name': name,
            'bands': [x if isinstance(x, Band) else Band.from_dict_with_ext_cat(x, id) for x in bands],
            'id': id
        })

    def to_simple(self):
        return {'name': self['name']}

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['name'], dict_obj.get('bands'), dict_obj.get('id'))


class PopulationSummary(dict):
    """ Structure for population summary item

    Fields:
        key (str): The key value of the summary item (depending on the gene)
        amount (int): The segment size with the key value
    """

    def __init__(self, key, amount):
        super(PopulationSummary, self).__init__({
            'key': key,
            'amount': amount
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['key'], dict_obj['amount'])


class EIGroup(dict):
    """ Structure for Etu Insight group

    Fields:
        name (str): The group id/name
        displayName (str): The display name

        id (int): The auto id (the same as EMC group)
    """

    def __init__(self, name, display_name, id=None):
        super(EIGroup, self).__init__({
            'name': name,
            'displayName': display_name,
            'id': id
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['name'], dict_obj['displayName'], dict_obj.get('id'))

    @classmethod
    def from_emc_group(cls, emc_group):
        assert emc_group and isinstance(emc_group, Group)
        return cls(emc_group['name'], emc_group['displayName'], emc_group['id'])


class EIUser(dict):
    """ Structure for Etu Insight user

    Fields:
        name (str): The login name of the user
        displayName (str): The display name
        role (str): The user role in Etu Insight, refer to AppRoleName for valid values.
                    It's a single role not a list, as the roles in EMC User object
        group (object): The group info of the user belongs to.

        id (int): The auto id (the same as EMC user)
    """

    def __init__(self, name, display_name, role, group, id=None):
        super(EIUser, self).__init__({
            'name': name,
            'displayName': display_name,
            'role': role,
            'group': group if isinstance(group, EIGroup) else
                     EIGroup.from_emc_group(group) if isinstance(group, Group) else EIGroup.from_dict(group),
            'id': id
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['name'], dict_obj['displayName'], dict_obj['role'], dict_obj['group'], dict_obj.get('id'))

    @classmethod
    def from_emc_user(cls, emc_group, emc_user):
        assert emc_group
        assert emc_user and isinstance(emc_user, User)
        filtered_role = filter(lambda u: u['appId'] == AppId.EI, emc_user.roles)
        if len(filtered_role) == 0:
            raise RuntimeError('The user (%s) does not have EI authorization.' % emc_user['name'])

        ei_role = filtered_role[0]
        return cls(emc_user['name'], emc_user['displayName'], ei_role['roleName'], emc_group, emc_user['id'])


class EI3(BaseApp):
    """ Encapsulate Etu Insight (v3) API """

    __APP_NAME = 'EI3'
    __HOST = 'eihome.online.etunexus.com'
    __API_BASE = '/EI/V3/service/v1'
    __SHIRO_CAS_BASE = '/EI/V3/shiro-cas'

    def __init__(self, cas, host=None, api_base=None, shiro_cas_base=None):
        """ Constructor """

        api_base = api_base if api_base else self.__API_BASE
        super(EI3, self).__init__(cas, EI3.__APP_NAME,
                                  api_host=host if host else self.__HOST,
                                  api_base=api_base if api_base else self.__API_BASE,
                                  shiro_cas_base=shiro_cas_base if shiro_cas_base else self.__SHIRO_CAS_BASE)

    # User info
    def get_me(self):
        res = self.request_get('/user/me')
        return EIUser.from_dict(res['data'])

    def get_superme(self):
        res = self.request_get('/user/superme')
        return EIUser.from_dict(res['data'])

    # Gene category and detail gene info
    def get_gene_categories(self, group):
        assert group
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_get('/genecategory?groupId={0}'.format(group_id))
        return [GeneCategory.from_dict(x) for x in res['data']]

    # Band category
    def get_band_categories(self):
        res = self.request_get('/bandcategory')
        return [BandCategory.from_dict(x) for x in res['data']]

    def add_band_category(self, band_category):
        assert band_category and isinstance(band_category, BandCategory)
        res = self.request_post_form('/bandcategory', band_category.to_simple())
        return BandCategory.from_dict(res['data'])

    def update_band_category(self, band_category):
        assert band_category and isinstance(band_category, BandCategory)
        band_category_id = band_category['id']
        assert band_category_id
        res = self.request_post_form('/bandcategory/{0}'.format(band_category_id), band_category.to_simple())
        return BandCategory.from_dict(res['data'])

    def del_band_category(self, band_category):
        assert band_category
        band_category_id = band_category['id'] if isinstance(band_category, BandCategory) else band_category
        assert band_category_id
        res = self.request_del('/bandcategory/{0}'.format(band_category_id))
        return res['data']

    # Band
    def add_band(self, band, file_path=None):
        assert band and isinstance(band, Band)
        band_category_id = band['categoryId']
        if file_path:
            assert band['type'] == BandType.UPLOAD
            res = self.request_upload('/band', band, file_path)
        else:
            res = self.request_post_multipart('/band', band)
        return Band.from_dict_with_ext_cat(res['data'], band_category_id)

    def update_band(self, band, file_path=None):
        assert band and isinstance(band, Band)
        band_category_id = band['categoryId']
        band_id = band['id']
        assert band_id
        if file_path:
            assert band['type'] == BandType.UPLOAD
            res = self.request_upload('/band/{0}'.format(band_id), band, file_path)
        else:
            res = self.request_post_multipart('/band/{0}'.format(band_id), band)
        return Band.from_dict_with_ext_cat(res['data'], band_category_id)

    def del_band(self, band):
        assert band
        band_id = band['id'] if isinstance(band, Band) else band
        assert band_id
        res = self.request_del('/band/{0}'.format(band_id))
        return res['data']

    # Fixed (external) gene
    def get_fixed_gene_categories(self):
        res = self.request_get('/fixedgenecategory')
        return [FixedGeneCategory.from_dict(x) for x in res['data']]

    def upload_fixed_gene_schema(self, group, file_path):
        """ Upload fixed (external) gene schema (admin/operator only) """
        assert group and file_path
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_upload('/fixedgene/schema', {'groupId': group_id}, file_path)
        return FixedGeneCategory.from_dict(res['data'])

    def upload_fixed_gene_data(self, group, file_path):
        """ Upload fixed (external) gene data (admin/operator only) """
        assert group and file_path
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_upload('/fixedgene/data', {'groupId': group_id}, file_path)
        return res['data']

    # Population summary data
    def get_population_summary(self, gene, data_source):
        """ Get population summary data """
        assert gene and data_source
        gene_id = gene['id'] if isinstance(gene, Gene) else int(gene)
        data_source_id = data_source['id'] if isinstance(data_source, DataSource) else int(data_source)
        res = self.request_get('/population/summary?geneId={0}&cId={1}'.format(gene_id, data_source_id))
        return [PopulationSummary.from_dict(x) for x in res['data']]

    # TODO: Add support for population timeline API

    # Statistics
    def get_statistics(self, group, items, start_date, end_date=date.today()):
        """ Get EI statistics.

        Arguments:
            group (obj or int): A Group instance or group id
            items (list): Refer to EIStatisticsItem for valid values, and put the (multiple) items into a list.
                e.g. [EIStatisticsItem.DOWNLOAD_UID_LIST, EIStatisticsItem.ADD_BAND]
            start_date (date or str): Start date of the statistics to query. It could be a datetime.date instance, or a
                string in 'yyyy-mm-dd' format
            end_date (date or str): End date of the statistics to query. It could be a datetime.date instance, or a
                string in 'yyyy-mm-dd' format

        Return:
            A list of tuple:
             [0] A date string in yyyy-mm-dd
             [1] An item:count dictionary

            The result is sorted by the date.
        """
        assert group and items and isinstance(items, list) and start_date and end_date
        group_id = group['id'] if isinstance(group, Group) else int(group)
        start_date_str = '%04d-%02d-%02d' % (start_date.year, start_date.month, start_date.day) \
            if isinstance(start_date, date) else str(start_date)
        end_date_str = '%04d-%02d-%02d' % (end_date.year, end_date.month, end_date.day) \
            if isinstance(end_date, date) else str(end_date)
        item_str = ','.join(items)
        res = self.request_get('/statistics/query?groupId={0}&startDate={1}&endDate={2}&itemName={3}'.format(
            group_id, start_date_str, end_date_str, item_str))
        return sorted([(key, value) for (key, value) in res['data'].iteritems()])

    # Un-documented APIs for admin/operator
    def do_su_login(self, group, user):
        assert group and user
        group_name = group['name'] if isinstance(group, Group) or isinstance(group, EIGroup) else str(group)
        user_name = user['name'] if isinstance(user, User) or isinstance(user, EIUser) else str(user)
        res = self.request_get('/suauth?groupName={0}&userName={1}'.format(group_name, user_name))
        return res['data']

    def do_su_logout(self):
        res = self.request_del('/suauth')
        return res['data']