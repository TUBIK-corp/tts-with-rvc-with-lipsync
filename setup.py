from setuptools import setup, find_packages

setup(
    name='tts_with_rvc_with_lipsync',
    version='0.0.2',
    description='Text to RVC LipSync',
    author='Amadeus (Wasys)',
    packages=find_packages(), 
    install_requires=[
        'moviepy'
    ],
    Scripts=['tts_with_rvc_with_lipsync/functions.py']
)