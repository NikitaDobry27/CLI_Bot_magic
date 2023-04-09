
import re
from collections import UserDict
import datetime
from itertools import islice
from sys import maxsize
import json


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
        phone_pattern = re.compile(r'^\+?[\d\s()]{9,15}$')
        if not phone_pattern.match(value):
            raise ValueError("Invalid phone number format")
        return value

class Birthday(Field):
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if value is None:
            self._value = value
        else:
            self._value = self.date_validation(value)

    def date_validation(self, bday):
        
        date_types = ["%d.%m.%Y", '%d.%m']
        for date_type in date_types:
            try:
                self._value = datetime.datetime.strptime(str(bday), date_type).date()
                return self._value
            except ValueError:
                pass
        raise TypeError(f"{bday}Incorrect date format, should be dd.mm.yyyy or dd.mm")

    def __str__(self):
        if self._value.year == 1900:
            return self._value.strftime("%d.%m")
        else:
            return self._value.strftime("%d.%m.%Y")
        
class Record:
    def __init__(self, name, phones=None, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        if birthday:
            self.birthday = Birthday(birthday)
        else:
            self.birthday = None
        if phones:
            for phone in phones:
                self.add_phone(phone)

    def has_phone(self, phone):
        for existing_phone in self.phones:
            if existing_phone.value == phone.value:
                return True
        return False

    def add_phone(self, phone):
        if not self.has_phone(phone):
            self.phones.append(phone)
            contacts.save_to_file("contacts.json")
        else:
            print("Phone number is already added for this contact.")
        
    def clear_phones(self):
        self.phones.clear()
    
    def days_to_birthday(self):
        if not self.birthday:
            return f"No birthday added to contact {self.name.value}"
        today = datetime.datetime.now().date()
        birthday_date = datetime.date(today.year, self.birthday.value.month, self.birthday.value.day)
        days_to_birt = (birthday_date - today).days
        if days_to_birt < 0:
            birthday_date = datetime.date(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            days_to_birt = (birthday_date - today).days
        if days_to_birt == 0:
            return f"Sing for {self.name.value} a song, cuz' {self.name.value}'s b-day is today! "
        return days_to_birt


    def __str__(self) -> str:
        phones_str = ', '.join([str(phone) for phone in self.phones])
        if self.birthday:
            return f"{self.name}: {phones_str}: {self.birthday}"
        return f"{self.name}: {phones_str}"
                

class AddressBook(UserDict):

    def save_to_file(self, file_name):
        data_to_save = {
            name: {
                'name': record.name.value,
                'phones': [phone.value for phone in record.phones],
                'birthday': record.birthday.value.strftime('%d.%m.%Y') if record.birthday else None
            } for name, record in self.data.items()
        }

        with open(file_name, 'w') as file:
            json.dump(data_to_save, file)

    def load_from_file(self, file_name):
        try:
            with open(file_name, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print(f"File {file_name} not found. Creating a new file.")
            with open(file_name, 'w') as file:
                json.dump({}, file)
            data = {}

        for name, record_data in data.items():
            record = Record(
                name=record_data['name'],
                phones=[Phone(phone) for phone in record_data['phones']],
                birthday=record_data['birthday']
            )
            self.data[name] = record

    def __iter__(self, num_records=None):
        iterator = iter(self.data.values())
        while True:
            page = list(islice(iterator, num_records or maxsize))
            if not page:
                break
            yield page

    def add_record(self, record):
        self.data[record.name.value] = record
        self.save_to_file("contacts.json")
        
    def find_records(self, query):
        result = []
        for name, record in self.data.items():
            if str(query).lower() in str(name).lower():
                result.append(record)
        return result


contacts = AddressBook()

def input_validation(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return '\nPlease provide name and phone number\n'
        except KeyError:
            return f'\nThere is no contact with such name\n'
        except ValueError:
            return '\nOnly name is required\n'
    return wrapper


def input_formatter(input_str):
    words_from_string = input_str.split()
    command = words_from_string[0]

    if len(words_from_string) == 1:
        return command, ()
    
    data = tuple(words_from_string[1:])
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

    if len(lst) < 2:
        raise IndexError

    phone_obj = Phone(lst[1])

    if len(lst) == 3:
        birthday = Birthday(lst[2])
    else:
        birthday = None

    existing_records = contacts.find_records(name)
    if existing_records:
        for record in existing_records:
            if not record.has_phone(phone_obj):
                record.add_phone(phone_obj)
                return f'\nNew phone number was added to contact {name.capitalize()}\n'
            else:
                return f'\nThe phone number is already added to contact {name.capitalize()}\n'

    record = Record(name, phones=[phone_obj], birthday=birthday)
    contacts.add_record(record)
   
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
        contacts.save_to_file("contacts.json")
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
        contacts.save_to_file("contacts.json")
    else:
        raise KeyError
    return f'\nContact {str(name).capitalize()} was successfully removed\n'

@input_validation
def days_to_birthday(*args):

    lst = args[0]

    if not lst:
        return '\nPlease provide "birthday" and contact name\n' 
    
    if len(lst) > 1:
        raise ValueError
    name = lst[0]

    records = contacts.find_records(name)
    if not records:
        return f'\nNo contact with name {name.capitalize()} found\n'

    result = ''
    for record in records:
        if record.birthday is not None:
            days = record.days_to_birthday()
            result += f'\n{record.name.value.capitalize()} has {days} day(s) left until their birthday.\n'
        else:
            result += f'\nNo birthday information found for {record.name.value.capitalize()}\n'
    return result

@input_validation
def search(*args):
    search_query = args[0][0]
    result = ''

    for record in contacts.data.values():
        name = str(record.name.value)
        phones = [str(phone) for phone in record.phones]
        phone_string = ', '.join(phones)

        if name.startswith(search_query) or any(phone.startswith(search_query) for phone in phones):
            birthday = record.birthday.value if record.birthday else None
            contact_info = f'\n{name.capitalize()}: {phone_string}'
            if birthday:
                contact_info += f'. Birthday: {birthday}\n'
            else:
                contact_info += '\n'
            result += contact_info

    if not result:
        return f'\nNo contact found with the query: {search_query}\n'
    return result

def show_all(*args):
    if not contacts:
        return '\nYour contacts list is empty\n'
    result = ''
    for record in contacts.data.values():
        name = str(record.name.value).capitalize()
        phones = ', '.join(str(phone) for phone in record.phones)
        birthday = record.birthday.value if record.birthday else None
        if birthday: 
            result += f'\n{name}: {phones}: {birthday}\n'
        else: 
            result += f'\n{name}: {phones}\n'
    return result


def show_page(*args):
    page_number, num_records = 1, 2
    if len(args[0]) > 0:
        page_number = int(args[0][0])
        if len(args[0]) > 1:
            num_records = int(args[0][1])

    if not contacts:
        return '\nYour contacts list is empty\n'
    result = ''
    pages = contacts.__iter__(num_records)

    for _ in range(page_number - 1):
        next(pages, None)
    page = next(pages, None)

    if not page:
        return '\nNo records found on this page\n'

    for record in page:
        name = str(record.name.value).capitalize()
        phones = ', '.join(str(phone) for phone in record.phones)
        birthday = record.birthday.value if record.birthday else None
        if birthday:
            result += f'\n{name}: {phones}. Birthday: {birthday}\n'
        else:
            result += f'\n{name}: {phones}\n'
    return result


COMMANDS = {
    hello: ['hi', 'hello', 'hey'],
    add_contact: ['add'],
    change: ['change'],
    phone: ['phone'],
    show_all: ['show'],
    remove_contact: ['remove', 'delete'],
    show_page: ['page'],
    days_to_birthday: ['birthday'],
    search:['search']
}


def main():
    file_name = 'contacts.json'
    contacts.load_from_file(file_name)

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