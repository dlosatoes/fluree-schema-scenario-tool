from setuptools import setup

setup(
    name='fsst',
    version="0.6.7",
    description="Fluree Schema Scenario Tool",
    long_description="Testing tool for schema and smart function unit tests for FlureeDB",
    author='Rob Meijer',
    author_email='pibara@gmail.com',
    url='https://github.com/pibara/fluree-schema-scenario-tool',
    license='BSD',
    py_modules=['fsst'],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'fsst = fsst:_main',
        ],
    },
    keywords='flureedb fluree flureeql',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=["base58", "aioflureedb>=0.6.4", "requests"],
    extras_require={'domainapi': ['jsonata>=0.2.3'], 'docker': ['docker']}
)
