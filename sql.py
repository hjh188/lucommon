"""
Do the raw SQL injection execution
"""

import re
import pyparsing

from django.conf import settings
from django.db import connections

from lucommon.logger import lu_logger
from lucommon.exception import (
    LuSQLNotAllowError,
    LuSQLSyntaxError,
)

from lucommon.confs import LuSQLConf
from lucommon.simpleSQL import (
    simpleSELECT,
    simpleSEARCH,
)

from lucommon import sql_func

class LuSQL(object):
    """
    Raw SQL Interface, efficient for multiple table SQL
    """
    def __init__(self, db, sql, sql_param=[], allow_sql=['SELECT'], map_sql={},
                       search_condition='', conf_sql={},
                       limit=settings.DEFAULT_LIMIT, offset=0,
                       response_field=None, request=None):
        self._db = db
        self._sql = sql
        self._sql_param = sql_param
        self._limit = limit
        self._offset = offset
        self._conf_sql = conf_sql
        self.__filter_sql(allow_sql, map_sql, search_condition, conf_sql, response_field)
        self._conn = connections[self._db]
        self._cursor = self._conn.cursor()
        self._request = request

    def __del__(self):
        try:
            self._cursor.close()
            self._conn.commit()
        except Exception, err:
            lu_logger.error(str(err))

    def execute(self):
        """
        Raw SQL execution
        """
        try:
            lu_logger.info(self._sql)

            if self._sql_param:
                self._cursor.execute(self._sql, self._sql_param)
            else:
                self._cursor.execute(self._sql)
        except Exception, err:
            raise LuSQLSyntaxError(str(err))

        if not self._sql.upper().startswith('SELECT'):
            return []

        fetchall = self._cursor.fetchall()

        col_names = [desc[0] for desc in self._cursor.description]

        data = []

        # Get LuSQLConf for response field
        conf_response = {}
        for key in self._conf_sql:
            if self._conf_sql[key].type == LuSQLConf.TYPE_RESPONSE:
                conf_response[self._conf_sql[key].value.split(' ')[-1]] = self._conf_sql[key].response_callback

        plain_data = True if self._request and 'lu_plain_data' in self._request.query_params else False

        for row in fetchall:
            dic = {} if not plain_data else []

            for index, value in enumerate(row):
                if col_names[index] in conf_response:
                    if not plain_data:
                        dic[col_names[index]] = conf_response[col_names[index]](value)
                    else:
                        dic.append(conf_response[col_names[index]](value))
                else:
                    if not plain_data:
                        dic[col_names[index]] = value
                    else:
                        dic.append(value)

            data.append(dic)

        try:
            pattern = re.compile(r'SELECT (.*?) FROM', re.IGNORECASE)
            count_sql = pattern.sub('SELECT count(*) FROM', self._sql)

            pattern = re.compile(r' limit (\d+) offset (\d+)', re.IGNORECASE)
            count_sql = pattern.sub('', count_sql)

            lu_logger.info(count_sql)

            if self._sql_param:
                self._cursor.execute(count_sql, self._sql_param)
            else:
                self._cursor.execute(count_sql)
        except Exception, err:
            raise LuSQLSyntaxError(str(err))

        count = self._cursor.fetchall()[0][0]

        # To compatible the previous version, push the count at the last element
        data.append(count)

        return data

    def __convert_sql(self, search_condition, conf_sql, response_field):
        """
        SQL runtime replacement and convertion
        """
        def find(src, obj, conf):
            tmp = src.strip('\"')
            tmp = tmp.strip('\'')

            if conf.mode in (LuSQLConf.MODE_FIXED, LuSQLConf.MODE_RUNTIME):
                if obj == tmp:
                    return True
            elif conf.mode in (LuSQLConf.MODE_CHANGED):
                try:
                    res = re.findall(obj, tmp)
                except Exception, err:
                    lu_logger.error(str(err))
                    res = None

                if res:
                    conf.value = eval(conf.value % res[0])
                    conf.key = tmp
                    return True

            return False

        if response_field:
            try:
                # TODO: smart analyzer and replacement
                response_fields = [item.strip() for item in response_field.split(settings.RESPONSE_FIELD_DELIMITER)]
                for i, field in enumerate(response_fields):
                    for key, conf in conf_sql.items():
                        if conf.type == LuSQLConf.TYPE_RESPONSE and find(field, key, conf):
                            response_fields[i] = conf.value
                response_field = ','.join(response_fields)
            except Exception, err:
                lu_logger.error(str(err))
            finally:
                self._sql = self._sql.replace('LU_RESPONSE_FIELD', response_field)
        else:
            self._sql = self._sql.replace('LU_RESPONSE_FIELD', '*')

        if search_condition:
            #TODO: smart analyzer and replacement
            try:
                parsed_sql = simpleSEARCH.parseString(search_condition)
                where = parsed_sql.where
                order_by = parsed_sql.order_by
                group_by = parsed_sql.group_by

                output = []
                for cond in where:
                    if isinstance(cond, str):
                        # For operation, skip
                        output.append(cond)
                        continue
                    if cond[1] in ('not in', 'in'):
                        # something like this: [u'id', 'in', '(', u'1', u'2', u'3', ')']
                        for key, conf in conf_sql.items():
                            if conf.type == LuSQLConf.TYPE_VALUE:
                                for i, item in enumerate(cond[3:-1]):
                                    if find(item, key, conf):
                                        if conf.key:
                                            cond[3+i] = item.replace(conf.key, conf.value)
                                        else:
                                            cond[3+i] = item.replace(key, conf.value)
                                        break
                            elif conf.type == LuSQLConf.TYPE_KEY:
                                if find(cond[0], key, conf):
                                    cond[0] = cond[0].replace(key, conf.value)
                                    break
                        # assemble the cond
                        output.append(' '.join(cond[0:3] + [','.join(cond[3:-1]), cond[-1]]))
                    else:
                        # something like this: [u'username', '=', u"'test'"]
                        for key, conf in conf_sql.items():
                            if conf.type == LuSQLConf.TYPE_VALUE:
                                if find(cond[2], key, conf):
                                    if conf.key:
                                        cond[2] = cond[2].replace(conf.key, conf.value)
                                    else:
                                        cond[2] = cond[2].replace(key, conf.value)
                                    break
                            elif conf.type == LuSQLConf.TYPE_KEY:
                                if find(cond[0], key, conf):
                                    cond[0] = cond[0].replace(key, conf.value)
                                    break
                        # assemble the cond
                        output.append(' '.join(cond))

                # Process order by
                if order_by:
                    order_item = []

                    for item in order_by[1:]:
                        order_item.append(' '.join(item))

                    output.append(order_by[0] + ' ' + ','.join(order_item))

                # Build the search condition
                search_condition = ' '.join(output)
            except Exception, err:
                lu_logger.error(str(err))
            finally:
                self._conf_sql = conf_sql
                self._sql = self._sql.replace('LU_SEARCH_CONDITION', search_condition)
                lu_logger.info(self._sql)
        else:
            self._sql = self._sql.replace('LU_SEARCH_CONDITION', '1=1')

    def __filter_sql(self, allow_sql, map_sql, search_condition, conf_sql, response_field):
        """
        SQL filter is a security policy from lucommon,
        Allow and Deny policy here

        Usually, lucommon will do the sql map firstly,
        then do sql allow check.
        """
        # Do the sql mapping
        self._sql = map_sql.get(self._sql, self._sql)

        # Do the replacement and convertion
        # This will be specially important to lucommon SQL injection powerful
        self.__convert_sql(search_condition, conf_sql, response_field)

        # For limit and offset
        if str(self._limit) != settings.UNLIMIT and self._sql.upper().startswith('SELECT'):
            self._sql += ' LIMIT %d OFFSET %d' % (int(self._limit), int(self._offset))

        # Do the sql filtering
        for sql in allow_sql:
            patten = re.compile(sql, re.IGNORECASE)
            if patten.match(self._sql.strip()):
                return

        raise LuSQLNotAllowError('LU SQL injection only support for: %s' % str(allow_sql))


