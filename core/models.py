from .api import GitlabAPI


class User:
  
  @staticmethod
  def __resolve(username: str) -> any:
    users = GitlabAPI.get(f'/users', params={'username': username})
    if len(users) == 0 or (user := next(iter([user for user in users if user['username'] == username]), None)) is None:
      raise ValueError('User not found')
    return user
  
  def __init__(self, username: str):
    self.username = username
    self.__repositories = None
    raw = User.__resolve(self.username)
    self.id = raw['id']
  
  def repository(self, name: str) -> 'Repository':
    if type(self.__repositories) is list and (repo := next(iter([repo for repo in self.__repositories if repo.name == name]), None)) is not None:
      return repo
    repos = GitlabAPI.get_all(f'/users/{self.id}/projects', params={'search': name})
    raw_repo = next(iter([repo for repo in repos if repo['name'] == name]), None)
    if raw_repo is None:
      raise ValueError('Repository not found')
    return Repository(raw_repo, self)
  
  def repositories(self, with_fork=False, force: bool = False) -> list['Repository']:    
    if self.__repositories is None or force:
      raw_repositories = GitlabAPI.get_all(f'/users/{self.id}/projects')
      if raw_repositories is not None:
        self.__repositories = [Repository(raw, self) for raw in raw_repositories if 'forked_from_project' not in raw or with_fork]
    return self.__repositories


class Repository:  
  def __init__(self, raw: dict, owner: User):
    self.id = raw['id']
    self.name = raw['name']
    self.owner = owner
    self.__branches = None
  
  @property
  def branches(self) -> list['Branche']:
    if self.__branches is None:
      raw_branches = GitlabAPI.get_all(f'/projects/{self.id}/repository/branches')
      if raw_branches is not None:
        self.__branches = [Branche(raw, self) for raw in raw_branches]
    return self.__branches
  
  def __repr__(self):
    return f'Repository<{self.id}-{self.name}>'


class Branche:
  def __init__(self, raw: dict, repository: Repository):
    self.name = raw['name']
    self.repository = repository
    self.__commits = None
  
  @property
  def commits(self) -> list['Commit']:
    if self.__commits is None:
      raw_commits = GitlabAPI.get_all(f'/projects/{self.repository.id}/repository/commits', params={'branche': self.name})
      if raw_commits is not None:
        self.__commits = [Commit(raw, self) for raw in raw_commits]
    return self.__commits
  
  def __repr__(self):
    return f'Branche<{self.name}>'


class Commit:  
  def __init__(self, raw: dict, branche: Branche):
    self.id = raw['id']
    self.branche = branche
    self.author = Actor(raw.get('author_name', '<Deleted_User>'), raw.get('author_email', '<Deleted_User>'))
    self.committer = Actor(raw.get('committer_name', '<Deleted_User>'), raw.get('committer_email', '<Deleted_User>'))
  
  def __repr__(self):
    return f'Commit<{self.id}>'


class Actor:    
  def __init__(self, name: str, email: str):
    self.name = name
    self.email = email
    
  def __eq__(self, value):
    if isinstance(value, Actor):
      return self.name == value.name and self.email == self.email
    return False
    
  def __hash__(self):
    return hash(self.name + ':' + self.email)
  
  def __repr__(self):
    return f'Actor<{self.name} | {self.email}>'
