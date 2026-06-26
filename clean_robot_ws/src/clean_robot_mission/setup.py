from setuptools import setup

package_name = 'clean_robot_mission'

setup(
    name=package_name,
    version='0.0.1',

    packages=[package_name],

    data_files=[

        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),

        (
            'share/' + package_name,
            ['package.xml']
        ),

        (
            'share/' + package_name + '/launch',
            ['launch/mission.launch.py']
        ),
    ],

    install_requires=['setuptools'],

    zip_safe=True,

    maintainer='asus',

    maintainer_email='asus@todo.todo',

    description='Mission package',

    license='Apache License 2.0',

    entry_points={

        'console_scripts': [

            'target_manager_node = clean_robot_mission.target_manager_node:main',

            'mission_manager_node = clean_robot_mission.mission_manager_node:main',
        ],
    },
)
