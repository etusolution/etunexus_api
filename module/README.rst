etunexus
========

Etunexus is an GPL-licensed SDK encapsulating the API to interact with
`etunexus online service <https://www.etunexus.com/>`__.

It supports API of Etu Management Center (EMC) v2, Etu Recommender (ER)
v3, and Etu Insight (EI) v3.


Features
--------

-  Simplify the single-signon process with a simple login() call.
-  Encapsulate the protocol detail into easy-of-use objects, but still
   keep the flexibility for adjustment.


Quick start
-----------

Etuneuxs online service provides a rich and full-featured API entries
for every client supporting RESTful programming model to manipulate the
data and settings. It also provides a single-sign-on (SSO) service that
multiple applications can share the same user login authentication.

However, for a Python programmer, it is still complicated to code the
SSO process with involving two stages communication between SSO server
and application server from the ground. The SDK wraps it as a simple
login() call as:

.. code-block:: pycon

    >>> from etunexus.cas import *
    >>> from etunexus.emc import *
    >>>
    >>> cas = CAS([user_group], [user_name], [password])
    >>> # It is optional to make SSO login first.
    >>> cas.login()
    'TGT-147-ZRV9j9fy2mv2wZujOKMyaFlOeKXJqvf9S6jBcWeJ39vb1TzKaY-cas.etu.im'
    >>>
    >>> # Login application
    >>> emc2 = EMC2(cas)
    >>> emc2.login()
    'ST-232-wUwi0bNFhB66Xxr4wM7o-cas.etu.im'

The subsequent API call is also trivial with the methods of the
application object. For example, it is easy to get the group list and
the user list in a group (of course, for an authorized account only)
with:

.. code-block:: pycon

    >>> # Get all groups, and then find a specific group.
    >>> groups=emc2.get_groups()
    >>> workshop_group = filter(lambda x: x['name']=='workshop', groups)[0]
    >>> print workshop_group
    {'id': 2, 'displayName': u'Workshop Sample', 'name': u'workshop', 'createTime': 1484113449499}
    >>>
    >>> # Get all users, and then find a specific user
    >>> workshop_users = emc2.get_users(workshop_group)
    >>> workshop_user = filter(lambda x: x['name']=='workshop_user', workshop_users)[0]
    >>> print workshop_user
    {'displayName': u'Workshop User', 'name': u'workshop_user', 'roles': [{'roleName': u'Operator', 'appId': u'ETU-INSIG
    HT'}, {'roleName': u'Viewer', 'appId': u'ETU-RECOMMENDER'}], 'lastUpdateTime': 1487399443855, 'createTime': 14841296
    56168, 'department': u'', 'mail': u'', 'password': None, 'id': 3}

It is worthy of noticing that the data returned are wrapped into
objects/classes:

.. code-block:: pycon

    >>> type(workshop_group)
    <class 'etunexus.emc.Group'>
    >>> type(workshop_user)
    <class 'etunexus.emc.User'>

To manipulate the data, for example, add a user to the group. First,
create an object as the data with the constructor already properly
designed:

.. code-block:: pycon

    >>> new_user=User('new_workshop_user', 'New workshop user', 'password')
    >>> emc2.add_user(workshop_group, new_user)
    {'createTime': 1487735435494, 'department': u'', 'displayName': u'New workshop user', 'id': 15, 'lastUpdateTime': 14
    87735435494, 'mail': u'', 'name': u'new_workshop_user', 'password': None, 'roles': []}

And, it is easy to update the data with:

.. code-block:: pycon

    >>> update_user = filter(lambda x: x['name']=='new_workshop_user', workshop_users)[0]
    >>>
    >>> from etunexus.enum import *
    >>> update_user['roles']=[UserRole(AppRoleName.VIEWER, AppId.ER), UserRole(AppRoleName.VIEWER, AppId.EI)]
    >>>
    >>> emc2.update_user(update_user)
    {'createTime': 1487735435494, 'department': u'', 'displayName': u'New workshop user', 'id': 15, 'lastUpdateTime': 14
    87736051534, 'mail': u'', 'name': u'new_workshop_user', 'password': None, 'roles': [{'appId': u'ETU-RECOMMENDER', 'r
    oleName': u'Viewer'}, {'appId': u'ETU-INSIGHT', 'roleName': u'Viewer'}]}

Finally, delete a resource is also as simple as:

.. code-block:: pycon

    >>> emc2.del_user(update_user)
    15

Similar programming model for other applications (ER and EI). Please
refer to pydoc for detail. There are also samples in `GitHub
repository <https://github.com/etusolution/etunexus_api.git>`__.


Installation
------------

Etunexus is in PyPI. It can be installed easily directly with:

.. code-block:: bash

    $ pip install etunexus

Or, from Github:

.. code-block:: bash

    $ git clone https://github.com/etusolution/etunexus_api.git
    $ cd etunexus_api/module
    $ python setup.py install

Documents generation
--------------------

After installed the SDK, the document of modules can be viewed with
following:

.. code-block:: bash

    $ pydoc etunexus.emc
    $ pydoc etunexus.er
    $ pydoc etunexus.ei
    $ pydoc etunexus.enum

Or, you can generate the HTML edition with "pydoc -w". For example,
following line generate an etunexus.emc.html.

.. code-block:: bash

    $ pydoc -w etunexus.emc

Resources
---------

-  `GitHub
   repository <https://github.com/etusolution/etunexus_api.git>`__