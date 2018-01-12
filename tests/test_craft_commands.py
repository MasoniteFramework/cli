import subprocess
import os
import pytest

def test_craft_install():
    subprocess.call(['touch', '.env-example'])
    subprocess.call(['craft', 'install'])
    
    assert os.path.exists('.env') == True
    
    subprocess.call(['rm', '.env'])
    subprocess.call(['rm', '.env-example'])

def test_craft_new():
    subprocess.call(['craft', 'new', 'testnew'])
    assert os.path.exists('testnew') == True

def test_craft_view():
    command = subprocess.Popen('cd testnew ; craft view test',stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(command)
    assert os.path.exists('testnew/resources/templates/test.html') == True
    subprocess.call(['rm', 'testnew/resources/templates/test.html'])

def test_craft_controller():
    command = subprocess.Popen('cd testnew ; craft controller TestController',stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(command)
    assert os.path.exists('testnew/app/http/controllers/TestController.py') == True
    subprocess.call(['rm', 'testnew/app/http/controllers/TestController.py'])

def test_craft_model():
    command = subprocess.Popen('cd testnew ; craft model TestModel',stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(command)
    assert os.path.exists('testnew/app/TestModel.py') == True
    subprocess.call(['rm', 'testnew/app/TestModel.py'])

def test_craft_migration():
    print(os.listdir('testnew/databases/migrations'))
    command = subprocess.Popen('cd testnew ; craft migration test_migration --table users',stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(command)
    assert len(os.listdir('testnew/databases/migrations')) > 2


