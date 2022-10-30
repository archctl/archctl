"""archctl configuration."""
from setuptools import setup

version = "0.0.1"

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

requirements = [
    'click>=7.0,<9.0.0',
    'PyInquirer'
]

setup(
    name='archctl',
    version=version,
    description=(
        'A command-line utility that uses cookiecutter to '
        'perform actions on company repos, such as rendering  '
        'the archetype to update a project.'
    ),
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Adrian Garcia',
    author_email='adriangarciasb@outlook.com',
    url='https://github.com/archctl/archctl',
    packages=['archctl'],
    package_dir={'archctl': 'archctl'},
    entry_points={'console_scripts': ['archctl = archctl.__main__:main']},
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=requirements,
    license='GPL-3.0',
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    keywords=[
        "archctl",
        "Python",
        "projects",
        "project templates",
        "project directory",
        "package",
        "packaging",
    ],
)