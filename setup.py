import setuptools
import os
import re

with open("README.md", "r") as fh:
    long_description = fh.read()

version="0.0.0"

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
    description="Py Social Login",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/udaykrishna/py-social-login/",
    install_requires=install_requires,
    extras_require=extras_require,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.9',
)