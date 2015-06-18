"""
Deploy Docker containers with Fabric.
"""
from setuptools import find_packages, setup

with open('requirements.txt') as f:
    dependencies = f.read().splitlines()

setup(
    name='fabdocker',
    version='0.2.0',
    url='https://github.com/DandyDev/fabdocker',
    license='MIT',
    author='Daan Debie',
    author_email='debie.daan@gmail.com',
    description='Deploy Docker containers with Fabric.',
    long_description='Deploy Docker containers with Fabric.',
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        # 'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ]
)
