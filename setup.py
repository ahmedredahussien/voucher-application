from setuptools import setup
# >python3 setup.py install --user

setup(
   name='voucher_project',
   version='1.0',
   description='Churning Customer Reactivation',
   author='ahmedreda',
   author_email='ahmedredahussien@gmail.com',
   packages=['src/main'],
   package_data={'src/main': ['*.yaml']},
   include_package_data=True,
   install_requires=['pandas','pyarrow', 's3fs==0.6.0','fsspec','pyyaml','fastapi','uvicorn[standard]','sqlalchemy'], #external packages as dependencies
)
