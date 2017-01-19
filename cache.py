from rest_framework_extensions.cache.decorators import (
    cache_response,
)

from rest_framework_extensions.etag.decorators import etag

from rest_framework_extensions.key_constructor.constructors import (
    bits,
    KeyConstructor,
)


class APIKeyConstructor(KeyConstructor):
    unique_method_id = bits.UniqueMethodIdKeyBit()
    format = bits.FormatKeyBit()
    language = bits.LanguageKeyBit()
    query_param = bits.QueryParamsKeyBit()
    args = bits.ArgsKeyBit()
    kwargs = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()

default_api_key_func = APIKeyConstructor()


