__author__ = 'Khiem Doan'
__github__ = 'https://github.com/khiemdoan'
__email__ = 'doankhiem.crazy@gmail.com'
__url__ = 'https://github.com/khiemdoan/clean-architecture-python-boilerplate/blob/main/src/templates/__init__.py'

__all__ = ['arender', 'render']

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

this_dir = Path(__file__).parent
env = Environment(
    loader=FileSystemLoader(this_dir),
    autoescape=select_autoescape(['html', 'xml']),
)


def render(file: str, context: dict[str, Any] = {}, **kwargs) -> str:
    template = env.get_template(file)
    return template.render(context, **kwargs)


async def arender(file: str, context: dict[str, Any] = {}, **kwargs) -> str:
    template = env.get_template(file)
    return template.render_async(context, **kwargs)
