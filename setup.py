"""archctl configuration."""
from setuptools import setup

version = "0.1.1"

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

requirements = [
    'click',
    'InquirerPy',
    'cookiecutter'
]

setup(
    name='archctl',
    version=version,
    description=(
        'A command-line utility that wraps the use of cookiecutter and'
        'manages both Templates and Projects GitHub Repositories'
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
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
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
