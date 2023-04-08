# **Contacts Management System**

## **Description**

This program is a simple command-line interface that allows users to manage their contacts. The program stores the contacts in a JSON file called contacts.json.

## **Functions**

### **load_contacts()**

Loads the contacts from the JSON file.

### **save_contacts(contacts)**

Saves the contacts to the JSON file.

### **input_validation(func)**

A decorator function that validates user input.

### **input_formatter(str)**

A function that formats user input.

### **command_handler(command)**

A function that handles user commands.

### **unknown_command(*args)**

A function that is called when an unknown command is entered.

### **hello()**

A function that greets the user.

### **add_contact(*args)**

A function that adds a contact to the list.

### **change(*args)**

A function that changes a contact's phone number.

### **phone(*args)**

A function that retrieves a contact's phone number.

### **remove_contact(*args)**

A function that removes a contact from the list.

### **show_all(*args)**

A function that displays all contacts.

## **Commands**

The following commands are available:

- hi, hello, hey: greets the user.
- add: adds a contact to the list.
- change: changes a contact's phone number.
- phone: retrieves a contact's phone number.
- show: displays all contacts.
- remove, delete: removes a contact from the list.
- page: shows contacts by pages (2 contacts/page default value)

## **Usage**

To run the program, simply execute the main() function. The program will display a greeting and prompt the user for input. Enter a command followed by any necessary arguments. To exit the program, enter one of the following: close, ., bye, or exit.
