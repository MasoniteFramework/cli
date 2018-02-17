''' A Module Description '''
from masonite.view import view
from masonite.facades.Auth import Auth
from config import application
from config import auth
import bcrypt


class RegisterController(object):
    ''' Class Docstring Description '''

    def __init__(self):
        pass

    def show(self, request):
        ''' Show the registration page '''
        return view('auth/register', {'app': application, 'Auth': Auth(request)})

    def store(self, request):
        ''' Register a new user '''
        # register the user
        password = bcrypt.hashpw(
                bytes(request.input('password'), 'utf-8'), bcrypt.gensalt()
            )

        auth.AUTH['model'].create(
            name=request.input('name'),
            password=password,
            email=request.input('email'),
        )

        # login the user
        # redirect to the homepage
        if Auth(request).login(request.input(auth.AUTH['model'].__auth__), request.input('password')):
            return request.redirect('/home')

        return request.redirect('/register')
