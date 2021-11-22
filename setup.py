from setuptools import setup
setup(
    data_files=[
        ('lib/systemd/user', ['picec.service']),
        ('share/systemd/user', ['picec.service']),
    ],
)
