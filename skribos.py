import yaml
import click
from git import Repo, Git, RemoteProgress
import sys

class GitHubDownloader(object):
  def __init__(self, repo, target, branch, tag):
    self.repo = repo
    self.target = target
    self.branch = branch
    self.tag = tag
    
  def download(self):
    link = 'https://github.com/{}.git'.format(self.repo)
    
    # get the folder name of the repo
    # check if repo is a git folder
    # pull if git
    # clone if not found
    
    repo = Repo(self.target)
    

    print('🔄 Updating "{}"'.format(self.target))    
    origin = repo.remotes.origin
    origin.pull()
    
    print('📦 Cloning "{}" to "{}"'.format(link, self.target))
    
    
#    with tqdm(total=100) as pbar:
    #Repo.clone_from(link, self.target)
    


class Download(object):
  def check_to(self, dict_entry):
    to = ""
    
    if 'to' in dict_entry:
      if dict_entry['to']:
        to = dict_entry['to'].strip()
    
    if not to:
      raise Exception('Target (to:) not found in download: {}!'.format(dict_entry))
    
  def __init__(self, dict_entry):
      print(dict_entry)
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
  skribos.load(recipe)
  skribos.download_all()

if __name__ == '__main__':
  main()
  
