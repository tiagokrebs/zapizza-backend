from setuptools import setup

requires = [
    'pyramid',
    'pyramid_jinja2',
    'deform>=2.0a2',
    'pyramid_sqlalchemy',
    'pyramid_tm'
]
setup(name='zapizza',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = zapizza:main
      [console_scripts]
      initialize_db = zapizza.scripts.initialize_db:main
      """
      )
