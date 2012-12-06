from setuptools import setup, find_packages

long_description = ""
try:
    readme = open("README.rst")
    long_description = str(readme.read())
    readme.close()
except:
    pass

VERSION = (1, 0, 0, 'a', 1)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3] != 'f':
        version = '%s%s%s' % (version, VERSION[3], VERSION[4])
    return version


setup(
    name='django-comments-plus',
    version=get_version(),
    description="Extended django.contrib.comments, reviews, authorization via comment-form, ajax submit and validation, subscription/unsubscribing (+web-interface)",
    long_description=long_description,
    keywords='django, comments',
    author='Mikhail Andreev',
    author_email='x11org@gmail.com',
    url='http://github.com/adw0rd/django-comments-plus',
    license='BSD',
    packages=find_packages(),
    zip_safe=False,
    install_requires=['setuptools', ],
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
