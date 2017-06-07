# -*- coding: utf-8 -*-


class AppId(object):
    """ Enum of app ids """
    EMC = 'ETU-SHIELD'
    ER = 'ETU-RECOMMENDER'
    EI = 'ETU-INSIGHT'


class AppRoleName(object):
    """ Enum of roles of apps """
    VIEWER = 'Viewer'
    OPERATOR = 'Operator'
    ADMIN = 'ADMIN'


class DataSourceContentType(object):
    """ Enum of data source content type """
    BEHAVIOR = 'behavior'
    ITEM_INFO = 'item'
    USER_PROFILE = 'userprofile'
    USER_RANK = 'userrank'


class DataSourceType(object):
    """ Enumeration of data source type """
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
    UNKNOWN = 'UNKNOWN'
    USER_BASED_CF = 'USER_BASED_CF'
    ITEM_BASED_CF = 'ITEM_BASED_CF'
    RANKING = 'RANKING'
    RANKING_ITEMINFO = 'RANKING_ITEMINFO'
    SEARCH2CLICK = 'SEARCH2CLICK'
    INFO_INTEGRITY = 'Info_Integrity'
    ALS = 'ALS'
    LDA = 'LDA'


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


class GeneType(object):
    """ Enumeration of gene types. It is also for fixed (external) gene """
    SET = 'set'
    DATE = 'date'
    PERCENT = 'percent'
    HOURS = 'hours'
    SET_KEYWORD = 'set_keyword'
    NUMBER_TIME = 'number_time'
    NUMBER = 'number'
    WEEKDAYS = 'weekdays'
    RANGE_DATE = 'range_date'


class GeneChartType(object):
    """ Enumeration of gene chart types. It is also for fixed (external) gene """
    SEMIDONUT = 'semidonut'
    BAR = 'bar'
    LINE = 'line'
    COLUMN = 'column'
    HEATMAP_DATE = 'heatmap_date'


class EIStatisticsItem(object):
    """ Enumeration of EI statistics item name """
    DOWNLOAD_UID_LIST = 'downloadUidList'
    ADD_BAND = 'addBand'
    UPDATE_BAND = 'updateBand'
    BAND_COUNT = 'bandCount'


class EIPopulationTimelineFilterOP(object):
    """ Enumeration of EI population timeline filter op """
    LT = 'LT'
    LE = 'LE'
    EQ = 'EQ'
    GE = 'GE'
    GT = 'GT'
    NE = 'NE'


class EIPopulationTimelineFilterCompType(object):
    """ Enumeration of EI population timeline filter comparator type """
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    SUBSTRING = 'SUBSTRING'


class LayoutTitleAlignment(object):
    """ Enumeration of ER logic layout title alignment """
    CENTER = 'center'
    LEFT = 'left'
    RIGHT = 'right'
