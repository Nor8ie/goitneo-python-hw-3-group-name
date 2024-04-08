from collections import UserDict, defaultdict
from datetime import datetime, timedelta

class NameError(Exception):
    pass

class PhoneNotFoundError(Exception):
    pass

class NumberError(Exception):
    pass

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    @staticmethod
    def name_validation(name):
        if not name.isalpha():  # Ensure name contains only alphabetic characters
            raise NameError("Name must contain only alphabetic characters.")
        return True, name

class Phone(Field):
    @staticmethod
    def phone_validation(phone):
        if not phone.isdigit() or len(phone) != 10:  # Ensure phone is all digits and has length 10
            raise NumberError('Phone number is not valid. Please provide a number with exactly 10 digits.')
        return True, phone

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        self.date = datetime.strptime(value, '%d.%m.%Y').date()

    @staticmethod
    def birthday_validation(birthday): #used to validate date format for birthday dates
        try:
            birthday = datetime.strptime(birthday, "%d.%m.%Y")
            return True, birthday
        except ValueError:
            return False, "Invalid birthday format. Please use DD.MM.YYYY."

class Record:
    def __init__(self, name, phone):
        self.name = Name(name)
        self.phones = [Phone(phone)]
        self.birthday = None

    def add_phone(self, phone):      # adds the contact and also used with command add-phone to add more phone numbers
        valid, msg = Phone.phone_validation(phone)
        if valid:
            if phone not in [p.value for p in self.phones]:
                self.phones.append(Phone(phone))
                print("Phone number added.")
            else:
                print("Phone number already exists for this contact.")
        else:
            print(msg)

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                print("Contact updated.")
                return
        print("Phone number not found for this contact.")

    def find_phone(self, phone_number):
        for i in self.phones:
            if i.value == phone_number:
                return i.value
        return None

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                print("Phone number removed.")
                return
        raise PhoneNotFoundError("Phone number does not exist for this contact.")

    def add_birthday(self, birthday):
        valid, msg = Birthday.birthday_validation(birthday)
        if valid:
            self.birthday = Birthday(birthday)
        else:
            raise ValueError(msg)  # Raise ValueError for invalid birthday format

    def show_birthday(self):
        if self.birthday:
            return f"The birthday of {self.name} is: {self.birthday}"
        else:
            return f"No birthday found for {self.name}."

    def __str__(self):
        phones_str = ', '.join(str(phone) for phone in self.phones)
        return f"Contact name: {self.name}, phones: {phones_str}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def add_record(self, name, phone):
        if not any(record.name.value == name and any(p.value == phone for p in record.phones) for record in self.data.values()):
            self.data[name] = Record(name, phone)
            print("Contact added.")
        else:
            print("Contact with the same name and phone number already exists.")

    def add_phone(self, name, phone):
        record = self.find(name)
        if record:
            record.add_phone(phone)
        else:
            print("Contact not found. Please enter an existing contact.")

    def find(self, name):
        if name in self.data:
            return self.data[name]
        else:
            return None

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        birthdays_per_week = defaultdict(list)
        today = datetime.today()  # Use datetime object instead of date

        for name, record in self.data.items():
            birthday = record.birthday.value
                # Convert birthday to datetime object
            birthday_datetime = datetime.strptime(birthday, "%d.%m.%Y")

                # Adjust birthday for this year or next year if it has passed
            birthday_this_year = birthday_datetime.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                # Calculate days until the next birthday
            delta_days = (birthday_this_year - today).days

                # Check if the birthday is within the next week
            if 0 <= delta_days < 7:
                birthday_weekday = birthday_this_year.strftime("%A")
                if birthday_weekday == "Saturday" or birthday_weekday == "Sunday":
                    birthday_weekday = "Monday"
                birthdays_per_week[birthday_weekday].append(name)

        result = ""
        for day, names in birthdays_per_week.items():
            result += f"{day}: {', '.join(names)}\n"
        return result.strip()
    
    def show_all(self):
        if not self.data:
            return "No contacts found."
        result = ""
        for name, record in self.data.items():
            result += f"{record}\n"
        return result.strip()

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def main():
    address_book = AddressBook()
    print("Welcome to the assistant bot! Please type 'Hello' to continue")
    
    while True:
        user_input = input("Enter a command: ").strip().lower()

        if not user_input:
            print('Please type a valid command or "exit" to close.')
            continue

        command, *args = user_input.split()

        if command in ["close", "exit"]:
            print("Goodbye!")
            break

        elif command == "hello":
            print("""
            How can I help you?
            Please choose from the following options:
            ** Add a new contact                          >>> add [name] [phone]
            ** Add a new phone for existing contact       >>> add-phone [name] [phone]   
            ** Change an existing contact                 >>> change [name] [old phone number] [new phone number]
            ** Display number for an existing contact     >>> phone [name]
            ** Display all contacts from the phonebook    >>> all
            ** Add birthday for a contact                 >>> add-birthday [name] [DD.MM.YYYY]
            ** Show birthday for a contact                >>> show-birthday [name]
            ** Show birthdays in the next week            >>> birthdays
            ** Delete a number for existing contact       >>> delete-number [name] [phone]
            ** Delete a contact from the address book     >>> delete-contact [name]          
            ** Exit the application                       >>> close or exit
            """)

        elif command == "add":
            if len(args) != 2:
                print("Invalid input. Please provide: add [name] [phone]")
            else:
                name, phone = args
                try:
                    name_validated = Name.name_validation(name)  # Validate name
                    phone_validated = Phone.phone_validation(phone)  # Validate phone number
                    address_book.add_record(name_validated[1], phone_validated[1])  # Add the contact to the address book
                except (NameError, NumberError) as e:
                    print(str(e))
        elif command == "add-phone":
            if len(args) != 2:
                print("Invalid input. Please provide: add-phone [name] [phone]")
            else:
                name, phone = args
                try:
                    name_validated = Name.name_validation(name)
                    phone_validated = Phone.phone_validation(phone)
                    if name_validated[0] and phone_validated[0]:
                        address_book.add_phone(name_validated[1], phone_validated[1])
                        print("Phone number added.")
                    else:
                        print("Name or phone number is not valid.")
                except (NameError, NumberError) as e:
                    print(str(e))

        elif command == "change":
            if len(args) != 3:
                print("Invalid input. Please provide: change [name] [old phone number] [new phone number]")
            else:
                name, old_phone, new_phone = args
                try:
                    name_validated = Name.name_validation(name)
                    phone_validated = Phone.phone_validation(new_phone)
                    if name_validated[0] and phone_validated[0]:
                        record = address_book.find(name_validated[1])
                        if record:
                            try:
                                record.edit_phone(old_phone, phone_validated[1])
                                print("Contact updated.")
                            except NumberError as e:
                                print(str(e))
                        else:
                            print("Contact not found. Please enter an existing contact.")
                    else:
                        print("Name or new phone number is not valid.")
                except (NameError, NumberError) as e:
                    print(str(e))

        elif command == "phone":
            if len(args) != 1:
                print("Invalid input. Please provide: phone [name]")
            else:
                name = args[0]
                try:
                    name_validated = Name.name_validation(name)
                    record = address_book.find(name_validated[1])
                    if record and len(record.phones) > 1:
                        print(f"The phone numbers for {name} are: {'; '.join(p.value for p in record.phones)}")

                    elif record:
                        print(f"The phone number for {name} is: {record.phones[0]}")
                    else:
                        print("Contact not found. Please enter an existing contact.")
                except NameError as e:
                    print(str(e))

        elif command == "all":
            print(address_book.show_all())

        elif command == "add-birthday":
            if len(args) != 2:
                print("Invalid input. Please provide: add-birthday [name] [DD.MM.YYYY]")
            else:
                name, birthday = args
                try:
                    name_validated = Name.name_validation(name)
                    if name_validated[0]:
                        record = address_book.find(name_validated[1])
                        if record:
                            record.add_birthday(birthday)
                            print(f"Birthday added for {name_validated[1]}.")
                        else:
                            print("Contact not found. Please enter an existing contact.")
                    else:
                        print("Name is not valid.")
                except (NameError, ValueError) as e:
                    print(str(e))


        elif command == "show-birthday":
            if len(args) != 1:
                print("Invalid input. Please provide: show-birthday [name]")
            else:
                name = args[0]
                try:
                    name_validated = Name.name_validation(name)
                    if name_validated[0]:
                        record = address_book.find(name_validated[1])
                        if record and record.birthday:
                            print(record.show_birthday())
                        elif record and not record.birthday:
                            print(f"No birthday found for {name_validated[1]}.")
                        else:
                            print("Contact not found. Please enter an existing contact.")
                    else:
                        print("Name is not valid.")
                except NameError as e:
                    print(str(e))

        elif command == "birthdays":
            birthdays = address_book.get_birthdays_per_week()
            if birthdays:
                print(birthdays)
            else:
                print("No birthdays in the next week.")
        
        elif command == "delete-contact":
            if len(args) != 1:
                print("Invalid input. Please provide: delete-contact [name]")
            else:
                name = args[0]
                try:
                    name_validated = Name.name_validation(name)
                    if name_validated[0]:
                        if name_validated[1] in address_book.data:
                            del address_book.data[name_validated[1]]
                            print(f"Contact {name_validated[1]} has been deleted.")
                        else:
                            print("Contact not found. Please enter an existing contact.")
                    else:
                        print("Name is not valid.")
                except NameError as e:
                    print(str(e))

        elif command == "delete-number":
            if len(args) != 2:
                print("Invalid input. Please provide: delete-number [name] [phone]")
            else:
                name, phone = args
                try:
                    name_validated = Name.name_validation(name)
                    phone_validated = Phone.phone_validation(phone)
                    if name_validated[0] and phone_validated[0]:
                        if name_validated[1] in address_book.data:
                            record = address_book.data[name_validated[1]]
                            try:
                                record.remove_phone(phone_validated[1])
                                print(f"Phone number {phone_validated[1]} has been removed from {name_validated[1]}.")
                            except PhoneNotFoundError as e:
                                print(str(e))
                        else:
                            print("Contact not found. Please enter an existing contact.")
                    else:
                        print("Name or phone number is not valid.")
                except (NameError, NumberError) as e:
                    print(str(e))

if __name__ == "__main__":
    main()

