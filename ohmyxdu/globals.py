from contextvars import ContextVar

__all__ = ('get_config', 'set_config', 'get_current_omx', 'set_current_omx')

# 异步隔离
_config = ContextVar('global_config')
_current_omx = ContextVar('public_omx')


def get_config() -> dict:
    """
    获取全局配置

    提示：不要直接使用config中的 set_config 修改全局配置，
    持久化请直接修改 get_config 并调用 OMX 对象的 dump_config_file
    :return: 含有全局配置信息的 dict
    """

    try:
        return _config.get()
    except LookupError:
        raise LookupError('全局配置文件未初始化，OMX 对象初始化了吗？')


set_config = _config.set


def get_current_omx() -> "OMX":  # TODO: 解决循环 import
    """
    获取当前 OMX 对象

    可在异步环境下确保 OMX 一一对应
    :return:当前线程上下文中对应的 OMX 对象
    """

    try:
        return _current_omx.get()
    except LookupError:
        raise LookupError('当前线程上下文中的 OMX 对象未初始化')


set_current_omx = _current_omx.set
