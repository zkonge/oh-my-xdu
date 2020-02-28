from defopt import _create_parser

from ohmyxdu.globals import get_current_omx


def show():
    """显示当前可用的插件"""

    app = get_current_omx()

    min_width = max(len(f.__name__) for f in app.plugins) + 1
    print('插件名称'.center(min_width), '插件介绍'.center(min_width))
    print('=' * min_width * 2)
    for plugin in app.plugins:
        parsed = _create_parser(plugin)  # TODO: 性能提升
        print(plugin.__name__.replace('_', '-').ljust(min_width), parsed.description.ljust(min_width))
