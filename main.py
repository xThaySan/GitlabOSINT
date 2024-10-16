from colorama import Fore
from rich.console import Console
import click
from core.api import GitlabAPI
from core.models import User, Actor
from core.utils import colorize, is_username, is_repo

console = Console(highlight=False)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument('to_explore')
@click.option('-t', '--token', prompt='Token', hide_input=True, prompt_required=True, help='Token of Gitlab API')
@click.option('-f', '--fork', is_flag=True, show_default=True, default=False, help='Enable exploration for forked repositories')
def explore(to_explore: str, token: str, fork: bool) -> None:
  """Retrieves usernames and e-mails from repository main branch logs.

  TO_EXPLORE: Can be either the username (all public repositories are used) or the name of a specific repository
  """
  
  try:
    GitlabAPI.init(token=token)
  except:
    console.print(colorize('/!\\ Token is not valid', Fore.RED))
    exit()
  
  actors: set[Actor] = set()
  with console.status('Exploring repositories...', spinner="moon") as status:
    username, repository = None, None
    if is_username(to_explore):
      username = to_explore
    elif is_repo(to_explore):
      username, repository = to_explore.split('/')
    else:
      console.print(f'❌ {colorize("TO_EXPLORE must have the pattern", Fore.WHITE)} {colorize("<username>", Fore.RED)} or {colorize("<username>/<repository>", Fore.RED)}')
      exit()
    
    try:
      user = User(username)
    except Exception as e:
      console.print(f'❌ {colorize("User", Fore.WHITE)} {colorize(to_explore, Fore.RED)} {colorize("does not exist", Fore.WHITE)}')
      exit()
    

    if repository:
      try:
        repositories = [user.repository(repository)]
      except Exception as e:
        print(e.with_traceback())
        console.print(f'❌ {colorize("Repository", Fore.WHITE)} {colorize(to_explore, Fore.RED)} {colorize("not found", Fore.WHITE)}')
        exit()
    else:
      repositories = user.repositories(with_fork=fork)
    
    repos_count = len(repositories)    
    console.print(f'✨ {colorize("Found", Fore.WHITE)} {colorize(str(repos_count), Fore.YELLOW)} {colorize("exploitable repositor" + ('ies' if repos_count > 1 else 'y'), Fore.WHITE)}')
    for i, repo in enumerate(repositories):
      for branche in repo.branches:
        status.update(f'({i+1}/{repos_count}) Exploring {repo.name} <{branche.name}>')
        for commit in branche.commits:
          actors.add(commit.author)
          actors.add(commit.committer)
  
  if len(actors) == 0:
    console.print(f'👀 {colorize("No relevant information found...", Fore.WHITE)}')
    exit()
  
  actors = sorted([actor for actor in actors if actor != user], key=lambda actor: (actor.name.lower(), actor.name))  
  for actor in actors:
    console.print('🪪 ' + colorize(actor.name, Fore.WHITE) + ' ' + colorize(actor.email, Fore.CYAN))
  

if __name__ == '__main__':
  explore()
