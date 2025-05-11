from setuptools import setup, find_packages

setup(
    name='stmt-proc-py',
    version='1.0.0',
    author='Jayesh Prajapati',
    author_email='jayeshecs@gmail.com',
    description='A Python module for processing bank account and credit card statements.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jayeshecs/stmtmgr',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'xlrd',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)