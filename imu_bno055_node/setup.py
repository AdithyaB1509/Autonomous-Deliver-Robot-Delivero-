import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'imu_bno055_node'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # --- ADD THESE LINES ---
        # Include all launch files
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        # Include all config files (YAML)
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='delivero',
    maintainer_email='delivero@todo.todo',
    description='BNO055 IMU node for Delivero Bot',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Note: Ensure these paths match your folder structure exactly
            'imupub = imu_bno055_node.imupublisher:main',
            'imuodom = imu_bno055_node.imuodom:main',
        ],
    },
)