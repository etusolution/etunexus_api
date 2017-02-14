# -*- coding: utf-8 -*-

from baseapp import BaseApp
from emc import Group, DataSource
from enum import *


class AlgInstance(dict):
    """ Structure of an algorithm instance in the recommendation logic.

    AlgInstance is an ABC for all different algorithm structure. The inherited algorithm implementation should be named
    as "Alg_[algId]", e.g. Alg_USER_BASED_CF or Alg_ALS.

    Fields:
        algId (str): The algorithm id, every derived algorithm should have its own id, refer to 'LogicAlgorithmId' for samples
        weight (int): The weight of the algorithm in the linear combination to the recommendation logic result
        setting (object): The setting depend on the concrete algorithm implementation
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
        klass = globals()[alg_class_name]
        return klass.from_dict(dict_obj)


class Alg_USER_BASED_CF(AlgInstance):
    """ Structure of user-based CF algorithm

    Fields:
        (As 'setting' in AlgInstance)
        id (str): 'USER_BASED_CF'
        DATASOURCE (object): A emc.DataSource instance, or at least a dict with 'id' and 'name'
        TIMERANGE (int): The data time range to calculate
        action (list): A list of event actions to calculate, refer to 'EventAction' to samples
    """
    def __init__(self, weight, data_source, time_range, actions):
        assert data_source and time_range and actions and isinstance(actions, list)
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
    """ Structure of item-based CF algorithm

    Fields:
        (As 'setting' in AlgInstance)
        id (str): 'ITEM_BASED_CF'
        DATASOURCE (object): A emc.DataSource instance, or at least a dict with 'id' and 'name'
        TIMERANGE (int): The data time range to calculate
        action (list): A list of event actions to calculate, refer to 'EventAction' to samples
    """
    def __init__(self, weight, data_source, time_range, actions):
        assert data_source and time_range and actions and isinstance(actions, list)
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
    """ Structure of ranking algorithm

    Fields:
        (As 'setting' in AlgInstance)
        id (str): 'RANKING'
        DATASOURCE (object): A emc.DataSource instance, or at least a dict with 'id' and 'name'
        TIMERANGE (int): The data time range to calculate
        actionList (list): A list of event actions to calculate, refer to 'EventAction' to samples
        addNonCategoryRec (bool): Generate category-independent recommendation list or not
    """

    def __init__(self, weight, data_source, time_range, actions, gen_non_category_rec=True, delimiter=None):
        assert data_source and time_range and actions
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


class UserFilter(dict):
    """ Structure of a user filter setting

    Fields:
        name (str): Name/id
        displayName (str): Display name

        id (int): The auto id
        createTime (long): Create time in Epoch (milliseconds)
        updateTime (long): Update time in Epoch (milliseconds)
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
    """ Structure of a recommendation logic

    Fields:
        name (str): Name/id
        displayName (str): Display name
        active (bool): Active or not
        numberOfRec (int): Max count of recommendation results
        algType (str): The logic algorithm type, refer to 'LogicAlgType' enum for valid values
        algInstances (list): Algorithm instances in the logic
        userFilter (object): User filter setting
        useLocation (bool): Use location or not
        delegateLogicName (str): The logic(s) for recommendation complementary
        enableUpdating (bool): Enable core engine process or not.

        ## Item Filtering (only for altType==ITEM_BASE)
        enableLastViewedItem (bool): Enable last viewed item recommendation or not (algType=ITEM_BASE)
        itemFilterSrc (str): The item info data source used for filtering
        enableSameCategory (bool): Enable item in same category recommendation or not
        avlItemFilterMode (str): The item avl filter mode, refer to 'LogicAvlItemFilterMode' enum for valid values

        id (int): The auto id
        createTime (long): Create time in Epoch (milliseconds)
        updateTime (long): Update time in Epoch (milliseconds)
    """
    def __init__(self, name, display_name, active, rec_count,
                 alg_type, alg_instances,
                 user_filter=None,
                 use_location=False, enable_last_viewed_item=False,
                 complementary_logics=None, enable_updating=True,
                 item_filter_src=None, enable_same_category=False, avl_item_filter_mode=LogicAvlItemFilterMode.DISABLED,
                 id=None, create_time=None, update_time=None):
        assert name and display_name and rec_count
        assert active and isinstance(active, bool)
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
        name (str): Campaign name
        displayName (str): Campaign display name
        startTime (long): Campaign start time in Epoch (milliseconds)
        endTime (long): Campaign end time in Epoch (milliseconds)
        logics (list): A list of 'Logic' instances
        id (int): The auto id
        createTime (long): Campaign create time in Epoch (milliseconds)
        updateTime (long): Campaign update time in Epoch (milliseconds)
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
    """ Structure for recommendation layout generator

    Fields:
        dataSrcName (str): The item info data source name/id
        loName: The layout name/id
        loTitle": "首頁推薦",
        loTitleAlign": "center",
        loItemCnt": 10,
        loItemWidth": 300,
        loItemHeight": 240,
        loItemMargin": 20,
        loBGColor": "rgba(255,255,255,1)",
        loFGColor": "rgba(0,0,0,1)",
        loCol": 5,
        loRow": 2,
        loFontSize": 16

        loID (int): The auto id
    """

    def __init__(self):
        super(Layout, self).__init__({
        })

    @classmethod
    def from_dict(cls, dict_obj):
        return cls()


class ER3(BaseApp):
    """ Encapsulate Etu Recommender (v3) API """

    __APP_NAME = 'ER3'
    __HOST = 'erhome.online.etunexus.com'
    __API_BASE = '/ER/V3/recsrv/v1'
    __SHIRO_CAS_BASE = '/ER/V3/shiro-cas'

    def __init__(self, cas, host=None, api_base=None, shiro_cas_base=None):
        """ Constructor """

        api_base = api_base if api_base else self.__API_BASE
        super(ER3, self).__init__(cas, ER3.__APP_NAME,
                                  api_host=host if host else self.__HOST,
                                  api_base=api_base if api_base else self.__API_BASE,
                                  shiro_cas_base=shiro_cas_base if shiro_cas_base else self.__SHIRO_CAS_BASE)

    # Logic #
    def get_logics(self, group):
        assert group
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_get('/group/{0}/logic'.format(group_id))
        return [Logic.from_dict(x) for x in res]

    def add_logic(self, group, logic):
        assert group and logic and isinstance(logic, Logic)
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_post('/group/{0}/logic'.format(group_id), logic)
        return Logic.from_dict(res)

    def update_logic(self, logic):
        assert logic and isinstance(logic, Logic)
        logic_id = logic['id']
        assert logic_id
        res = self.request_post('/logic/{0}'.format(logic_id), logic)
        return Logic.from_dict(res)

    def del_logic(self, logic):
        assert logic
        logic_id = logic['id'] if isinstance(logic, Logic) else logic
        assert logic_id
        return self.request_del('/logic/{0}'.format(logic_id))

    # Campaign #
    def get_campaigns(self, group):
        assert group
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_get('/group/{0}/campaign'.format(group_id))
        return [Campaign.from_dict(x) for x in res]

    def add_campaign(self, group, campaign):
        assert group and campaign and isinstance(campaign, Campaign)
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_post('/group/{0}/campaign', campaign)
        return Campaign.from_dict(res)

    def update_campaign(self, campaign):
        assert campaign and isinstance(campaign, Campaign)
        campaign_id = campaign['id']
        assert campaign_id
        res = self.request_post('/campaign/{0}'.format(campaign_id), campaign)
        return Campaign.from_dict(res)

    def del_campaign(self, campaign):
        assert campaign
        campaign_id = campaign['id'] if isinstance(campaign, Campaign) else int(campaign)
        assert campaign_id
        return self.request_del('/campaign/{0}'.format(campaign_id))

    # User filter #
    def get_user_filters(self, group):
        assert group
        group_id = group['id'] if isinstance(group, Group) else int(group)
        res = self.request_get('/group/{0}/userfilter'.format(group_id))
        return [UserFilter.from_dict(x) for x in res]

    def add_user_filter(self, group_id, user_filter, file_path):
        assert group_id and user_filter and isinstance(user_filter, UserFilter)
        res = self.request_upload('/group/{0}/userfilter'.format(group_id), user_filter, file_path)
        return UserFilter.from_dict(res)

    def update_user_filter(self, user_filter, file_path):
        assert user_filter and isinstance(user_filter, UserFilter)
        user_filter_id = user_filter['id']
        assert user_filter_id
        res = self.request_upload('/userfilter/{0}'.format(user_filter_id), user_filter, file_path)
        return UserFilter.from_dict(res)

    def del_user_filter(self, user_filter):
        assert user_filter
        user_filter_id = user_filter['id'] if isinstance(user_filter, UserFilter) else int(user_filter)
        assert user_filter_id
        return self.request_del('/userfilter/{0}'.format(user_filter_id))

    # Layout #
    def get_layouts(self, group_id):
        assert group_id
        res = self.request_get('/group/{0}/layout'.format(group_id))
        return [Layout.from_dict(x) for x in res]

    def add_layout(self, group_id, layout):
        assert group_id and layout and isinstance(layout, Layout)
        res = self.request_post('/group/{0}/layout'.format(group_id), layout)
        return Layout.from_dict(res)

    def update_layout(self, layout):
        assert layout and isinstance(layout, Layout)
        layout_id = layout['id']
        assert layout_id
        res = self.request_post('/layout/{0}'.format(layout_id), layout)
        return Layout.from_dict(res)

    def del_layout(self, layout):
        assert layout
        layout_id = layout['id'] if isinstance(layout, Layout) else int(layout)
        assert layout_id
        return self.request_del('/layout/{0}'.format(layout_id))
