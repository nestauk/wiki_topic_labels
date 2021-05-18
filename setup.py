from setuptools import setup
from setuptools import find_namespace_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

common_kwargs = dict(
    version='0.1',
    license='MIT',
    install_requires=required,
    long_description=open('README.md').read(),
    url='https://github.com/nestauk/wiki_topic_labels',
    author='Joel Klinger',
    author_email='joel.klinger@nesta.org.uk',
    maintainer='Joel Klinger',
    maintainer_email='joel.klinger@nesta.org.uk',
    classifiers=[
        'Natural Language :: English',
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.7',
    include_package_data=True,
)

setup(name="wiki_topic_labels",
      packages=find_namespace_packages(where="."),
      package_dir={'': '.'},
      package_data={'': ['*.pysql']},
      **common_kwargs)
