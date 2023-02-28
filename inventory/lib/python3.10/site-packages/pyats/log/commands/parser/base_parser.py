from . import _base_parser_internal
from async_lru import alru_cache


class BaseResultsParser(_base_parser_internal.BaseResultsParser):
    pass


class Pattern(_base_parser_internal.BaseResultsParser):
    pass


class LogSection(_base_parser_internal.LogSection):

    @property
    @alru_cache()
    async def child_execute(self):
        super().child_execute()


class LogExecute(_base_parser_internal.LogExecute):
    pass