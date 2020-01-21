import pytest
import subprocess

def exec_cli(args):
  cli = ['python', 'skribos.py']
  cli.extend(args)
  out = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  return out.communicate()
  

def test_mytest():
  #stdout, stderr = exec_cli(['--recipe', 'blabla.yml'])
  
  stdout, stderr = exec_cli(['--help'])

  print("Error: ", stderr, " Stdout:", stdout)

