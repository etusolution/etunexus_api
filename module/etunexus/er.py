# -*- coding: utf-8 -*-

from baseapp import BaseApp
from emc import Group, DataSource
from enum import *


class ERGroup(dict):
    """ Structure of a ER specific group.

    NOTICE: No createTime field as in emc.Group.

    Fields:
        name (str): The group id/name of.
        displayName (str): The group display name.
        id (int): The auto id of the group.
        createTime (long): The group create time.
    """
    def __init__(self, name, display_name, id=None):
        assert name and display_name
        super(ERGroup, self).__init__({
            'name': name,
            'displayName': display_name,
            'id': id
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['name'], dict_obj['displayName'], dict_obj.get('id'))


class ERDataSource(dict):
    """ Structure of a ER specific/authorized data source.

    NOTICE: While all data source management should be applied on EMC. The structure here includes only basic
    information as not as rich as emc.DataSource.

    Fields:
        name (str): The data source id/name.
        displayName (str): The data source display name.
        contentType (str): The data source content type, refer to 'DataSourceContentType' enum for valid values
        type (str): The data source type (how to get data), refer to 'DataSourceType' enum for valid values

        id (int): Data source auto id
        groupId (int): Group auto id
    """
    def __init__(self, name, display_name, content_type, type, id=None, group_id=None):
        super(ERDataSource, self).__init__({
            'name': name,
            'displayName': display_name,
            'contentType': content_type,
            'type': type,

            'id': id,
            'groupId': group_id
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['name'], dict_obj['displayName'], dict_obj['contentType'], dict_obj['type'],
                      dict_obj.get('id'), dict_obj.get('groupId'))


class AlgInstance(dict):
    """ Structure of an algorithm instance in the recommendation logic.

    AlgInstance is an ABC for all different algorithm structure. The inherited algorithm implementation should be named
    as "Alg_[algId]", e.g. Alg_USER_BASED_CF or Alg_ALS.

    Fields:
        algId (str): The algorithm id, every derived algorithm should have its own id, refer to "LogicAlgorithmId" enum
        for samples but not limited.
        weight (int): The weight of the algorithm in the linear combination to the recommendation logic result.
        setting (obj): The setting depend on the concrete algorithm implementation.
    """
    def __init__(self, alg_id, weight, setting):
        assert alg_id and weight and setting and isinstance(setting, dict)
        super(AlgInstance, self).__init__({
            'algId': alg_id,
            'weight': weight,
            'setting': setting
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls._create_alg_instance(dict_obj['algId'], dict_obj)

    @classmethod
    def _create_alg_instance(cls, alg_id, dict_obj):
        alg_class_name = 'Alg_{0}'.format(alg_id)
        try:
            klass = globals()[alg_class_name]
        except KeyError, ke:
            klass = None
        return klass.from_dict(dict_obj) if klass else Alg_UNKNOWN.from_dict(dict_obj)


class Alg_UNKNOWN(AlgInstance):
    """ Structure of unknown/not-supported algorithm.

    Fields:
        (As 'setting' in AlgInstance)
    """
    def __init__(self, weight, setting):
        assert weight and setting and isinstance(setting, dict)
        super(Alg_UNKNOWN, self).__init__(LogicAlgorithmId.UNKNOWN, weight, setting)

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj and dict_obj['setting']
        setting = dict_obj['setting']
        return cls(dict_obj['weight'], setting)


class Alg_USER_BASED_CF(AlgInstance):
    """ Structure of user-based CF algorithm.

    Fields:
        (As "setting" in AlgInstance)
        id (str): Fixed "USER_BASED_CF".
        DATASOURCE (obj): An emc.DataSource instance, ERDataSource instance, or a dict instance with "id" and "name").
        TIMERANGE (int): The data time range to calculate.
        action (list): A list of event actions to calculate, refer to "EventAction" enum for samples but not limited.
    """
    def __init__(self, weight, data_source, time_range, actions):
        assert data_source and isinstance(data_source, dict)
        assert time_range
        assert actions and isinstance(actions, list)
        setting = {
            'id': LogicAlgorithmId.USER_BASED_CF,
            'DATASOURCE': {'id': data_source['id'], 'name': data_source['name']},
            'TIMERANGE': time_range,
            'action': actions
        }
        super(Alg_USER_BASED_CF, self).__init__(LogicAlgorithmId.USER_BASED_CF, weight, setting)

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj and dict_obj['setting']
        setting = dict_obj['setting']
        return cls(dict_obj['weight'], setting['DATASOURCE'], setting['TIMERANGE'], setting['action'])


class Alg_ITEM_BASED_CF(AlgInstance):
    """ Structure of item-based CF algorithm.

    Fields:
        (As 'setting' in AlgInstance)
        id (str): Fixed "ITEM_BASED_CF".
        DATASOURCE (obj): An emc.DataSource instance, ERDataSource instance, or a dict instance with "id" and "name").
        TIMERANGE (int): The data time range to calculate.
        action (list): A list of event actions to calculate, refer to "EventAction" enum for samples but not limited.
    """
    def __init__(self, weight, data_source, time_range, actions):
        assert data_source and isinstance(data_source, dict)
        assert time_range
        assert actions and isinstance(actions, list)
        setting = {
            'id': LogicAlgorithmId.ITEM_BASED_CF,
            'DATASOURCE': {'id': data_source['id'], 'name': data_source['name']},
            'TIMERANGE': time_range,
            'action': actions
        }
        super(Alg_ITEM_BASED_CF, self).__init__(LogicAlgorithmId.ITEM_BASED_CF, weight, setting)

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj and dict_obj['setting']
        setting = dict_obj['setting']
        return cls(dict_obj['weight'], setting['DATASOURCE'], setting['TIMERANGE'], setting['action'])


class Alg_RANKING(AlgInstance):
    """ Structure of ranking algorithm.

    Fields:
        (As 'setting' in AlgInstance)
        id (str): Fixed "RANKING".
        DATASOURCE (obj): An emc.DataSource instance, ERDataSource instance, or a dict instance with "id" and "name").
        TIMERANGE (int): The data time range to calculate.
        actionList (list): A list of event actions to calculate, refer to "EventAction" enum for samples but not
        limited.
        addNonCategoryRec (bool): Generate category-independent recommendation list or not.
        delimiter (str): The delimiter in the category string for multiple levels categories.
    """
    def __init__(self, weight, data_source, time_range, actions, gen_non_category_rec=True, delimiter=None):
        assert data_source and isinstance(data_source, dict)
        assert time_range
        assert actions and isinstance(actions, list)
        if delimiter is None:
            delimiter = ','

        setting = {
            'id': LogicAlgorithmId.RANKING,
            'DATASOURCE': {'id': data_source['id'], 'name': data_source['name']},
            'TIMERANGE': time_range,
            'actionList': actions,
            'addNonCategoryRec': str(bool(gen_non_category_rec)).lower(),
            'delimiter': delimiter
        }
        super(Alg_RANKING, self).__init__(LogicAlgorithmId.RANKING, weight, setting)

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj and dict_obj['setting']
        setting = dict_obj['setting']
        return cls(dict_obj['weight'], setting['DATASOURCE'], setting['TIMERANGE'], setting['actionList'],
                   setting.get('addNonCategoryRec'), setting.get('delimiter'))


class Alg_RANKING_ITEMINFO(AlgInstance):
    """ Structure for ranking with item info algorithm.

    Fields:
        (As 'setting' in AlgInstance)
        id: Fixed "RANKING_ITEMINFO".
        DATASOURCE (obj): An emc.DataSource instance, ERDataSource instance, or a dict instance with "id" and "name").
        TIMERANGE (int): The data time range to calculate.
        actionList (list): A list of event actions to calculate, refer to "EventAction" enum for samples but not
        limited.
        datasource_Iteminfo (obj): An emc.DataSource instance, ERDataSource instance, or a dict instance with "id" and
        "name").
        addNonCategoryRec (bool): Generate category-independent recommendation list or not.
        delimiter (str): The delimiter in the category string for multiple levels categories.
    """
    def __init__(self, weight, data_source, time_range, actions, item_data_source,
                 gen_non_category_rec=True, delimiter=None):
        assert data_source and isinstance(data_source, dict)
        assert time_range
        assert actions and isinstance(actions, list)
        assert item_data_source and isinstance(item_data_source, dict)
        if delimiter is None:
            delimiter = ','

        setting = {
            'id': LogicAlgorithmId.RANKING,
            'DATASOURCE': {'id': data_source['id'], 'name': data_source['name']},
            'TIMERANGE': time_range,
            'actionList': actions,
            'datasource_Iteminfo': {'id': item_data_source['id'], 'name': item_data_source['name']},
            'addNonCategoryRec': str(bool(gen_non_category_rec)).lower(),
            'delimiter': delimiter
        }
        super(Alg_RANKING_ITEMINFO, self).__init__(LogicAlgorithmId.RANKING_ITEMINFO, weight, setting)

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj and dict_obj['setting']
        setting = dict_obj['setting']
        return cls(dict_obj['weight'], setting['DATASOURCE'], setting['TIMERANGE'], setting['actionList'],
                   setting['datasource_Iteminfo'],
                   setting.get('addNonCategoryRec'), setting.get('delimiter'))


class Alg_SEARCH2CLICK(AlgInstance):
    """ Structure for search to click algorithm.

    Fields:
        (As 'setting' in AlgInstance)
        id: Fixed "SEARCH2CLICK"
        DATASOURCE (obj): An emc.DataSource instance, ERDataSource instance, or a dict instance with "id" and "name").
        TIMERANGE (int): The data time range to calculate.
        TIME_DECAYED (int): The time decay factor.
        ACTION (str): The event action to calculate after the search event.
    """
    def __init__(self, weight, data_source, time_range, time_decay_factor, action):
        assert data_source and isinstance(data_source, dict)
        assert time_range
        assert time_decay_factor
        assert action
        setting = {
            'id': LogicAlgorithmId.SEARCH2CLICK,
            'DATASOURCE': {'id': data_source['id'], 'name': data_source['name']},
            'TIMERANGE': time_range,
            'TIME_DECAYED': time_decay_factor,
            'ACTION': action
        }
        super(Alg_SEARCH2CLICK, self).__init__(LogicAlgorithmId.SEARCH2CLICK, weight, setting)

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj and dict_obj['setting']
        setting = dict_obj['setting']
        return cls(dict_obj['weight'], setting['DATASOURCE'], setting['TIMERANGE'], setting['TIME_DECAYED'],
                   setting['ACTION'])


class Alg_Info_Integrity(AlgInstance):
    """ Structure for item info integrity recommendation.
    
    Fields:
        (As 'setting' in AlgInstance)
        id: Fixed "Info_Integrity"
        dataSource (obj): An emc.DataSource instance, ERDataSource instance, or a dict instance with "id" and "name").
        attritubeList (list): The attributes used to process integrity recommendation.

    Notice: "attritubeList" is the typo of "attributeList".
    """
    def __init__(self, weight, data_source, attributes):
        assert data_source and isinstance(data_source, dict)
        assert attributes and isinstance(attributes, list)
        setting = {
            'id': LogicAlgorithmId.INFO_INTEGRITY,
            'dataSource': {'id': data_source['id'], 'name': data_source['name']},
            'attritubeList': attributes
        }
        super(Alg_Info_Integrity, self).__init__(LogicAlgorithmId.INFO_INTEGRITY, weight, setting)

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj and dict_obj['setting']
        setting = dict_obj['setting']
        return cls(dict_obj['weight'], setting['dataSource'], setting['attritubeList'])


class Alg_ALS(AlgInstance):
    """ Structure for ALS recommendation.

    Fields:
        (As 'setting' in AlgInstance)
        id: Fixed "ALS"
        dataSource (obj): An emc.DataSource instance, ERDataSource instance, or a dict instance with "id" and "name").
        timeRange (int): The data time range to calculate.
        LAMBDA (float): The lambda value for ALS algorithm.
    """
    def __init__(self, weight, data_source, time_range, lambda_val=0.1):
        assert data_source and isinstance(data_source, dict)
        assert time_range
        assert lambda_val
        setting = {
            'id': LogicAlgorithmId.ALS,
            'dataSource': {'id': data_source['id'], 'name': data_source['name']},
            'timeRange': time_range,
            'LAMBDA': lambda_val
        }
        super(Alg_ALS, self).__init__(LogicAlgorithmId.ALS, weight, setting)

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj and dict_obj['setting']
        setting = dict_obj['setting']
        return cls(dict_obj['weight'], setting['dataSource'], setting['timeRange'], setting['LAMBDA'])


class Alg_LDA(AlgInstance):
    """ Structure for LDA context-awared recommendation.

    Fields:
        (As 'setting' in AlgInstance)
        id: Fixed "LDA"
        DATASOURCE (obj): An emc.DataSource instance, ERDataSource instance, or a dict instance with "id" and "name").
    """
    def __init__(self, weight, data_source):
        assert data_source and isinstance(data_source, dict)
        setting = {
            'id': LogicAlgorithmId.LDA,
            'DATASOURCE': {'id': data_source['id'], 'name': data_source['name']}
        }
        super(Alg_LDA, self).__init__(LogicAlgorithmId.LDA, weight, setting)

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj and dict_obj['setting']
        setting = dict_obj['setting']
        return cls(dict_obj['weight'], setting['DATASOURCE'])


class UserFilter(dict):
    """ Structure of a user filter setting.

    Fields:
        name (str): The user filter name/id.
        displayName (str): The user filter display name.

        id (int): The auto id.
        createTime (long): Create time in Epoch (milliseconds).
        updateTime (long): Update time in Epoch (milliseconds).
    """
    def __init__(self, name, display_name, id=None, create_time=None, update_time=None):
        assert name and display_name
        super(UserFilter, self).__init__({
            'name': name,
            'displayName': display_name,
            'id': id,
            'createTime': create_time,
            'updateTime': update_time
        })

    @classmethod
    def from_dict(cls, dict_obj):
        assert dict_obj
        return cls(dict_obj['name'], dict_obj['displayName'],
                   dict_obj.get('id'), dict_obj.get('createTime'), dict_obj.get('updateTime'))


class Logic(dict):
    """ Structure of a recommendation logic.

    Fields:
        name (str): The logic name/id.
        displayName (str): The logic display name.
        active (bool): The logic is active or not.
        numberOfRec (int): Max count of recommendation results.
        algType (str): The logic algorithm type, refer to "LogicAlgType" enum for valid values.
        algInstances (list): Algorithm instances in the logic.
        userFilter (object): User filter setting.
        useLocation (bool): Use location or not.
        delegateLogicName (str): The logic(s) for recommendation complementary.
        enableUpdating (bool): Enable core engine process or not.

        ## Item Filtering (only for altType==ITEM_BASE)
        enableLastViewedItem (bool): Enable last viewed item recommendation or not.
        itemFilterSrc (str): The item info data source used for filtering.
        enableSameCategory (bool): Enable item in same category recommendation or not.
        avlItemFilterMode (str): The item avl filter mode, refer to "LogicAvlItemFilterMode" enum for valid values.

        id (int): The auto id.
        createTime (long): Create time in Epoch (milliseconds).
        updateTime (long): Update time in Epoch (milliseconds).
    """
    def __init__(self, name, display_name, active, rec_count,
                 alg_type, alg_instances,
                 user_filter=None,
                 use_location=False, enable_last_viewed_item=False,
                 complementary_logics=None, enable_updating=True,
                 item_filter_src=None, enable_same_category=False, avl_item_filter_mode=LogicAvlItemFilterMode.DISABLED,
                 id=None, create_time=None, update_time=None):
        assert name and display_name and rec_count
        assert active is not None and isinstance(active, bool)
        assert alg_type and alg_instances and isinstance(alg_instances, list)
        if user_filter is not None:
            assert isinstance(user_filter, UserFilter)
        assert isinstance(use_location, bool)
        assert isinstance(enable_last_viewed_item, bool)
        assert isinstance(enable_same_category, bool)
        super(Logic, self).__init__({
            'name': name,
            'displayName': display_name,
            'active': active,
            'numberOfRec': rec_count,
            'algType': alg_type,
            'algInstances': [x if isinstance(x, AlgInstance) else AlgInstance.from_dict(x) for x in alg_instances],
            'userFilter': user_filter,
            'useLocation': use_location,
            'enableLastViewedItem': enable_last_viewed_item,
            'delegateLogicName': complementary_logics,
            'enableUpdating': enable_updating,

            'itemFilterSrc': item_filter_src,
            'enableSameCategory': enable_same_category,
            'avlItemFilterMode': avl_item_filter_mode,

            'id': id,
            'createTime': create_time,
            'updateTime': update_time
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['name'], dict_obj['displayName'], dict_obj['active'], dict_obj['numberOfRec'],
                   dict_obj['algType'], dict_obj['algInstances'],
                   dict_obj.get('userFilter'),
                   dict_obj['useLocation'], dict_obj['enableLastViewedItem'],
                   dict_obj.get('delegateLogicName'), dict_obj['enableUpdating'],
                   dict_obj.get('itemFilterSrc'), dict_obj['enableSameCategory'], dict_obj['avlItemFilterMode'],
                   dict_obj.get('id'), dict_obj.get('createTime'), dict_obj.get('updateTime'))


class Campaign(dict):
    """ Structure for a recommendation campaign

    Fields:
        name (str): Campaign name/id.
        displayName (str): Campaign display name.
        startTime (long): Campaign start time in Epoch (milliseconds).
        endTime (long): Campaign end time in Epoch (milliseconds).
        logics (list): A list of "Logic" instances.

        id (int): The auto id.
        createTime (long): Campaign create time in Epoch (milliseconds).
        updateTime (long): Campaign update time in Epoch (milliseconds).
    """
    def __init__(self, group_id, name, display_name, start_time, end_time, logics=None, id=None, create_time=None, update_time=None):
        assert group_id and name and display_name
        assert 0 <= start_time and 0 <= end_time and start_time < end_time
        if logics is None:
            logics = []
        super(Campaign, self).__init__({
            'groupId': group_id,
            'name': name,
            'displayName': display_name,
            'startTime': start_time,
            'endTime': end_time,
            'logics': [x if isinstance(x, Logic) else Logic.from_dict(x) for x in logics],
            'id': id,
            'createTime': create_time,
            'updateTime': update_time
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['groupId'], dict_obj['name'], dict_obj['displayName'],
                   dict_obj['startTime'], dict_obj['endTime'],
                   dict_obj['logics]'],
                   dict_obj.get('id'), dict_obj.get('createTime'), dict_obj.get('updateTime'))


class Layout(dict):
    """ Structure for a recommendation layout generator.

    Fields:
        dataSrcName (str): The item info data source name/id.
        loName (str): The layout name/id.
        loTitle (str): The title of the layout.
        loTitleAlign (str): Alignment of the title, refer to "LayoutTitleAlignment" for valid values.
        loItemCnt (int): The total count of items.
        loItemWidth (int): The width of an item (px).
        loItemHeight (int): The height of an item (px).
        loItemMargin (int): The margin between items (px).
        loBGColor (str): Background color in "rgba(r,g,b,alpha)" format.
        loFGColor (str): Foreground color in "rgba(r,g,b,alpha)" format.
        loCol (int): Number of columns.
        loRow (int): Number of rows.
        loFontSize (int): Font size (px).

        loID (int): The auto id
    """

    def __init__(self, data_source, name,
                 title, title_align=LayoutTitleAlignment.CENTER,
                 item_count=10, item_width=200, item_height=200, item_margin=20,
                 bg_color='rgba(255,255,255,0)', fg_color='rgba(0,0,0,1)',
                 columns=5, rows=2, font_size=16):
        assert data_source and name and title
        data_source_name = data_source['name']\
            if isinstance(data_source, DataSource) and DataSource['contentType'] == DataSourceContentType.ITEM_INFO\
            else str(data_source)
        super(Layout, self).__init__({
            'dataSrcName': data_source_name,
            'loName': name,
            'loTitle': title,
            'loTitleAlign': title_align,
            'loItemCnt': item_count,
            'loItemWidth': item_width,
            'loItemHeight': item_height,
            'loItemMargin': item_margin,
            'loBGColor': bg_color,
            'loFGColor': fg_color,
            'loCol': columns,
            'loRow': rows,
            'loFontSize': font_size
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(dict_obj['dataSrcName'], dict_obj['loName'],
                   dict_obj['loTitle'], dict_obj.get('loTitleAlign'),
                   dict_obj.get('loItemCnt'), dict_obj.get('loItemWidth'), dict_obj.get('loItemHeight'),
                   dict_obj.get('loItemMargin'),
                   dict_obj.get('loBGColor'), dict_obj.get('loFGColor'),
                   dict_obj.get('loCol'), dict_obj.get('loRow'), dict_obj.get('loFontSize'))


class ER3(BaseApp):
    """ Encapsulate Etu Recommender (v3) API """

    __APP_NAME = 'ER3'
    __HOST = 'erhome.online.etunexus.com'
    __API_BASE = '/ER/V3/recsrv/v1'
    __SHIRO_CAS_BASE = '/ER/V3/shiro-cas'

    def __init__(self, cas, host=None, api_base=None, shiro_cas_base=None):
        """ Constructor of ER3 instance. """
        api_base = api_base if api_base else self.__API_BASE
        super(ER3, self).__init__(cas, ER3.__APP_NAME,
                                  api_host=host if host else self.__HOST,
                                  api_base=api_base if api_base else self.__API_BASE,
                                  shiro_cas_base=shiro_cas_base if shiro_cas_base else self.__SHIRO_CAS_BASE)

    # Group #
    def get_groups(self):
        """ Get group (list).

        Depending on the authorization of the user, the group(s) returned would be different. For a normal user, it is
        most likely only the group which the user belongs to.

        Arguments:
        Return:
            A list of ERGroup instances.
        """
        res = self.request_get('/group')
        return [ERGroup.from_dict(x) for x in res]

    # Data source #
    def get_data_sources(self, group):
        """ Get data source list in a group.

        Only the data sources in the group authorized to ER are returned, and it may be just a subset of the list
        returned from the same API in EMC.

        Arguments:
            group (obj or int): The emc.Group instance, ERGroup instance, or group id to get.
        Return:
            A list of ERDataSource instances.
        """
        assert group
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, ERGroup) else int(group)
        res = self.request_get('/group/{0}/data-source'.format(group_id))
        return [ERDataSource.from_dict(x) for x in res]

    # Logic #
    def get_logics(self, group):
        """ Get the recommendation logics in a group.

        Arguments:
            group (obj or int): The emc.Group instance, ERGroup instance, or group id to get.
        Return:
            A list of Logic instances.
        """
        assert group
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, ERGroup) else int(group)
        res = self.request_get('/group/{0}/logic'.format(group_id))
        return [Logic.from_dict(x) for x in res]

    def add_logic(self, group, logic):
        """ Add a new recommendation logic to a group.

        Arguments:
            group (obj or int): The emc.Group instance, ERGroup instance, or group id to add logic.
            logic (obj): The Logic instance to add.
        Return:
            A Logic instance as the added one (with fields filled by server, e.g. createTime).
        """
        assert group and logic and isinstance(logic, Logic)
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, ERGroup) else int(group)
        res = self.request_post('/group/{0}/logic'.format(group_id), logic)
        return Logic.from_dict(res)

    def update_logic(self, logic):
        """ Update a recommendation logic.

        Arguments:
            logic (obj): The Logic instance to update, with a valid "id".
        Return:
            A Logic instance as the updated one.
        """
        assert logic and isinstance(logic, Logic)
        logic_id = logic['id']
        assert logic_id
        res = self.request_post('/logic/{0}'.format(logic_id), logic)
        return Logic.from_dict(res)

    def del_logic(self, logic):
        """ Delete a recommendation logic.

        Arguments:
            logic (obj or int): The Logic instance or logic id to delete.
        Return:
            The logic id deleted. It must be the same as the one in argument.
        """
        assert logic
        logic_id = logic['id'] if isinstance(logic, Logic) else int(logic)
        assert logic_id
        res = self.request_del('/logic/{0}'.format(logic_id))
        assert res == logic_id
        return res

    # Campaign #
    def get_campaigns(self, group):
        """ Get the campaigns in a group.

        Arguments:
            group (obj or int): The emc.Group instance, ERGroup instance, or group id to get.
        Return:
            A list of Campaign instances.
        """
        assert group
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, ERGroup) else int(group)
        res = self.request_get('/group/{0}/campaign'.format(group_id))
        return [Campaign.from_dict(x) for x in res]

    def add_campaign(self, group, campaign):
        """ Add a new campaign to a group.

        Arguments:
            group (obj or int): The emc.Group instance, ERGroup instance, or group id to add campaign.
            campaign (obj): The Campaign instance to add.
        Return:
            A Campaign instance as the added one (with fields filled by server, e.g. createTime).
        """
        assert group and campaign and isinstance(campaign, Campaign)
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, ERGroup) else int(group)
        res = self.request_post('/group/{0}/campaign'.format(group_id), campaign)
        return Campaign.from_dict(res)

    def update_campaign(self, campaign):
        """ Update a campaign.

        Arguments:
            campaign (obj): The Campaign instance to update, with a valid "id".
        Return:
            A Campaign instance as the updated one.
        """
        assert campaign and isinstance(campaign, Campaign)
        campaign_id = campaign['id']
        assert campaign_id
        res = self.request_post('/campaign/{0}'.format(campaign_id), campaign)
        return Campaign.from_dict(res)

    def del_campaign(self, campaign):
        """ Delete a campaign.

        Arguments:
            campaign (obj or int): The Campaign instance or campaign id to delete.
        Return:
            The campaign id deleted. It must be the same as the one in argument.
        """
        assert campaign
        campaign_id = campaign['id'] if isinstance(campaign, Campaign) else int(campaign)
        assert campaign_id
        res = self.request_del('/campaign/{0}'.format(campaign_id))
        assert res == campaign_id
        return res

    # User filter #
    def get_user_filters(self, group):
        """ Get the user filters in a group.

        Arguments:
            group (obj or int): The emc.Group instance, ERGroup instance, or group id to get.
        Return:
            A list of UserFilter instances.
        """
        assert group
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, ERGroup) else int(group)
        res = self.request_get('/group/{0}/userfilter'.format(group_id))
        return [UserFilter.from_dict(x) for x in res]

    def add_user_filter(self, group, user_filter, file_path):
        """ Add a new user filter data.

        The user_filter argument is setting only, and it requires a file containing the user list data.
        The file format is standard CSV, and include at least a "uid" column as the user/customer id list.

        Arguments:
            group (obj or int): The emc.Group instance, ERGroup instance, or group id to add user filter.
            user_filter (obj): The UserFilter instance to add.
            file_path (str): The file path of the user list to upload.
        Return:
            A UserFilter instance as the added one (with fields filled by server, e.g. createTime).
        """
        assert group and user_filter and isinstance(user_filter, UserFilter)
        group_id = group['id'] if isinstance(group, Group) or isinstance(group, ERGroup) else int(group)
        res = self.request_upload('/group/{0}/userfilter'.format(group_id), user_filter, file_path)
        return UserFilter.from_dict(res)

    def update_user_filter(self, user_filter, file_path):
        """ Update an user filter data.

        The user_filter argument is setting only, and it requires a file containing the user list data.
        The file format is standard CSV, and include at least a "uid" column as the user/customer id list.

        Arguments:
            user_filter (obj): The UserFilter instance to update, with valid "id".
            file_path (str): The file path of the user list to upload.
        Return:
            A UserFilter instance as updated.
        """
        assert user_filter and isinstance(user_filter, UserFilter)
        user_filter_id = user_filter['id']
        assert user_filter_id
        res = self.request_upload('/userfilter/{0}'.format(user_filter_id), user_filter, file_path)
        return UserFilter.from_dict(res)

    def del_user_filter(self, user_filter):
        """ Delete an user filter.

        Arguments:
            user_filter (obj or int): The UserFilter instance or a user filter id to delete.
        Return:
            The user filter id deleted. It must be the same as the one in argument.
        """
        assert user_filter
        user_filter_id = user_filter['id'] if isinstance(user_filter, UserFilter) else int(user_filter)
        assert user_filter_id
        res = self.request_del('/userfilter/{0}'.format(user_filter_id))
        assert res == user_filter_id
        return res

    # Layout #
    def get_layout(self, logic):
        """ Get layout setting of a recommendation logic.

        If there is no layout saved for the given logic, it raises a 404 error. Client should handle the error.
        In this case, it is possible to create a new Layout instance with proper default value before further processing.

        Arguments:
            logic (obj or int): The Logic instance or a logic id to get layout.
        Return:
            A Layout instance.
        """
        assert logic
        logic_id = logic['id'] if isinstance(logic, Logic) else int(logic)
        res = self.request_get('/logic/{0}/layout'.format(logic_id))
        return Layout.from_dict(res)

    def update_layout(self, logic, layout):
        """ Add or update layout setting of a recommendation logic.

        Arguments:
            logic (obj or int): The Logic instance or a logic id to add/update layout.
            layout (obj): The Layout instance to add/update.
        Return:
            A Layout instance as added or updated.
        """
        assert logic and layout and isinstance(layout, Layout)
        logic_id = logic['id'] if isinstance(logic, Logic) else int(logic)
        res = self.request_post('/logic/{0}/layout'.format(logic_id), layout)
        return Layout.from_dict(res)
