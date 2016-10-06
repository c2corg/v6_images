from setuptools import setup, find_packages


setup(
    name='c2corg_images',
    packages=find_packages(),
    entry_points="""\
      [console_scripts]
      resize_images = c2corg_images.scripts.resize_images:main
      migrate = c2corg_images.scripts.migrate:main
      """
)
