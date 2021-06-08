from setuptools import setup
from setuptools import find_packages
import clisearch

requirements = []
dependency_links = []


try:
    with open('requirements.txt') as f:
        for line in f:

            if line.startswith('--trusted-host'):
                continue

            if line.startswith('--extra-index-url'):
                dependency_links.append(line.replace('--extra-index-url', '').strip())
                continue

            requirements.append(line)


except FileNotFoundError:
    pass

setup_args = dict(
    name='clisearch',
    description='OTL CLI',
    packages=find_packages(),
    version=clisearch.__version__,
    url='https://github.com/ISGNeuroTeam/clisearch',
    author=clisearch.__author__,
    author_email=clisearch.__email__,
    install_requires=requirements,
    dependency_links=dependency_links,
    options={"bdist_wheel": {"universal": "1"}},
    data_files=[('', ['clisearch/clisearch.cfg'])],
    entry_points={
        'console_scripts': [
            'clisearch=clisearch.clisearch:main',
        ],
    }
)

setup(**setup_args)
