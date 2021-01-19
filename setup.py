from distutils.core import setup
import os

version = (('version' in os.environ) and os.environ['version'] or "0.0.1")

NAME_PROJECT = "downloader_postal_code"

with open("{}/version.py".format(NAME_PROJECT), "w") as f:
    f.write("__version__ = '{0}'\n".format(version))

if __name__ == "__main__":
    setup(
        name=NAME_PROJECT,
        version=version,
        author='ammosov',
        author_email='ammosovdaniil@gmail.com',
        packages=[
            NAME_PROJECT,
            "{}/parsers".format(NAME_PROJECT),
            "{}/db".format(NAME_PROJECT)
        ],
        scripts=["scripts/deploy_postal_code_db", "scripts/download_postal_code"],
        requires=['sqlalchemy', 'alembic', "requests"],
        data_files=[
            ("/var/lib/{}".format(NAME_PROJECT), ["alembic/script.py.mako", "alembic/env.py", "alembic/README"]),
            ("/var/lib/{}/versions".format(NAME_PROJECT), ["alembic/versions/ed65b559ace1_creates_addr_objects_and_house_objects_.py"]),
            ("/etc/{}".format(NAME_PROJECT), ["config/{}.ini".format(NAME_PROJECT), "config/{}.json".format(NAME_PROJECT)]),
            ("/etc/cron.d", ['cron.d/{}'.format(NAME_PROJECT)]),
        ],
        description='Package for a deploying db of postal indexes '
    )
