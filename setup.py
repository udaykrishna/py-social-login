import setuptools
import os
import re

with open("README.md", "r") as fh:
    long_description = fh.read()


RE_VER = re.compile(r"^__version__ = ['\"]([^'\"]*)['\"]", re.M)

version = ''
with open("social_login/_version.py", "rt") as f:
    ver_cont = f.read()
    match_version = RE_VER.search(ver_cont)
    if match_version:
        version = match_version.group(1)

library_folder = os.path.dirname(os.path.realpath(__file__))
requirement_file_path = library_folder + '/requirements.txt'

install_requires = ['PyJWT', 'cryptography', 'pydantic', 'pytz', 'requests']
extras_require = {
    'dev': ['flask']
}

setuptools.setup(
    name="py_social_login", 
    version=version,
    author="Uday Krishna",
    author_email="uday@udaykrishna.com",
    description="Social Login",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/udaykrishna/py-social-auth/",
    install_requires=install_requires,
    extras_require=extras_require,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.9',
)