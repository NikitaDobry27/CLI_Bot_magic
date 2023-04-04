
import re
from collections import UserDict
import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value=None):
        if value:
            value = self.validate_phone(value)
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value:
            new_value = self.validate_phone(new_value)
        self._value = new_value

    def validate_phone(self, value):
        phone_pattern = re.compile(r'^\+?[\d\s\-()]{9,15}$')
        if not phone_pattern.match(value):
            raise ValueError("Invalid phone number format")
        return value

class Birthday(Field):
    def __init__(self, value=None):
        if value:
            value = self.validate_birthday(value)
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value:
            new_value = self.validate_birthday(new_value)
        self._value = new_value

    def validate_birthday(self, value):
        try:
            value = datetime.strptime(value, '%d.%m.%Y').date()
            return value
        except ValueError:
            raise ValueError("Invalid date format. Please use 'dd.mm.yyyy'")

class Record:
    def __init__(self, name, phones=None, birthday=None):
        self.name = Name(name)
        self.phones = []
        if birthday:
            self.birthday = Birthday(birthday)
        else:
            self.birthday = None
        if phones:
            for phone in phones:
                self.add_phone(phone)

    def add_phone(self, phone):
        self.phones.append(phone)
        
    def clear_phones(self):
        self.phones.clear()

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.date.today()
        birthday_date = self.birthday.value.day
        birthday_month = self.birthday.value.month
        new_birthday = datetime.date(today.year, birthday_month, birthday_date)
        
        if new_birthday < today:
            new_birthday = datetime.date(today.year + 1, birthday_month, birthday_date)

        time_to_birthday = new_birthday - today
        return time_to_birthday.days

    def __str__(self) -> str:
        phones_str = ', '.join([str(phone) for phone in self.phones])
        return f"{self.name}: {phones_str}"
                

class AddressBook(UserDict):
        
    def add_record(self, record):
        self.data[record.name.value] = record
        
        
    def find_records(self, query):
        result = []
        for name, record in self.data.items():
            if str(query).lower() in str(name).lower():
                result.append(record)
        return result


contacts = AddressBook()

def input_validation(func):
    def wrapper(*args):
        try:
            return func(*args)
        except IndexError:
            return '\nPlease provide name and phone number\n'
        except KeyError:
            return f'\nThere is no contact with such name\n'
        except ValueError:
            return '\nOnly name is required\n'
    return wrapper


def input_formatter(str):
    words_from_string = re.findall(r'\b\w+\b', str)
    command = words_from_string[0]

    if len(words_from_string) == 1:
        return command, ''
    data = words_from_string[1:]
    return command, data

def command_handler(command):
    for func, word in COMMANDS.items():
        if command in word:
            return func
    return unknown_command


def unknown_command(*args):
    return "\nThis command doesn't exist. Please try again\n"

@input_validation
def hello(*args):
    return '\nHi! How can I help you\n'

@input_validation
def add_contact(*args):
    lst = args[0]
    name = lst[0]
    phone = lst[1]
    birthday = '.'.join(lst[2:])

    if len(lst) < 2:
        raise IndexError
    if len(phone) > 15 or len(phone) < 9:
        return f'\n{phone} is not valid phone number\n'
    name_obj = Name(name)
    birthday_obj = Birthday(birthday)
    record_birth = Record(birthday_obj)
    record_name = Record(name_obj)
    record_name.add_phone(Phone(phone))
    contacts.add_record(record_name)
   
    return f'\nContact {name.capitalize()} was successfully added\n'


@input_validation
def change(*args):
    lst = args[0]
    name = lst[0]
    phone = lst[1]

    if len(lst) < 2:
        raise IndexError
    if len(phone) > 15 or len(phone) < 9:
        return f'\n{phone} is not valid phone number\n'

    records = contacts.find_records(name)

    if records:
        for record in records:
            record.clear_phones()
            record.add_phone(Phone(phone))

        return f'\nPhone number for contact {name.capitalize()} was successfully changed\n'
    else:
        raise KeyError



@input_validation
def phone(*args):
    lst = args[0]
    if not lst:
        raise IndexError
    if len(lst) > 1:
        raise ValueError
    name = lst[0]

    records = contacts.find_records(name)
    if not records:
        raise KeyError
    
    result = ''
    for record in records:
        phones = record.phones
        result += f'\nPhone number(s) for contact {str(record.name.value).capitalize()}: '
        for phone in phones:
            result += f'{phone}\n'
    return result


@input_validation
def remove_contact(*args):
    lst = args[0]
    
    if not lst:
        return '\nPlease provide "remove" and contact name\n' 

    if len(lst) > 1:
        raise ValueError
    name = lst[0]

    records = contacts.find_records(name)

    if records:
        for record in records:
            contacts.data.pop(record.name.value)
    else:
        raise KeyError
    return f'\nContact {str(name).capitalize()} was successfully removed\n'

def show_all(*args):
    if not contacts:
        return '\nYour contacts list is empty\n'
    result = ''
    for record in contacts.values():
        name = str(record.name.value).capitalize()
        phones = ', '.join(str(phone) for phone in record.phones)
        result += f'\n{name}: {phones}\n'
    return result


COMMANDS = {
    hello: ['hi', 'hello', 'hey'],
    add_contact: ['add'],
    change: ['change'],
    phone: ['phone'],
    show_all: ['show'],
    remove_contact: ['remove', 'delete']
}


def main():
    print(hello())
    while True:
        
        user_input = input('Type your query >>> ').lower()
            
        if user_input in ['close', '.', 'bye', 'exit']:
            print('\nSee you!')
            break
        
        try:
            command, data = input_formatter(user_input)
        except IndexError:
            print('\nPlease provide command and data\n')
            continue
            
        call = command_handler(command)

        print(call(data))


if __name__ == "__main__":
    main()