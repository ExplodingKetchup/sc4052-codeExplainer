import base64
import os

import requests
from dotenv import load_dotenv

load_dotenv()

def search_code(keyword: str, repo: None|str=None, language: None|str=None, search_keyword_in_path: bool=False, search_exact: bool=False) -> None|str:
    query_string = ''
    if search_exact:
        query_string += f'"{keyword}"'
    else:
        query_string += keyword
    if repo is not None:
        query_string += f'+repo:{repo}'
    if language is not None:
        query_string += f'+language:{language}'
    if not search_keyword_in_path:
        query_string += '+in:file'

    search_result = ''
    url = f'https://api.github.com/search/code?q={query_string}&per_page=5'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {os.getenv('GITHUB_API_KEY')}',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    try:
        print(f'GET {url}')
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        items = response.json()['items']
        for item in items:
            file_content = get_file_content(item['url'])
            if file_content is not None:
                search_result += f'--- {item['repository']['full_name']}/{item['path']}'
                search_result += file_content
                search_result += '---'
    except requests.exceptions.HTTPError as err:
        print(f'HTTP error occurred: {err}')
    except KeyError as err:
        print(f'Response not in expected format: {err}')
    except Exception as err:
        print(f'An error occurred: {err}')
    return search_result


def get_file_content(url: str) -> None|str:
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {os.getenv('GITHUB_API_KEY')}',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    try:
        print(f'GET {url}')
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['type'] != 'file':
            print(f'Response is not a file, but a {data['type']}')
            return None
        if data['encoding'] != 'base64':
            print(f'Encoding of response is {data['encoding']}, cannot handle')
            return None
        return base64.b64decode(data['content']).decode(encoding='utf-8')
    except requests.exceptions.HTTPError as err:
        print(f'HTTP error occurred: {err}')
    except KeyError as err:
        print(f'Response not in expected format: {err}')
    except Exception as err:
        print(f'An error occurred: {err}')
    return None
