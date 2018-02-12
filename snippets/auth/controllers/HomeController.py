''' A Module Description '''
from config import application
from masonite.facades.Auth import Auth

class HomeController(object):
    ''' Class Docstring Description '''

    def __init__(self):
        pass

    def show(self, Request):
        if not Auth(Request).user():
            Request.redirect('/login')
        return view('auth/home', {'app': application, 'Auth': Auth(Request)})
