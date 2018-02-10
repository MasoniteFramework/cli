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

    subprocess.call(['craft', 'new', 'testnewversion', '--version', '1.2.0'])
    assert os.path.exists('testnewversion') == True

    
    subprocess.call(['craft', 'new', 'testnewmaster', '--branch', 'master'])
    assert os.path.exists('testnewmaster') == True



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
    command = subprocess.Popen('cd testnew ; craft migration test_migration --table users',stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(command)
    assert len(os.listdir('testnew/databases/migrations')) >= 2

def test_auth():
    command = subprocess.Popen('cd testnew ; craft auth',stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(command)

    ## Test auth controllers being added
    assert os.path.exists('testnew/app/http/controllers/LoginController.py') == True
    assert os.path.exists('testnew/app/http/controllers/RegisterController.py') == True
    assert os.path.exists('testnew/app/http/controllers/HomeController.py') == True

    # Test templates
    assert os.path.exists('testnew/resources/templates/auth/base.html') == True   
    assert os.path.exists('testnew/resources/templates/auth/home.html') == True   
    assert os.path.exists('testnew/resources/templates/auth/login.html') == True   
    assert os.path.exists('testnew/resources/templates/auth/nav.html') == True   
    assert os.path.exists('testnew/resources/templates/auth/register.html') == True   

def test_package():
    commandnewpackage = subprocess.Popen('cd testnew ; craft package testpackage',stdout=subprocess.PIPE, shell=True)
    command = subprocess.Popen('mkdir testpackage; cd testpackage ; craft package testpackage',stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(commandnewpackage)
    subprocess.Popen.wait(command)

    assert os.path.exists('testpackage/testpackage/integration.py') == True
    assert os.path.exists('testpackage/testpackage/__init__.py') == True
    assert os.path.exists('testpackage/setup.py') == True
    assert os.path.exists('testpackage/MANIFEST.in') == True

def test_create_service_provider():
    commandnewprovider = subprocess.Popen(
        'cd testnew ; craft provider TestServiceProvider', stdout=subprocess.PIPE, shell=True)
    subprocess.Popen.wait(commandnewprovider)

    assert os.path.exists('testnew/app/providers/TestServiceProvider.py') == True

