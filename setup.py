from setuptools import setup, find_packages


setup(
    name='c2corg_images',
    packages=find_packages(),
    entry_points="""\
      [console_scripts]
      resize = c2corg_images.scripts.resize:Resizer.run
      migrate = c2corg_images.scripts.migrate:Migrator.run
      """
)
