import subprocess
import os
import pytest

def test_craft_install():
    subprocess.call(['touch', '.env-example'])
    subprocess.call(['craft', 'install'])
    
    assert os.path.isfile('.env')
    
    subprocess.call(['rm', '.env'])
    subprocess.call(['rm', '.env-example'])

def test_craft_new():
    subprocess.call(['craft', 'new', 'testnew'])
    assert os.path.isdir('testnew')

def test_craft_view():
    command = subprocess.Popen('cd testnew ; craft view test',stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(command)
    assert os.path.isfile('testnew/resources/templates/test.html')
    subprocess.call(['rm', 'testnew/resources/templates/test.html'])

def test_craft_controller():
    command = subprocess.Popen('cd testnew ; craft controller TestController',stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(command)
    assert os.path.isfile('testnew/app/http/controllers/TestController.py')
    subprocess.call(['rm', 'testnew/app/http/controllers/TestController.py'])

def test_craft_model():
    command = subprocess.Popen('cd testnew ; craft model TestModel',stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(command)
    assert os.path.isfile('testnew/app/TestModel.py')
    subprocess.call(['rm', 'testnew/app/TestModel.py'])

