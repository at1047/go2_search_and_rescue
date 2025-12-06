from setuptools import setup
import os
from glob import glob

package_name = 'go2_sar_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Install launch files
        ('share/' + package_name + '/launch', glob('launch/*.py')),

        # Install config files (YAML)
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='unitree',
    maintainer_email='unitree@todo.todo',
    description='SAR navigation and exploration stack for Unitree Go2',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_navigator = go2_sar_pkg.simple_navigator:main',
            'odom_tf_broadcaster = go2_sar_pkg.odom_tf_broadcaster:main',
            'odom_tf_broadcaster2 = go2_sar_pkg.odom_tf_broadcaster2:main',
            'odom_tf_broadcaster3 = go2_sar_pkg.odom_tf_broadcaster3:main',
            'odom_tf_broadcaster4 = go2_sar_pkg.odom_tf_broadcaster4:main',
            'local_costmap = go2_sar_pkg.local_costmap:main',
            'fake_dog_maps = go2_sar_pkg.fake_dog_maps:main',
            ],
    },
)

