import click
import shutil
import sys
import importlib
import os
from subprocess import call
import zipfile
import subprocess


''' Append the projects directory to the sys path 
    This is used so project modules are importable like the config module
'''
sys.path.append(os.getcwd())

@click.command()
@click.argument('command')
@click.argument('submodule', default=False)
@click.argument('function', default=False)
def cli(command, submodule, function):
    ''' Masonite Command Line Helper Tool '''
    found = False

    try:
        from config import application
        from config import packages
        # Add additional site packages to vendor if they exist
        for directory in packages.SITE_PACKAGES:
            path = os.path.join(os.getcwd(), directory)
            sys.path.append(path)
    except ModuleNotFoundError:
        raise Exception('\033[95mThis command must be ran inside your project root directory.\033[0m')

    for key, provider in enumerate(application.PROVIDERS):
        if hasattr(importlib.import_module(provider), command):
            click.echo('\033[92mExecuting Command ...\033[0m')
            getattr(importlib.import_module(provider), command)()
            found = True
            break

    # run through third party commands
    if not found:
        try:
            if function:
                module = importlib.import_module(
                    command + ".commands." + submodule)
                command = getattr(module, function)
            elif submodule:
                module = importlib.import_module(
                    command + ".commands." + submodule)
                command = getattr(module, submodule)
            else:
                module = importlib.import_module(
                    command + ".commands." + command)
                command = getattr(module, command)

            command()
            found = True
        except Exception as e:
            click.echo(e)
    
    if not found:
        click.echo('\033[95mCommand not found.\033[0m')

@click.group()
def group():
    pass

@group.command()
def install():
    ''' Installs all dependency requirements.
        This command is analogous to pip3 install -r requirements.txt
    '''
    call(["pip3", "install", "-r", "requirements.txt"])

    # create the .env file if it does not exist
    if not os.path.isfile('.env'):
        shutil.copy('.env-example', '.env')

@group.command()
@click.option('--port', default='8000', help='Change the port to run on')
@click.option('--host', default='127.0.0.1', help='Change the IP address to run on')
def serve(port, host):
    ''' Runs the application. '''
    call(["waitress-serve", '--port', port, "--host", host, "wsgi:application"])

@group.command()
@click.argument('viewname')
def view(viewname):
    ''' Creates a view '''
    if os.path.isfile('resources/templates/' + viewname + '.html'):
        click.echo('\033[95m' + viewname + ' View Exists!' + '\033[0m')
    else:
        open('resources/templates/' + viewname + '.html', 'w+')
        click.echo('\033[92m' + viewname +
              ' View Created Successfully!' + '\033[0m')

@group.command()
@click.argument('controller')
def controller(controller):
    ''' Creates a controller '''
    if os.path.isfile('app/http/controllers/' + controller + '.py'):
        click.echo('\033[95m' + controller + ' Controller Exists!' + '\033[0m')
    else:
        f = open('app/http/controllers/' + controller + '.py', 'w+')
        f.write("''' A Module Description '''\n")
        f.write('from masonite.view import view\n\n')
        f.write('class ' + controller + '(object):\n')
        f.write("    ''' Class Docstring Description '''\n\n")
        f.write('    def __init__(self):\n')
        f.write('        pass\n')

        click.echo('\033[92m' + controller + ' Created Successfully!' + '\033[0m')

@group.command()
@click.argument('model')
def model(model):
    ''' Creates a model '''

    if not os.path.isfile('app/' + model + '.py'):
        if not os.path.exists(os.path.dirname('app/' + model + '.py')):
            # Create the path to the model if it does not exist
            os.makedirs(os.path.dirname('app/' + model + '.py'))

        f = open('app/' + model + '.py', 'w+')

        f.write("''' A " + model + " Database Model '''\n")
        f.write('from orator import DatabaseManager, Model\n')
        f.write('from config.database import Model\n\n')
        f.write("class "+model+"(Model):\n    pass\n")

        click.echo('\033[92mModel Created Successfully!\033[0m')
    else:
        click.echo('\033[95mModel Already Exists!\033[0m')

@group.command()
def migrate():
    ''' Migrates all migrations into the database '''
    subprocess.call(['orator', 'migrate', '-c', 'config/database.py', '-p', 'databases/migrations', '-f'])

@group.command(name="migrate:rollback")
def migrationrollback():
    ''' Undo all migrations '''
    subprocess.call(['orator', 'migrate:rollback', '-c',
                      'config/database.py', '-p', 'databases/migrations', '-f'])

@group.command(name="migrate:reset")
def migrationreset():
    ''' Rolls back lastest migration operation '''
    subprocess.call(['orator', 'migrate:reset', '-c',
                      'config/database.py', '-p', 'databases/migrations', '-f'])

@group.command(name="migrate:refresh")
def migrationrefresh():
    ''' Rolls back migrations and remigrates '''
    subprocess.call(['orator', 'migrate:refresh', '-c',
                      'config/database.py', '-p', 'databases/migrations', '-f'])



@group.command(name="migration")
@click.argument('migrationname')
@click.option('--table', default=False)
@click.option('--create', default=False)
def makemigration(migrationname, table, create):
    ''' Creates a migration file '''

    if create:
        subprocess.call(['orator', 'make:migration', migrationname,
                         '-p', 'databases/migrations', '--table', create, '--create'])
    elif table:
        subprocess.call(['orator', 'make:migration', migrationname,
                         '-p', 'databases/migrations', '--table', table])
    else:
        subprocess.call(['orator', 'make:migration', migrationname,
                         '-p', 'databases/migrations'])

@group.command()
@click.option('--local', default=False, is_flag=True, help='Deploys the local master branch')
@click.option('--current', default=False, is_flag=True, help='Deploys the current branch')
def deploy(local, current):
    ''' Deploys your application's origin/master branch. 
        Deploying your command with no flags will deploy the origin master branch. 
        See flag options for deploying other branches
    '''
    from config import application
    output = subprocess.Popen(
        ['heroku', 'git:remote', '-a', application.NAME.lower()], stdout=subprocess.PIPE).communicate()[0]
    if not output:

        # Python 2.7 support
        try:
            input = raw_input
        except NameError:
            pass

        create_app = input(
            "\n\033[92mApp doesn't exist for this account. Would you like to craft one?\033[0m \n\n[y/n] > ")  # Python 2
        if 'y' in create_app:
            subprocess.call(['heroku', 'create', application.NAME.lower()])
            if local:
                subprocess.call(['craft', 'deploy', '--local'])
            elif current:
                subprocess.call(['craft', 'deploy', '--current'])
            else:
                subprocess.call(['craft', 'deploy'])
    else:
        if local:
            subprocess.call(['git', 'push', 'heroku', 'master:master'])
        elif current:
            subprocess.call(['git', 'push', 'heroku', 'HEAD:master'])
        else:
            subprocess.call(['git', 'push', 'heroku', 'master'])

@group.command()
def auth():
    ''' Scaffolds an authentication system. 
        This command will create multiple authentication controllers, routes, and views.
    '''
    click.echo('\n\033[92mScaffolding Application ...\033[0m\n')
    module_path = os.path.dirname(os.path.realpath(__file__))
    
    f = open('routes/web.py', 'a')
    # add all the routes
    f.write('\nROUTES = ROUTES + [\n    ')
    f.write("Get().route('/login', 'LoginController@show'),\n    ")
    f.write("Get().route('/logout', 'LoginController@logout'),\n    ")
    f.write("Post().route('/login', 'LoginController@store'),\n    ")
    f.write("Get().route('/register', 'RegisterController@show'),\n    ")
    f.write("Post().route('/register', 'RegisterController@store'),\n    ")
    f.write("Get().route('/home', 'HomeController@show'),\n")
    f.write(']\n')

    # move controllers
    shutil.copyfile(module_path+"/snippets/auth/controllers/LoginController.py",
                    os.getcwd()+"/app/http/controllers/LoginController.py")
    shutil.copyfile(module_path+"/snippets/auth/controllers/RegisterController.py",
                    os.getcwd()+"/app/http/controllers/RegisterController.py")
    shutil.copyfile(module_path+"/snippets/auth/controllers/HomeController.py",
                    os.getcwd()+"/app/http/controllers/HomeController.py")

    # move templates
    shutil.copytree(module_path + "/snippets/auth/templates/auth",
                    os.getcwd()+"/resources/templates/auth")
    
    click.echo('\n\033[92mProject Scaffolded. You now have 4 new controllers, 5 new templates and 6 new routes\033[0m\n')

@group.command()
@click.argument('project')
def new(project):
    ''' Creates a new project '''
    if not os.path.isdir(os.getcwd() + '/' + project):
        click.echo('\033[92mCrafting Application ...\033[0m')

        success = False
        from io import BytesIO
        zipurl = 'http://github.com/josephmancuso/masonite-starter/archive/master.zip'

        try:
            # Python 3
            from urllib.request import urlopen
            
            with urlopen(zipurl) as zipresp:
                with zipfile.ZipFile(BytesIO(zipresp.read())) as zfile:
                    zfile.extractall(os.getcwd())
            
            success = True
        except:
            # Python 2
            import urllib
            r = urllib.urlopen(zipurl)
            with zipfile.ZipFile(BytesIO(r.read())) as z:
                z.extractall(os.getcwd())
            
            success = True

        # rename file

        if success:
            os.rename(os.getcwd() + '/masonite-starter-master', os.getcwd() + '/' +project)
            click.echo('\033[92m\nApplication Created Successfully!\n\nNow just cd into your project and run\n\n    $ craft install\n\nto install the project dependencies.\n\nCreate Something Amazing!\033[0m')
        else:
            click.echo('\033[91mCould Not Create Application :(\033[0m')
    else:
        click.echo('\033[91mDirectory {0} already exists. Please choose another project name\033[0m'.format("'"+project+"'"))

@group.command()
@click.argument('package_name')
def publish(package_name):
    ''' Used to run integrations on packages.
        Can be used to seamlessly integrate config files into your project.
    '''
    from config import packages

    # Add additional site packages to vendor if they exist
    for directory in packages.SITE_PACKAGES:
        path = os.path.join(os.getcwd(), directory)
        sys.path.append(path)

    imported_package = importlib.import_module(package_name+'.integration')

    imported_package.boot()

@group.command()
@click.argument('package_name')
def package(package_name):
    ''' Scaffold a new Masonite package.
        This will scaffold the bare bones of a PyPi project
        and create the integrations module as well as boot function
    '''
    ## create setup.py
    setup = open(os.path.join(os.getcwd(), 'setup.py'), 'w+')
    setup.write("from setuptools import setup\n\n")
    setup.write('setup(\n    ')
    setup.write('name="{0}",\n    '.format(package_name))
    setup.write("version='0.0.1',\n    ")
    setup.write("packages=['{0}'],\n    ".format(package_name))
    setup.write("install_requires=[\n        ".format(package_name))
    setup.write("'masonite',\n    ".format(package_name))
    setup.write("],\n    ".format(package_name))
    setup.write('include_package_data=True,\n')
    setup.write(')\n')
    setup.close()

    manifest = open(os.path.join(os.getcwd(), 'MANIFEST.in'), 'w+')
    manifest.close()

    if not os.path.exists(package_name):
        os.makedirs(package_name)

    init_file = open(os.path.join(os.getcwd(), '{0}/{1}'.format(package_name, '__init__.py')), 'w+')
    init_file.close()

    integration_file = open(os.path.join(os.getcwd(), '{0}/{1}'.format(package_name, 'integration.py')), 'w+')

    integration_file.write('from masonite.packages import create_or_append_config\n')
    integration_file.write('import os\n\n')
    integration_file.write('package_directory = os.path.dirname(os.path.realpath(__file__))\n\n')
    integration_file.write('def boot():\n    pass')
    integration_file.close()
    click.echo('\033[92mPackage Created Successfully!\033[0m')


@group.command()
def key():
    ''' Generates a random secret key.
        You can use secret keys to encrypt and decrypt anything.
        Keep this secret!
    '''
    from cryptography.fernet import Fernet

    click.echo("\033[92mKEY: {0}\033[0m".format(
        bytes(Fernet.generate_key()).decode('utf-8')))


@group.command()
@click.argument('provider')
def provider(provider):
    ''' Creates a Service Provider'''

    if not os.path.isfile('app/providers/' + provider + '.py'):
        if not os.path.exists(os.path.dirname('app/providers/' + provider + '.py')):
            # Create the path to the model if it does not exist
            os.makedirs(os.path.dirname('app/providers/' + provider + '.py'))

        f = open('app/providers/' + provider + '.py', 'w+')

        f.write("''' A " + provider + " Service Provider '''\n")
        f.write('from masonite.provider import ServiceProvider\n\n')
        f.write("class "+provider+"(ServiceProvider):\n\n    ")
        f.write("def register(self):\n        pass\n\n    ")
        f.write("def boot(self):\n        pass\n")

        click.echo('\033[92mService Provider Created Successfully!\033[0m')
    else:
        click.echo('\033[95mService Provider Already Exists!\033[0m')
