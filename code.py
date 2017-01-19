#!/usr/bin/env python
#coding:utf-8

"""
Response code/message mapping

```
HTTP CODE => [code, message]
```

"""
from lucommon import status


class Mapping(object):
    """
    HTTP CODE => [code, message]
    """
    #####################
    #   Add more here   #
    #####################
    qc_code = {
        200: [status.LU_0_SUCCESS, '请求成功'],
        201: [status.LU_0_SUCCESS, '请求成功'],
        204: [status.LU_0_SUCCESS, '请求成功'],
        400: [status.LU_4000_FAIL, '请求失败'],
        401: [status.LU_4001_UNAUTHORIZED, '访问权限不够'],
        404: [status.LU_4004_NOT_FOUND, '资源不存在'],
        500: [status.LU_5000_SERVER_ERROR, '服务器错误'],
    }


class LuCode(Mapping):
    """
    Codec for code mapping
    """

    def __init__(self, http_code=200):
        self.http_code = http_code

    @property
    def code(self):
        return self.qc_code[self.http_code][0] if self.http_code in self.qc_code else -1

    @property
    def message(self):
        return self.qc_code[self.http_code][1] if self.http_code in self.qc_code else '`code` need to be defined!'


