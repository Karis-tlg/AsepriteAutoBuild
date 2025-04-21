import requests
import os
import sys
from packaging import version

ASEPRITE_REPOSITORY = 'aseprite/aseprite'
SKIA_REPOSITORY = 'aseprite/skia'
SKIA_RELEASE_FILE_NAME = 'Skia-Windows-Release-x64.zip'

def get_current_version():
    try:
        with open('version.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return '0.0.0'  

def get_aseprite_releases():
    response = requests.get(f'https://api.github.com/repos/{ASEPRITE_REPOSITORY}/releases')
    response.raise_for_status()
    return response.json()

def save_aseprite_tag(tag):
    with open('version.txt', 'w') as f:
        f.write(tag)

def clone_aseprite(tag):
    clone_url = f'https://github.com/{ASEPRITE_REPOSITORY}.git'
    git_cmd = f'git clone -b {tag} {clone_url} src/aseprite --depth 1'
    os.system(git_cmd)
    os.system('cd src/aseprite && git submodule update --init --recursive')

def get_latest_tag_skia():
    response = requests.get(f'https://api.github.com/repos/{SKIA_REPOSITORY}/releases/latest')
    response.raise_for_status()
    return response.json()['tag_name']

def download_skia_for_windows(tag):
    download_url = f'https://github.com/{SKIA_REPOSITORY}/releases/download/{tag}/{SKIA_RELEASE_FILE_NAME}'
    file_response = requests.get(download_url)
    file_response.raise_for_status()
    
    with open(f'src/{SKIA_RELEASE_FILE_NAME}', 'wb') as f:
        f.write(file_response.content)
    os.system(f'7z x src/{SKIA_RELEASE_FILE_NAME} -osrc/skia')

def main():
    current_version = get_current_version()
    releases = get_aseprite_releases()
    releases = sorted(releases, key=lambda x: x['created_at'], reverse=True)
    
    for release in releases:
        tag = release['tag_name']
        if not tag.startswith('v'):
            continue
        tag_version = tag[1:]  
        
        if version.parse(tag_version) > version.parse(current_version):
            if os.path.exists('src'):
                os.system('rm -rf src')
            os.makedirs('src', exist_ok=True)
            
            clone_aseprite(tag)
            save_aseprite_tag(tag)
            skia_tag = get_latest_tag_skia()
            download_skia_for_windows(skia_tag)

if __name__ == '__main__':
    main()
