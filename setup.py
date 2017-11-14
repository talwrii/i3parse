import setuptools
import os

HERE = os.path.dirname(__file__)

setuptools.setup(
    name='i3parse',
    version="0.1.0",
    author='Tal Wrii',
    author_email='talwrii@gmail.com',
    description='',
    license='GPLv3',
    keywords='',
    url='',
    packages=['i3parse'],
    long_description='See https://github.com/talwrii/i3parse',
    entry_points={
        'console_scripts': ['i3parse=i3parse.i3parse:main']
    },
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ],
    test_suite='nose.collector',
    install_requires=[]
)
