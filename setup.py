from setuptools import setup, find_packages

requires =[
    'flask',
    'spotipy',
    'html5lib',
    'requests',
    'requests-html',
    'beautifulsoup4',
    'youtube_dl',
    'pathlib',
    'pandas',
    'bs4',
    'requests_html'
]

setup(
    name='Melody-Playlist Powered by Spotify',
    version='1.0.0',
    description='An application that converts Spotify playlists to instrumental Youtube playlists',
    author='Rimma Kubanova',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires
)