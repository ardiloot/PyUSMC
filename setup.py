from setuptools import setup
import re

# Parse version
__version__ = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    open('PyUSMC/__init__.py').read()).group(1)

setup(name = "PyUSMC",
      version = __version__,
      author = "Ardi Loot",
      url = "https://github.com/ardiloot/PyUSMC",
      author_email = "ardi.loot@outlook.com",
      packages = ["PyUSMC"])
