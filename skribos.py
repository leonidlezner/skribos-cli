import yaml
import click
from git import Repo, Git, RemoteProgress
import sys
import re
import os
import subprocess

class RecipeError(Exception):
  pass

class GitHubDownloader(object):
  def __init__(self, repo, target, branch, tag, override, use_ssh):
    self.repo = repo
    self.target = target
    self.branch = branch
    self.tag = tag
    self.override = override
    self.use_ssh = use_ssh

  def get_repo_name(self, fullname):
    # Check the fullname for the format "username/reponame"
    result = re.search("^([\w\-\.]+)/([\w\-\.]+)$", fullname)

    if not result:
      return None

    return result.group(2)
    
  def download(self):
    if self.use_ssh:
      link = 'git@github.com:/{}.git'.format(self.repo)
    else:
      link = 'https://github.com/{}.git'.format(self.repo)
    
    repo_folder = self.get_repo_name(self.repo)

    if not repo_folder:
      raise RecipeError('Bad GitHub Repository: {}'.format(self.repo))

    repo_path = "{}/{}".format(self.target, repo_folder)

    repo = None

    # Check if the folder exists. If it does, do git pull and
    # update the repository. If not, clone the repository
    if os.path.isdir(repo_path):
      print('🔄 Updating "{}"'.format(repo_path))

      repo = Repo(repo_path)

      # If there are some local changes in the repo display the warning
      if repo.is_dirty():
        print('🚧 Repo has local changes!')

        if not self.override:
          raise RecipeError('Can\'t update Repo because of local changes!')

      origin = repo.remotes.origin

      branch = None

      # Check if the repository has an active branch.
      # If a tag is checked out, there is not active branch and
      # pulling will not work.
      try:
        branch = repo.active_branch
      except TypeError:
        branch = None

      if branch:
        origin.pull()
      else:
        origin.fetch()
    else:
      print('🚚 Cloning "{}" to "{}"'.format(link, repo_path))
      repo = Repo.clone_from(link, repo_path)

    if repo:
      if self.tag:
        # Checkout the tag and override any local changes
        # if the option is set
        print('🏷 Tag: {}'.format(self.tag))
        repo.git.checkout(self.tag, force=self.override)
      else:
        # Checkout the branch and override any local changes
        # if the option is set
        print('🌳 Branch: {}'.format(self.branch))
        repo.git.checkout(self.branch, force=self.override)


class Download(object):
  def check_to(self, dict_entry):
    to = ""
    
    if 'to' in dict_entry:
      if dict_entry['to']:
        to = dict_entry['to'].strip()
    
    if not to:
      raise RecipeError('Target (to:) not found in download: {}!'.format(dict_entry))
    
  def __init__(self, dict_entry):
      self.downloader = None
      
      if 'github' in dict_entry:
        repo = dict_entry['github']
        self.check_to(dict_entry)
        target = dict_entry['to']
        branch = dict_entry.get('branch', 'master')
        tag = dict_entry.get('tag', None)
        override = dict_entry.get('override', False)
        use_ssh = dict_entry.get('ssh', False)
        self.downloader = GitHubDownloader(repo, target, branch, tag, override, use_ssh)
    
  def process(self):
    self.downloader.download()

class Job(object):
  def __init__(self, job_dict, file_list, build_vars):
    self.job_dict = job_dict

    if 'name' not in job_dict:
      raise RecipeError('Job without name: {}'.format(job_dict))

    if 'command' not in job_dict:
      raise RecipeError('Job without command: {}'.format(job_dict))    

    self.vars = build_vars
    self.file_list = file_list

  def replace_placeholders(self, command):
    for key, value in self.vars.items():
      command = command.replace('${}'.format(key), value)
    
    command = command.replace('$files', self.file_list)
    
    return command

  def process(self):
    print('🌀 Processing Job: {}'.format(self.job_dict['name']))
    command = self.replace_placeholders(self.job_dict['command'])
    subprocess.check_output(command, shell=True)


class Builder(object):
  def __init__(self, build_dict, file_list, override_vars):
    self.files = file_list

    build_vars = build_dict.get('vars', {})
    
    # Merge variables provided over CLI
    build_vars.update(override_vars)

    if 'jobs' not in build_dict or not isinstance(build_dict['jobs'], list):
      raise RecipeError('No jobs (jobs:) found!')

    self.jobs = list(map(lambda j: Job(j, file_list, build_vars), build_dict['jobs']))

  def process(self):
    for job in self.jobs:
      job.process()

class Skribos(object):
  def __init__(self):
    self.downloads = None
    self.chapters = None
    self.builder = None
  
  def load(self, filename, override_vars):
    if not os.path.isfile(filename):
      raise RecipeError('Recipe file not found: {}'.format(filename))

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
            raise RecipeError('Chapters not found in recipe!')

        self.chapters = chapters

        if 'build' in recipe:
          build = recipe['build']
          builder = Builder(build, self.get_filelist_as_line(), override_vars)
          self.builder = builder
        else:
          raise RecipeError('Build information not found in recipe!')
  
  def download_all(self):
    for download in self.downloads:
      download.process()
    
  def get_filelist_as_line(self):
    return " ".join(map(lambda c: '"{}"'.format(c), self.chapters))

  def check_chapters(self):
    for chapter in self.chapters:
      if not os.path.isfile(chapter):
        raise RecipeError('File "{}" not found!'.format(chapter))

  def build(self):
    self.builder.process()

@click.command()
@click.option('--recipe', help='Yaml file with skribos recipe', required=True)
@click.option('--output', help='Output directory variable for the recipe', default=None)
@click.option('--nodownload', is_flag=True, help='Skip downloading, just build the recipes')
def main(recipe, nodownload, output):
  skribos = Skribos()

  vars_from_cli = {}
  
  if output:
    vars_from_cli['output'] = output
  
  print('📃 Read skribos recipe "{}"'.format(recipe))
  skribos.load(recipe, override_vars=vars_from_cli)
  
  if not nodownload:
    print('📦 Downloading resources...')
    skribos.download_all()
    print('✅ Downloads finished!')

  skribos.check_chapters()

  skribos.build()

  print('✅ Skribos is done!')

if __name__ == '__main__':
  try:
    main()
  except RecipeError as error:
    print('❌ Skribos Error! {}'.format(error))  
  
