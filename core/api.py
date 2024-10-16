import requests
from urllib.parse import urljoin


class GitlabAPI:
  __BASE_URL = 'https://gitlab.com/api/v4/'
  __INSTANCE = None
  
  @staticmethod
  def with_token() -> bool:
    return GitlabAPI.__INSTANCE.with_token
  
  @staticmethod
  def token_is_valid() -> bool:
    return GitlabAPI.__INSTANCE.token_is_valid 
  
  @staticmethod
  def init(token: str):
    GitlabAPI.__INSTANCE = GitlabAPI(token)
  
  def __init__(self, token: str):
    self.headers = {}
    auth_headers = {'PRIVATE-TOKEN': f'{token}'}
    if self.__get('/user', headers=auth_headers) is None:
      raise ValueError('Invalid API Token')
    self.headers.update(auth_headers)
  
  @staticmethod
  def get(path: str, headers: dict = {}, params: dict = {}) -> any:
    if GitlabAPI.__INSTANCE is None:
      raise RuntimeError('Gitlab API not initialized.')
    return GitlabAPI.__INSTANCE.__get(path, headers=headers, params=params)

  @staticmethod
  def get_all(path: str, headers: dict = {}, params: dict = {}) -> any:
    data = []
    page = 1
    per_page = 100
    while True:
      _params = {
        'page': page,
        'per_page': per_page,
        **params
      }
      new_data = GitlabAPI.get(path, headers=headers, params=_params)
      if new_data is None:
        raise Exception(f'Fetch failed on {path}')
      if type(new_data) is not list:
        raise Exception(f'Fetched data type of {type(new_data).__name__}, expected list')
      data.extend(new_data)
      if len(new_data) != per_page:
        break
      page += 1
    return data
  
  def __get(self, path: str, headers: dict = {}, params: dict = {}) -> any:
    _headers = {**self.headers, **headers}
    response = requests.get(urljoin(GitlabAPI.__BASE_URL, './' + path), headers=_headers, params=params)
    if response.status_code != 200:
      return None
    return response.json()
