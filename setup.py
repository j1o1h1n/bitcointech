try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Bitcoin Tech',
    'author': 'John Lehmann',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'j1o1h1n@gmail.com',
    'version': '0.1',
    'install_requires': ['nose', "pycrypto", "ecdsa"],
    'packages': ['bitcointech'],
    'scripts': [],
    'name': 'bitcointech'
}

setup(**config)
