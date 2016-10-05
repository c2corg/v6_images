from setuptools import setup, find_packages


setup(
    name='c2corg_images',
    packages=find_packages(),
    entry_points="""\
      [console_scripts]
      generate_thumbnails = c2corg_images.scripts.generate_thumbnails:main
      """
)
