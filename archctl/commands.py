from abc import ABC, abstractmethod
from archctl.main import Archctl
import archctl.interactive as it
from archctl.validation import InteractiveValidation


class Command(ABC):

    @abstractmethod
    def run(self):
        """Returns a list of the """


class Register(Command):

    def __init__(self):
        self.validator = InteractiveValidation()

    def run(self):
        answers = it.RegisterQuestions().interactive()
        self.validator.confirm_command_execution(answers)
        Archctl().register(answers['repo'], answers['kind'])


class List(Command):

    def run(self):
        Archctl().list()


class Delete(Command):

    def __init__(self):
        self.validator = InteractiveValidation()

    def run(self):
        answers = it.DeleteQuestions().interactive()
        self.validator.confirm_command_execution(answers)
        Archctl().delete(answers['repo'])


class Create(Command):

    def __init__(self):
        self.validator = InteractiveValidation()

    def run(self):
        Archctl().create()
