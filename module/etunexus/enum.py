# -*- coding: utf-8 -*-


class AppId(object):
    """ Enum of app ids (str) """
    EMC = 'ETU-SHIELD'
    ER = 'ETU-RECOMMENDER'
    EI = 'ETU-INSIGHT'


class AppRoleName(object):
    """ Enum of roles of apps (str) """
    VIEWER = 'Viewer'
    OPERATOR = 'Operator'
    ADMIN = 'ADMIN'


class DataSourceContentType(object):
    """ Enum of data source content type (str) """
    BEHAVIOR = 'behavior'
    ITEM_INFO = 'item_info'
    USER_PROFILE = 'profile'
    USER_RANK = 'user_rank'


class DataSourceType(object):
    """ Enumeration of data source type (str) """
    EVENT_COLLECTOR = 'EVENT_COLLECTOR'
    IMPORTER = 'IMPORTER'
    FETCH = 'FETCH'
    UPLOAD = 'UPLOAD'


class LogicAlgType(object):
    """ Enumeration of recommendation logic type """
    USER_BASE = 'USER_BASE'
    ITEM_BASE = 'ITEM_BASE'
    RANK = 'RANK'
    KEYWORD = 'KEYWORD'


class LogicAvlItemFilterMode(object):
    """ Enumeration of recommendation logic item filter mode """
    DISABLED = 'DISABLED'
    INCLUDE = 'INCLUDE'
    EXCLUDE = 'EXCLUDE'


class LogicAlgorithmId(object):
    """ Enumeration of recommendation algorithm samples """
    INFO_INTEGRITY = 'Info_Integrity'
    ITEM_BASED_CF = 'ITEM_BASED_CF'
    LDA = 'LDA'
    RANKING = 'RANKING'
    RANKING_ITEMINFO = 'RANKING_ITEMINFO'
    SEARCH2CLICK = 'SEARCH2CLICK'
    USER_BASED_CF = 'USER_BASED_CF'
    ALS = 'ALS'


class EventAction(object):
    """ Enumeration of action samples used in algorithms """
    VIEW = 'view'
    CART = 'cart'
    ORDER = 'order'
    LIKE = 'like'
    SHARE = 'share'


class BandType(object):
    """ Enumeration of band types """
    GENE = "gene"
    COMBINE = "combine"
    UPLOAD = "upload"
    FIXED_GENE = "fixedgene"


class BandGeneOperator(object):
    """ Enumeration of operators for gene-based bands """
    LT = 'LT'
    LE = 'LE'
    EQ = 'EQ'
    GE = 'GE'
    GT = 'GT'
    IN = 'IN'
    BETWEEN = 'BETWEEN'
    # for list
    INC = 'INC'
    INCALL = 'INCALL'
    INCNONE = 'INCNONE'
    # for range list
    RINC = 'RINC'
    RINCALL = 'RINCALL'
    RINCNONE = 'RINCNONE'
    # partial comparison for listKINC = 'KINC'
    KINCALL = 'KINCALL'
    KINCNONE = 'KINCNONE'


class BandCombineOperator(object):
    """ Enumeration of operators for combined bands """
    UNION = 'UNION'
    INTERSECT = 'INTERSECT'
    EXCEPT = 'EXCEPT'
