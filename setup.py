from setuptools import setup
setup(
    data_files=[
        ('lib/systemd/user', ['cecmap.service']),
        ('share/systemd/user', ['cecmap.service']),
    ],
)
