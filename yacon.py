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

API_HOST = 'https://api.directory.yandex.net/v6'
API_GROUPS_LIST = {'url': '%s/groups/' % API_HOST, 'method': 'GET'}
API_DEPARTMENTS_LIST = {'url': '%s/departments/' % API_HOST, 'method': 'GET'}
API_DEPT_PATCH = {'url': '%s/departments/' % API_HOST, 'method': 'PATCH'}

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

    def run_api(self, api_call, payload, resource_id=None, pages=None):
        """ run API method
        params:
            api_call    dict with url and http_method
            payload     parmaters for url
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

    def departments_list(self, payload):
        """ Get list of departments
        """
        return self.run_api(API_DEPARTMENTS_LIST, payload)

    def dept_patch(self, dept_id, payload):
        """ Get list of departments
        """
        return self.run_api(API_DEPT_PATCH, payload, dept_id)



def main():
    """ Just main() function
    """
    log_format = '[%(filename)-21s:%(lineno)4s - %(funcName)20s()] \
            %(levelname)-7s | %(asctime)-15s | %(message)s'
    logging.basicConfig(stream=sys.stdout, format=log_format, level='DEBUG')
    yacon = YandexConnect()
    #res = yacon.run_api(API_GROUPS_LIST, {'fields': 'name,email'})
    #
    #res = yacon.groups_list({'fields': 'type,name,email,members,'})
    res = yacon.departments_list(
        {'fields': 'name,email,parents,label,description',
         'page': 1,
         'per_page': 1000
        }
    )
    #res = yacon.dept_patch(str(2), {'description': 'Отдел Информационных Технологий'})


    logging.info(json.dumps(res, ensure_ascii=False, indent=4))

if __name__ == '__main__':
    main()
