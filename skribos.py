import yaml
import click
from git import Repo, Git, RemoteProgress
import sys
import re
import os


class GitHubDownloader(object):
  def __init__(self, repo, target, branch, tag):
    self.repo = repo
    self.target = target
    self.branch = branch
    self.tag = tag

  def get_repo_name(self, fullname):
    # Check the fullname for the format "username/reponame"
    result = re.search("^([\w\-\.]+)/([\w\-\.]+)$", fullname)

    if not result:
      return None

    return result.group(2)
    
  def download(self):
    link = 'https://github.com/{}.git'.format(self.repo)
    
    repo_folder = self.get_repo_name(self.repo)

    if not repo_folder:
      raise Exception('Bad GitHub Repository: {}'.format(self.repo))

    repo_path = "{}/{}".format(self.target, repo_folder)

    # Check if the folder exists. If it does, do git pull and
    # update the repository. If not, clone the repository
    if os.path.isdir(repo_path):
      print('  🔄 Updating "{}"'.format(repo_path))
      repo = Repo(repo_path)
      origin = repo.remotes.origin
      origin.pull()
    else:
      print('  🚚 Cloning "{}" to "{}"'.format(link, repo_path))
      Repo.clone_from(link, repo_path)


class Download(object):
  def check_to(self, dict_entry):
    to = ""
    
    if 'to' in dict_entry:
      if dict_entry['to']:
        to = dict_entry['to'].strip()
    
    if not to:
      raise Exception('Target (to:) not found in download: {}!'.format(dict_entry))
    
  def __init__(self, dict_entry):
      self.downloader = None
      
      if 'github' in dict_entry:
        repo = dict_entry['github']
        self.check_to(dict_entry)
        target = dict_entry['to']
        branch = dict_entry.get('branch', None)
        tag = dict_entry.get('tag', None)
        self.downloader = GitHubDownloader(repo, target, branch, tag)
    
  def process(self):
    self.downloader.download()

class Skribos(object):
  def __init__(self):
    self.downloads = None
    self.chapters = None
  
  def load(self, filename):
    with open(filename) as file:
        recipe = yaml.load(file, Loader=yaml.Loader)
        
        # Check if 'downloads' are available
        # Don't skip if not found
        if 'downloads' in recipe:
            if isinstance(recipe['downloads'], list):
                downloads = list(map(lambda d: Download(d), recipe['downloads']))
            else:
                downloads = None
        else:
            downloads = None
            
        self.downloads = downloads
        
        # Check if 'chapters' are available
        # and raise an error if not
        if 'chapters' in recipe:
            if isinstance(recipe['chapters'], list):
                chapters = recipe['chapters']
            else:
                chapters = None
        else:
            raise Exception('Chapters not found in recipe!')
  
  def download_all(self):
    for download in self.downloads:
      download.process()
    
  def get_filelist(self):
    pass



@click.command()
@click.option('--recipe', prompt='Skribos Recipe', help='Yaml file with skribos recipe')
def main(recipe):
  skribos = Skribos()

  print('📃 Read recipe "{}"'.format(recipe))
  skribos.load(recipe)
  
  print('📦 Downloading resources...')
  skribos.download_all()
  print('✅ Downloads finished!')

if __name__ == '__main__':
  main()
  
