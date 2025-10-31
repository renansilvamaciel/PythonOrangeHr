import logging

logger = logging.getLogger(__name__)

'''
Exceptions
    Add quick explanation TODO

'''


class BusinessException(RuntimeError):
    ...


class SystemException(RuntimeError):
    ...


class InterruptException(RuntimeError):
    ...
