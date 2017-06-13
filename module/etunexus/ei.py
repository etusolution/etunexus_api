# -*- coding: utf-8 -*-

from datetime import date

from baseapp import BaseApp
from enum import *
from emc import Group, DataSource, User


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


class GeneCategory(dict):
    """ Structure for (aggregation) gene category.

    Fields:
        name (str): Fixed gene name.
        subcategories (list): A list of GeneCategory as subcategories.
        genes (list): A list of Gene instances.

        id (int): The auto id.
    """

    def __init__(self, name, subcategories, genes, id=None):
        assert name and subcategories is not None and isinstance(subcategories,
                                                                 list) and genes is not None and isinstance(genes, list)
        super(GeneCategory, self).__init__({
            'name': name,
            'subcategories': [x if isinstance(x, GeneCategory) else GeneCategory.from_dict(x) for x in
                              subcategories],
            'genes': [x if isinstance(x, Gene) else Gene.from_dict(x) for x in genes],
            'id': id
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['name'], dict_obj['subcategories'], dict_obj['genes'], dict_obj.get('id'))


class Gene(dict):
    """ Structure for (aggregation) gene.

    Fields:
        id (str): The id of the gene. It should be unique in a subcategory.
        name (str); Gene name.
        timerange (int): Gene time range.
        type (str): Gene type, refer to "GeneType" for valid values.
        chartType (str): Gene chart type, refer to "GeneChartType" for valid values.
        uiInfo (obj): A GeneUIInfo instance as the gene UI info setting.
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


class BandCategory(dict):
    """ Structure for a band category.

    Fields:
        name (str): The band category name.
        bands (list): A list of Band instances.

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
        ret = {'name': self['name']}
        if self.get('isDefault'):
            ret['isDefault'] = self.get('isDefault')
        return ret

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['name'], dict_obj.get('bands'), dict_obj.get('id'))


class BandGene(dict):
    """ Structure for a gene-based band.

    Fields:
        geneId (str): The gene id.
        cid (int): The data source id to calculate the band.
        operator (str): The band operator to calculate the band, refer to "BandGeneOperator" enum for valid values.
        operand (str): The operands to calculate the band.
    """

    def __init__(self, gene_id, data_source, operator, operand):
        assert gene_id and data_source >= 0 and operator and operand is not None
        super(BandGene, self).__init__({
            'geneId': gene_id,
            'cid': data_source['id'] if isinstance(data_source, DataSource) else int(data_source),
            'operator': operator,
            'operand': operand
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['geneId'], dict_obj['cid'], dict_obj['operator'], dict_obj['operand'])


class BandCombine(dict):
    """ Structure for a combined band.

    Fields:
        bandIds (list): List of band ids to combine.
        operators (list): List of operators used to combine the bands (only the first element is used so far), refer to
        "BandCombineOperator" enum for valid values.
    """

    def __init__(self, bands, operators):
        assert bands and isinstance(bands, list)
        assert isinstance(operators, list)
        super(BandCombine, self).__init__({
            'bandIds': [x['id'] if isinstance(x, Band) else x for x in bands],
            'operators': operators
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['bandIds'], dict_obj['operators'])


class Band(dict):
    """ Structure for a band.
    
    Fields:
        categoryId (int): The band category id of the band belongs to.
        name (str): Band name.
        description (str): Band description (not used so far).
        type (str): Band type, refer to 'BandType' for valid values.
        targetGene (obj): A BandGene instance if type=gene or type=fixedgene.
        targetBand (obj): A BandCombine instance if type=combine.

        needRefresh (bool): Need to refresh the band or not.
        snapshotInfo (obj): A SnapshotInfo instance. For a pure band, it's an SnapshopInfo with no parent and empty
        children.

        shared (bool): The band is shared in group or not.

        id (int): The auto id.
        amount (int): Amount of users in the band.
        updateTime (long): The band update time in Epoch (milliseconds).
        owner (str): The owner (user_id) of the band.
    """

    def __init__(self, category, name, description,
                 type, target_gene=None, target_band=None,
                 need_refresh=True, snapshot_info=None,
                 shared=False,
                 id=None, amount=None, update_time=None, owner=None):
        super(Band, self).__init__({
            'categoryId': category['id'] if isinstance(category, BandCategory) else int(category),
            'name': name,
            'description': description,
            'needRefresh': need_refresh,
            'type': type,
            'targetGene': target_gene if isinstance(target_gene, BandGene)
                else BandGene.from_dict(target_gene) if target_gene is not None else None,
            'targetBand': target_band if isinstance(target_band, BandCombine)
                else BandCombine.from_dict(target_band) if target_band is not None else None,
            'snapshotInfo': snapshot_info if isinstance(snapshot_info, SnapshotInfo)
                else SnapshotInfo.from_dict(snapshot_info) if snapshot_info is not None else SnapshotInfo(),
            'shared': shared,

            'id': id,
            'amount': amount,
            'updateTime': update_time,
            'owner': owner
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['categoryId'], dict_obj['name'], dict_obj['description'],
                   dict_obj['type'], dict_obj.get('targetGene'), dict_obj.get('targetBand'),
                   dict_obj['needRefresh'], dict_obj.get('snapshotInfo'),
                   dict_obj.get('shared'),
                   dict_obj.get('id'), dict_obj.get('amount'), dict_obj.get('updateTime'),
                   dict_obj.get('owner'))

    @classmethod
    def from_dict_with_ext_cat(cls, dict_obj, category):
        assert dict_obj and category
        category_id = category['id'] if isinstance(category, BandCategory) else int(category)
        return cls(category_id, dict_obj['name'], dict_obj['description'],
                   dict_obj['type'], dict_obj.get('targetGene'), dict_obj.get('targetBand'),
                   dict_obj['needRefresh'], dict_obj.get('snapshotInfo'),
                   dict_obj.get('shared'),
                   dict_obj.get('id'), dict_obj.get('amount'), dict_obj.get('updateTime'),
                   dict_obj.get('owner'))


class SnapshotInfo(dict):
    """ Structure for band snapshot information.

    Fields:
        parent (int): The parent band id.
        children (list): A list of band ids as children.
    """

    def __init__(self, parent=None, children=None):
        if not children:
            children = []
        super(SnapshotInfo, self).__init__({
            'parent': parent,
            'children': children
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj.get('parent'), dict_obj.get('children'))


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


class FixedGene(dict):
    """ Structure for fixed (external) gene.

    Fields:
        id (str): The id of the fixed gene. It should be unique in a fixed gene subcategory.
        name (str); Gene name.
        timerange (int): Gene time range.
        type (str): Gene type, refer to "GeneType" enum for valid values.
        chartType (str): Gene chart type, refer to "GeneChartType" for valid values.
        uiInfo (obj): A GeneUIInfo instance as the gene UI info setting.
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


class PopulationSummary(dict):
    """ Structure for population summary item.

    Fields:
        key (str): The key value of the summary item (depending on the gene).
        amount (int): The segment size with the key value.
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


class PopulationTimeline(dict):
    """ Structure for poluation timeline data.
    
    Fields:
        name (str): The gene id.
        group (str): The group name.
        data_source_id (int): The data source id.
        start_time (int): The Epoch timestamp of data query start time.
        end_time (int): The Epoch timestamp of data query end time.
        data (obj): List of (date, count) detail data.
    """

    def __init__(self, name, group, ds_id, start_time, end_time, data):
        super(PopulationTimeline, self).__init__({
            'name': name,
            'group': group,
            'data_source_id': ds_id,
            'start_time': start_time,
            'end_time': end_time,
            'data': [(date.fromtimestamp(x[0]/1000), x[1]) for x in data]
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['name'], dict_obj['group'], dict_obj['cid'], dict_obj['startTime'], dict_obj['endTime'],
                   dict_obj['data'])


class EIGroup(dict):
    """ Structure for Etu Insight group.

    Fields:
        name (str): The group id/name.
        displayName (str): The display name.

        id (int): The auto id (the same id as the same group in EMC).
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
    """ Structure for Etu Insight user.

    Fields:
        name (str): The login name of the user.
        displayName (str): The display name.
        role (str): The user role in Etu Insight, refer to "AppRoleName" for valid values.
                    It's a single role name rather than a list as the roles in emc.User object for multiple applications.
        group (object): A emc.Group or EIGroup instance that the user belongs to.

        id (int): The auto id (the same id as the same user in EMC)
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


class UidBandList(dict):
    """ Structure for the band list (id and name) of a uid belongs to.

    Fields:
        userId (str): The uid/customer id.
        bandIdList (list): The list of band ids.
        bandNameList (list): The list of band names.
    """

    def __init__(self, band_id_list, band_name_list):
        assert band_id_list and isinstance(band_id_list, list)
        assert band_name_list and isinstance(band_name_list, list)
        super(UidBandList, self).__init__({
            'bandIdList': band_id_list,
            'bandNameList': band_name_list
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['bandIdList'], dict_obj['bandNameList'])


class EI3(BaseApp):
    """ Encapsulate Etu Insight (v3) API """

    __APP_NAME = 'EI3'
    __HOST = 'eihome.online.etunexus.com'
    __API_BASE = '/EI/V3/service/v1'
    __SHIRO_CAS_BASE = '/EI/V3/shiro-cas'

    def __init__(self, cas, host=None, api_base=None, shiro_cas_base=None):
        """ Constructor of EI3 instance. """

        api_base = api_base if api_base else self.__API_BASE
        super(EI3, self).__init__(cas, EI3.__APP_NAME,
                                  api_host=host if host else self.__HOST,
                                  api_base=api_base if api_base else self.__API_BASE,
                                  shiro_cas_base=shiro_cas_base if shiro_cas_base else self.__SHIRO_CAS_BASE)

    def _resolve_root_url(self, postfix):
        return 'https://{0}/{1}'.format(self._api_host, postfix)

    # User info
    def get_me(self):
        """ Get the special "me" user information.

        The "me" might be a simulated user if a "su" process is applied by calling do_su_login().

        Arguments:
        Return:
            A EIUser instance as "me".
        """
        res = self.request_get('/user/me')
        return EIUser.from_dict(res['data'])

    def get_superme(self):
        """ Get the special "superme" user information.

        The "superme" is the actual login user no matter a "su" process is applied or not.

        Arguments:
        Return:
            A EIUser instance as "superme".
        """
        res = self.request_get('/user/superme')
        return EIUser.from_dict(res['data'])

    # Gene category and detail gene info
    def get_gene_categories(self, group):
        """ Get all (aggregation) gene categories and detail genes.

        Though the gene setting is global, different group may be authorized with different set.

        Arguments:
            group (obj or int): The emc.Group instance, or EIGroup instance, or a group id to get genes.
        Return:
            A list of GeneCategory instances.
        """
        assert group
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, EIGroup) else int(group)
        res = self.request_get('/genecategory?groupId={0}'.format(group_id))
        return [GeneCategory.from_dict(x) for x in res['data']]

    # Band category
    def get_band_categories(self):
        """ Get user's all band categories and detail bands.

        Arguments:
        Return:
            A list of BandCategory instances.
        """
        res = self.request_get('/bandcategory')
        return [BandCategory.from_dict(x) for x in res['data']]

    def add_band_category(self, band_category):
        """ Add a new band category.

        In most cases, no need to initialize the "bands" in the new category. Use add_band() to add bands into the new
        category later.

        Arguments:
            band_category (obj): The BandCategory instance to add.
        Return:
            A BandCategory instance as the added one (with fields filled by server, e.g. id).
        """
        assert band_category and isinstance(band_category, BandCategory)
        res = self.request_post_form('/bandcategory', band_category.to_simple())
        return BandCategory.from_dict(res['data'])

    def update_band_category(self, band_category):
        """ Update a band category.

        Only update the attributes of a band category, e.g. "name". DO NOT USE this method to manipulate "bands". Use
        add_band(), update_band(), delete_band() methods instead.

        Arguments:
            band_category (obj): The BandCategory instance to update.
        Return:
            A BandCategory instance as the updated one.
        """
        assert band_category and isinstance(band_category, BandCategory)
        band_category_id = band_category['id']
        assert band_category_id
        res = self.request_post_form('/bandcategory/{0}'.format(band_category_id), band_category.to_simple())
        return BandCategory.from_dict(res['data'])

    def del_band_category(self, band_category):
        """ Delete a band category.

        It would cause error if the band category is not empty (still exist bands in it).

        Arguments:
            band_category (obj or int): The BandCategory instance or a band category id to delete.
        Return:
            The band category id deleted. It must be the same as the one in argument.
        """
        assert band_category
        band_category_id = band_category['id'] if isinstance(band_category, BandCategory) else int(band_category)
        assert band_category_id
        res = self.request_del('/bandcategory/{0}'.format(band_category_id))
        # For unknown reason, delete category returns a list. Leave a possible change in the future that it might become
        # a simple dict
        res_id = res['data'][0]['id'] if isinstance(res['data'], list) else res['data']['id']
        assert res_id == band_category_id
        return res_id

    def get_shared_band_categories(self, group=None):
        """ Get shared band categories and detail bands in the group.

        Arguments:
            group (obj or int): The emc.Group instance, or EIGroup instance, or a group id to get shared bands. If
                                it is omitted (=None), current user gorup is used. 
        Return:
            A list of BandCategory instances.
        """
        api = '/sharingbandcategory'
        if group is not None:
            group_id = group['id'] if isinstance(group, Group) or isinstance(group, EIGroup) else int(group)
            api = '/sharingbandcategory?groupId={0}'.format(group_id)

        res = self.request_get(api)
        return [BandCategory.from_dict(x) for x in res['data']]

    # Band
    def add_band(self, band, file_path=None):
        """ Add a new band.

        If the band type is BandType.UPLOAD, it requires file as the band list. The file format is standard CSV with at
        lease a "uid" column as the user/customer id list.

        Arguments:
            band (obj): The Band instance to add.
            file_path (str): The file to upload if the band type is BandType.UPLOAD.
        Return:
            A Band instance as the added one.
        """
        assert band and isinstance(band, Band)
        band_category_id = band['categoryId']
        if file_path:
            assert band['type'] == BandType.UPLOAD
            res = self.request_upload('/band', band, file_path)
        else:
            res = self.request_post_multipart('/band', band)
        return Band.from_dict_with_ext_cat(res['data'], band_category_id)

    def update_band(self, band, file_path=None):
        """ Update a band.

        It is not recommended to change the band type after added with this method, but not enforced. Therefore, it is
        suggested that client code could make the check before calling update_band().

        If the band type is BandType.UPLOAD, it requires file as the band list. The file format is standard CSV with at
        lease a "uid" column as the user/customer id list.

        Arguments:
            band (obj): The Band instance to add.
            file_path (str): The file to upload if the band type is BandType.UPLOAD.
        Return:
            A Band instance as the updated one.
        """
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
        """ Delete a band.

        Arguments:
            band (obj or int): The Band instance or a band id to delete.
        Return:
            The band id deleted. It must be the same as the one in argument.
        """
        assert band
        band_id = band['id'] if isinstance(band, Band) else int(band)
        assert band_id
        res = self.request_del('/band/{0}'.format(band_id))
        res_id = res['data']['id']
        assert res_id == band_id
        return res_id

    def get_uid_list(self, band, save_path):
        """ Get/download user/customer id list in a band.
        
        Arguments:
            band (obj or int): The Band instance or a band id to get the user list.
            save_path (str): The file path to save the user list.
        Return:
            The save_path in argument.
        """
        assert band
        band_id = band['id'] if isinstance(band, Band) else int(band)
        assert band_id
        res = self.request_get('/band/{0}/uidlist'.format(band_id))
        download_link = res['data']['downloadLink']
        self.logger.debug('Get the download link: %s' % download_link)
        download_url = self._resolve_root_url(download_link)
        self.logger.debug('Make download from: %s' % download_url)
        return self.request_download(download_url, save_path)

    # Snapshot
    def do_snapshot(self, band):
        """ Make a snapshot/clone of a band.

        Arguments:
            band (obj or int): The Band instance or a band id to clone.
        Return:
            A Band instance as the cloned one, with a given name derived from the original band name.
        """
        assert band
        band_id = band['id'] if isinstance(band, Band) else int(band)
        assert band_id
        res = self.request_post('/band/{0}/snapshot'.format(band_id))
        return Band.from_dict(res['data'])

    # Fixed (external) gene
    def get_fixed_gene_categories(self):
        """ Get the fixed (external) gene categories and detail genes.

        Arguments:
        Return:
            A list of FixedGeneCategory instances.
        """
        res = self.request_get('/fixedgenecategory')
        return [FixedGeneCategory.from_dict(x) for x in res['data']]

    def upload_fixed_gene_schema(self, group, file_path):
        """ Upload fixed (external) gene schema (admin/operator only).

        It requires a gene schema file, and the file format is JSON. Please refer to the product documents or consult
        with Etu members for the detail.

        Arguments:
            group (obj or int): The emc.Group or EIGroup instance or a group id to upload fixed gene schema.
            file_path (str): The schema file.
        Return:
            A FixedGeneCategory instance as the schema defined.
        """
        assert group and file_path
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, EIGroup) else int(group)
        assert group_id
        res = self.request_upload('/fixedgene/schema', {'groupId': group_id}, file_path)
        return FixedGeneCategory.from_dict(res['data'])

    def upload_fixed_gene_data(self, group, file_path):
        """ Upload fixed (external) gene data (admin/operator only).

        It requires a gene data/value file, and the file format is standard CSV. A "uid" column is required, and other
        columns should be the same as the "gene_id" in the schema uploaded. Please refer to the product documents or
        consult with Etu members for the detail.

        Arguments:
            group (obj or int): The emc.Group or EIGroup instance or a group id to upload fixed gene schema.
            file_path (str): The data file.
        Return:
            A success message.
        """
        assert group and file_path
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, EIGroup) else int(group)
        assert group_id
        res = self.request_upload('/fixedgene/data', {'groupId': group_id}, file_path)
        return res['data']

    # Population summary data
    def get_population_summary(self, gene, data_source):
        """ Get population summary data.

        Arguments:
            gene (obj or int): The Gene instance or a gene id to get summary data.
            data_source (obj or int): The emc.DataSource instance or a data source id.
        Return:
            A list of PopulationSummary instances.
        """
        assert gene and data_source
        gene_id = gene['id'] if isinstance(gene, Gene) else str(gene)
        data_source_id = data_source['id'] if isinstance(data_source, DataSource) else int(data_source)
        res = self.request_get('/population/summary?geneId={0}&cId={1}'.format(gene_id, data_source_id))
        return [PopulationSummary.from_dict(x) for x in res['data']]

    def get_population_timeline(self, genes, data_source, start_date, end_date, filter_op,
                                filter_comp=EIPopulationTimelineFilterCompType.STRING + ':*'):
        """ Get population timeline data.
        
        Arguments:
            genes (obj): A list of Gene instances or gene ids to get timeline data.
            data_source (obj or int): The emc.DataSource instance or a data source id.
            start_date (date or str): Start date of the data to query. It could be a datetime.date instance, or a
                string in 'yyyy-mm-dd' format.
            end_date (date or str): End date of the data to query. It could be a datetime.date instance, or a
                string in 'yyyy-mm-dd' format.
            filter_op (str): The filter operator, refer to "EIPopulationTimelineFilterOP" enum for valid values.
            filter_comp (str): The filter comparator in format "TYPE:VALUE". For valid "TYPE", refer to
                "EIPopulationTimelineFilterCompType" enum.
        Return:
            A list of PopulationTimeline instances.
        """
        assert genes and isinstance(genes, list) and data_source
        assert start_date and end_date
        assert filter_op and filter_comp
        gene_ids = ','.join([gene['id'] if isinstance(gene, Gene) else str(gene) for gene in genes])
        data_source_id = data_source['id'] if isinstance(data_source, DataSource) else int(data_source)
        start_date_str = '%04d-%02d-%02d' % (start_date.year, start_date.month, start_date.day) \
            if isinstance(start_date, date) else str(start_date)
        end_date_str = '%04d-%02d-%02d' % (end_date.year, end_date.month, end_date.day) \
            if isinstance(end_date, date) else str(end_date)

        res = self.request_get('/timeline/population/{0}/{1}?startTime={2}&endTime={3}&filterOperator={4}&filterComparator={5}'.format(
            gene_ids, data_source_id, start_date_str, end_date_str, filter_op, filter_comp
        ))
        return [PopulationTimeline.from_dict(x) for x in res['data']]

    # Statistics
    def get_statistics(self, group, items, start_date, end_date=date.today()):
        """ Get EI statistics.

        Arguments:
            group (obj or int): The emc.Group instance, or EIGroup instance, or a group id to get statistics.
            items (list): Refer to EIStatisticsItem for valid values, and put the (multiple) items into a list.
                e.g. [EIStatisticsItem.DOWNLOAD_UID_LIST, EIStatisticsItem.ADD_BAND]
            start_date (date or str): Start date of the statistics to query. It could be a datetime.date instance, or a
                string in 'yyyy-mm-dd' format.
            end_date (date or str): End date of the statistics to query. It could be a datetime.date instance, or a
                string in 'yyyy-mm-dd' format.
        Return:
            A list of tuple:
             [0] A date string in yyyy-mm-dd
             [1] An item:count dictionary

            The result is sorted by the date.
        """
        assert group and items and isinstance(items, list) and start_date and end_date
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, EIGroup) else int(group)
        start_date_str = '%04d-%02d-%02d' % (start_date.year, start_date.month, start_date.day) \
            if isinstance(start_date, date) else str(start_date)
        end_date_str = '%04d-%02d-%02d' % (end_date.year, end_date.month, end_date.day) \
            if isinstance(end_date, date) else str(end_date)
        item_str = ','.join(items)
        res = self.request_get('/statistics/query?groupId={0}&startDate={1}&endDate={2}&itemName={3}'.format(
            group_id, start_date_str, end_date_str, item_str))
        return sorted([(key, value) for (key, value) in res['data'].iteritems()])

    # Customer information
    def get_customer_info(self, data_source, uid):
        """ Get the gene values of a user/customer.

        Arguments:
            data_source (obj or int): A emc.DataSource instance or a data source id.
            uid (str): The user/customer id.
        Return:
            A dict with the key as gene ids and corresponding values.
        """
        assert data_source and uid and isinstance(uid, str)
        data_source_id = data_source['id'] if isinstance(data_source, DataSource) else int(data_source)
        res = self.request_get('/customerinformation/{0}?cId={1}'.format(uid, data_source_id))
        return res['data']

    def get_uid_band_list(self, user, uid):
        """ Get the band list of a user/customer belongs to.

        This methods returns the band list, owned by the "user" given, of the user/customer belongs to. Currently, there
        is no authentication check.

        Arguments:
            user (obj or int): The owner of the bands.
            uid (str): The user/customer id.
        Return:
            An UidBandList instance.
        """
        assert user and uid and isinstance(uid, str)
        user_id = user['id'] if isinstance(user, User) or isinstance(user, EIUser) else int(user)
        res = self.request_get('/uidbandlist/id?uid={0}&userId={1}'.format(uid, user_id))
        return UidBandList.from_dict(res['data'])

    # Item data source
    def upload_item_data(self, group, file_path):
        """ Upload item information data.

        It requires a item information file as standard CSV format. Please refer to the product documents or consult
        with Etu members for the detail.

        Arguments:
            group (obj or int): The emc.Group instance, or EIGroup instance, or a group id to add the data.
            file_path (str): The data file.
        Return:
            The total item info (pid count) uploaded.
        """
        assert group and file_path
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, EIGroup) else int(group)
        res = self.request_upload('/item', data={'groupId': group_id}, file=file_path)
        return res['data']['pidNumber']

    # EC Application - Summary
    def get_summary(self, summary_id, data_source, band):
        """ Get the summary data of EC application.

        Arguments:
            summary_id (str): The summary id, e.g. Summary_Revisit_7, Summary_Revisit_30, etc.
            data_source (obj or int): A emc.DataSource instance or a data source id.
            band (obj or int): A Band instance of a band id.
        Return:

        """
        assert summary_id and data_source and band
        upper_bound = 1
        lower_bound = 1
        data_source_id = data_source['id'] if isinstance(data_source, DataSource) else int(data_source)
        band_id = band['id'] if isinstance(band, Band) else int(band)
        res = self.request_get('/summary/{0}?cId={1}&bandId={2}&upperBound={3}&lowerBound={4}'.format(
            summary_id, data_source_id, band_id, upper_bound, lower_bound))
        return res['data']

    # Un-documented APIs for admin/operator
    def do_su_login(self, group, user):
        """ Make "su" login (admin/operator only).

        Arguments:
            group (obj or int): The Group instance, or EIGroup instance, or a group name of the user to simulate.
            user (obj or int): The User instance, or EIUser instance, or a user name of the user to simulate.
        Return:
            A success message.
        """
        assert group and user
        group_name = group['name'] if isinstance(group, Group) or isinstance(group, EIGroup) else str(group)
        user_name = user['name'] if isinstance(user, User) or isinstance(user, EIUser) else str(user)
        res = self.request_get('/suauth?groupName={0}&userName={1}'.format(group_name, user_name))
        return res['data']

    def do_su_logout(self):
        """ Make "su" logout (admin/operator only).

        Arguments:
        Return:
            A success message.
        """
        res = self.request_del('/suauth')
        return res['data']

    def get_default_bandcategories(self, data_source):
        """ Get default band category and bands.
        
        Arguments:
            data_source (obj or int): The emc.DatraSource instance or a data source id.
        Return:
            A list of BandCategory instances.
        """
        assert data_source
        data_source_id = data_source['id'] if isinstance(data_source, DataSource) else int(data_source)
        res = self.request_get('/defaultbandcategory?cId={0}'.format(data_source_id))
        return [BandCategory.from_dict(x) for x in res['data']]