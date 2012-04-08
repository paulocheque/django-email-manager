#from distutils.core import setup
from setuptools import setup, find_packages

# http://guide.python-distribute.org/quickstart.html
# python setup.py sdist
# python setup.py register
# python setup.py sdist upload
# pip install django-email-manager
# pip install django-email-manager --upgrade --no-deps
# Manual upload to PypI
# http://pypi.python.org/pypi/django-email-manager
# Go to 'edit' link
# Update version and save
# Go to 'files' link and upload the file


tests_require = [
    'nose==1.1.2',
    'django-nose==0.1.3',
]

install_requires = [
]

setup(name='django-email-manager',
      url='https://github.com/paulocheque/django-email-manager',
      author="paulocheque",
      author_email='paulocheque@gmail.com',
      keywords='python django email',
      description='A simple application to store a summary of system e-mails.',
      license='MIT',
      classifiers=[
          'Framework :: Django',
          'Operating System :: OS Independent',
          'Topic :: Software Development'
      ],

      version='0.2.0',
      install_requires=install_requires,
      tests_require=tests_require,
      test_suite='runtests.runtests',
      extras_require={'test': tests_require},

      packages=find_packages(),
      include_package_data=True,
      package_data={
          'email_manager': [
              'templates/*',
              'templates/email_manager/*',
          ],
      },
)
