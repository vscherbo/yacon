#!/usr/bin/env python
# coding: utf-8
"""
https://yandex.ru/dev/connect/directory/api/concepts/examples/examples-docpage/
"""
import os
import sys
import logging
import json
import requests
import fire

API_HOST = 'https://api.directory.yandex.net/v6'
API_GROUPS_LIST = {'url': '%s/groups/' % API_HOST, 'method': 'GET'}
API_GROUP_MEMBERS = {'url': '%s/groups/_group_id_/members/' % API_HOST, 'method': 'GET'}
API_GROUP_ADD_MEMBER = {'url': '%s/groups/_group_id_/members/' % API_HOST, 'method': 'POST'}
API_GROUP_CREATE = {'url': '%s/groups/' % API_HOST, 'method': 'POST'}
API_DEPARTMENTS_LIST = {'url': '%s/departments/' % API_HOST, 'method': 'GET'}
API_DEPT_PATCH = {'url': '%s/departments/' % API_HOST, 'method': 'PATCH'}
API_USERS_LIST = {'url': '%s/users/' % API_HOST, 'method': 'GET'}
API_USER_PATCH = {'url': '%s/users/' % API_HOST, 'method': 'PATCH'}
API_USER_ALIAS = {'url': '%s/users/_user_id_/aliases/' % API_HOST, 'method': 'POST'}

class YandexConnect():
    """
    Base class for Yandex.Connect Directory API
    """
    host = 'https://api.directory.yandex.net/v6'
    api_group_list = {'url': '%s/groups/' % host, 'method': 'GET'}

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.__token = os.environ.get('TOKEN')
        assert self.__token is not None, 'env TOKEN is not defined'

    def run_api(self, api_call, payload=None, resource_id=None, pages=None):
        """ run API method
        params:
            api_call    dict with url and http_method
            payload     parameters for url
        """
        headers = {
            'Authorization': 'OAuth ' + self.__token,
            # 'User-Agent': USER_AGENT,
        }
        args_dic = {'url': api_call['url'], 'timeout': 10}

        args_dic['headers'] = headers
        if pages:
            payload['per_page'] = pages['per_page']
            payload['page'] = pages['page']

        if api_call['method'] == 'GET':
            method = requests.get
            args_dic['params'] = payload
            headers['Accept'] = 'application/json'
        elif api_call['method'] == 'POST':
            method = requests.post
            args_dic['json'] = payload
            headers['Content-Type'] = 'application/json; charset=utf-8'
        elif api_call['method'] == 'PATCH':
            method = requests.patch
            args_dic['json'] = payload
            args_dic['url'] += resource_id + '/'
            headers['Content-Type'] = 'application/json; charset=utf-8'
        elif api_call['method'] == 'DELETE':
            method = requests.delete
            args_dic['url'] += resource_id + '/'
        else:
            logging.error('Unknown HTTP method')
            return None

        logging.debug('args_dic=%s', args_dic)
        response = method(**args_dic)
        # В случае ошибки, бросим исключение.
        response.raise_for_status()
        # А если всё хорошо, то вернём json.
        response_data = response.json()
        return response_data

    def groups_list(self, payload):
        """ Get list of groups
        """
        return self.run_api(API_GROUPS_LIST, payload)

    def group_members(self, group_id):
        """ Get group members list
        """
        group_id = str(group_id) if isinstance(group_id, int) else group_id
        loc_api = API_GROUP_MEMBERS.copy()
        loc_api['url'] = loc_api['url'].replace('_group_id_', group_id)
        return self.run_api(loc_api)

    def group_add_member(self, group_id, payload):
        """ Add a member to group with group_id
        params:
            group_id    group id
            payload     '{"type": "user", "id":1130000038979341}'
        """
        group_id = str(group_id) if isinstance(group_id, int) else group_id
        loc_api = API_GROUP_ADD_MEMBER.copy()
        loc_api['url'] = loc_api['url'].replace('_group_id_', group_id)
        return self.run_api(loc_api, payload)

    def group_add_member_by_login(self, group_id, login):
        """ Add a member with login to group with group_id
        params:
            group_id    group's id
            login       user's login
        """
        user_id = self.user_id_by_login(login)
        payload = {}
        payload['type'] = 'user'
        payload['id'] = user_id
        return self.group_add_member(group_id, payload)


    def group_create(self, payload):
        """ Create a group
        """
        return self.run_api(API_GROUP_CREATE, payload)

    def departments_list(self, payload):
        """ Get list of departments
        """
        return self.run_api(API_DEPARTMENTS_LIST, payload)

    def dept_id_by_label(self, dept_label, payload=None):
        """ Get dept_id by it's label
        """
        ret_id = None
        if not payload:
            payload = {}
            payload['fields'] = 'label'
        elif 'label' not in payload['fields']:
            payload['fields'] += ',label'

        res = self.run_api(API_DEPARTMENTS_LIST, payload)
        found_dept = [dept for dept in res['result'] if dept['label'] == dept_label]
        if found_dept:
            ret_id = found_dept[0]["id"]
        return ret_id

    def dept_patch(self, dept_id, payload):
        """ Path department with dept_id
        """
        dept_id = str(dept_id) if isinstance(dept_id, int) else dept_id
        return self.run_api(API_DEPT_PATCH, resource_id=dept_id, payload=payload)

    def dept_patch_by_label(self, dept_label, payload):
        """ Path department with dept_label
        """
        dept_id = str(self.dept_id_by_label(dept_label))
        return self.run_api(API_DEPT_PATCH, payload, dept_id)

    def users_list(self, payload):
        """ Get list of users
        """
        return self.run_api(API_USERS_LIST, payload)

    def user_id_by_login(self, login):
        """ Get user_id by his/her login(nickname)
        """
        payload = {'nickname': login}
        res = self.run_api(API_USERS_LIST, payload)['result']
        #logging.debug('type(res)=%s', type(res))
        #logging.debug('type(res[0])=%s', type(res[0]))
        #logging.debug('len(res)=%s', len(res))
        return res[0]["id"]

    def user_patch(self, user_id, payload):
        """ Patch user with user_id
        """
        user_id = str(user_id) if isinstance(user_id, int) else user_id
        return self.run_api(API_USER_PATCH, resource_id=user_id, payload=payload)

    def user_alias(self, user_id, name):
        """ Set new alias to user with user_id
        """
        user_id = str(user_id) if isinstance(user_id, int) else user_id
        payload = {'name': name}
        loc_api = API_USER_ALIAS.copy()
        loc_api['url'] = loc_api['url'].replace('_user_id_', user_id)
        return self.run_api(loc_api, payload=payload)

def main():
    """ Just main() function
    """
    yacon = YandexConnect()
    res = None
    #res = yacon.run_api(API_GROUPS_LIST, {'fields': 'name,email'})
    #
    #res = yacon.groups_list({'fields': 'type,name,email,members,'})
    # id=18 _email_admins
    res = yacon.group_members(str(18))

    """
    res = yacon.departments_list(
        {'fields': 'name,email,parents,label,description',
         'page': 1,
         'per_page': 1000
        }
    )
    it_dept_id = yacon.dept_id_by_label(
        'it',
        {'fields': 'name,email,parents,description'}
        # {'fields': 'name,email,parents,label,description'}
    )
    logging.info('it_dept_id=%d', it_dept_id)
    """

    #res = yacon.dept_patch_by_label('it', {'description': 'Отдел информационных технологий'})

    #res = yacon.users_list({'fields': 'nickname,name,email,groups,'})

    # Error 422: res = yacon.user_patch(str(1130000038951366), {'email': 'v.scherbo@tabloled.ru'})
    # Error 422: res = yacon.user_patch(str(1130000038951366), {'nickname': 'v.scherbo'})
    #res = yacon.user_patch(str(1130000038951366), {'position': 'ИТ директор'})
    #res = yacon.user_patch(str(1130000038951366), {'is_enabled': False})
    #res = yacon.user_alias(str(1130000038951366), 'yacon')

    if res:
        logging.info(json.dumps(res, ensure_ascii=False, indent=4))

if __name__ == '__main__':
    LOG_FORMAT = '[%(filename)-21s:%(lineno)4s - %(funcName)20s()] \
            %(levelname)-7s | %(asctime)-15s | %(message)s'
    logging.basicConfig(stream=sys.stdout, format=LOG_FORMAT, level='DEBUG')
    # main()
    fire.Fire(YandexConnect)
