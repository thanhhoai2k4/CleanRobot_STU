from setuptools import setup

package_name = 'clean_robot_perception'

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
            ['launch/perception.launch.py']
        ),
    ],

    install_requires=['setuptools'],

    zip_safe=True,

    maintainer='asus',

    maintainer_email='asus@todo.todo',

    description='Perception package',

    license='Apache License 2.0',

    entry_points={

        'console_scripts': [

            'trash_detector_node = clean_robot_perception.trash_detector_node:main',

            'trash_localization_node = clean_robot_perception.trash_localization_node:main',

            'trash_tracker_node = clean_robot_perception.trash_tracker_node:main',

            'trash_marker_node = clean_robot_perception.trash_marker_node:main',

            'fake_trash_candidate_node = clean_robot_perception.fake_trash_candidate_node:main',

            'camera_dataset_capture_node = clean_robot_perception.camera_dataset_capture_node:main',
        ],
    },
)
