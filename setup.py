import os

from setuptools import setup, find_packages


def parse_requirements(filename):
    req_list = []
    try:
        script_directory = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(script_directory, filename)) as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0 or line[0] == '#':
                    continue
                req_list.append(line)
    except IOError:
        return []
    return req_list


install_requires = parse_requirements('requirements.txt')
tests_require = parse_requirements('requirements_test.txt')

setup(
    name='strava-flow',
    version='0.0.1',
    url='https://github.com/vmarceau/strava-flow',
    author='Vincent Marceau',
    author_email='vmarceau@gmail.com',
    packages=find_packages(exclude=['tests*']),
    data_files=[],
    package_data={
        'readme': ['README.md'],
        'strava_flow': ['py.typed']
    },
    install_requires=install_requires,
    test_suite='tests',
    tests_require=tests_require,
    include_package_data=True,
    zip_safe=False
)
