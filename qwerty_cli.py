#!/bin/python3
import pyperclip
from crypto_ops import *
from getpass import getpass

pwd = getpass("Enter password: ")
entries = try_decrypt(pwd)
if not entries:
    print("Wrong password!")
    exit(1)
print("Welcome to qwerty")
search_term = ""
while True:
    for i in range(len(entries)):
        if search_term == "" or search_term.lower() in entries[i][0].lower():
            print(i + 1, ": ", entries[i][0], " : ", "*" * len(entries[i][1]))
    print("\nChoose an option:")
    print("1. copy entry value")
    print("2. edit entry key")
    print("3. edit entry value")
    print("4. add new entry")
    print("5. delete entry")
    print("6. search entry")
    print("7. change master password")
    print("8. save and exit")
    choice1 = input("> ")
    if choice1 == "1" or choice1 == "42":
        num = input("Enter the entry number: ")
        try:
            num = int(num) - 1
            if choice1 == "1":
                pyperclip.copy(entries[num][1])
                print("value for", entries[num][0], "copied to clipboard")
            else:
                print(entries[num][1])
        except IndexError:
            print("Invalid index")
        except ValueError:
            print("Please enter an integer")
        except:
            print("Could not copy value.")
    elif choice1 == "2":
        num = input("Enter the entry number: ")
        try:
            num = int(num) - 1
            new_key = input("Enter the new key: ")
            entries[num] = (new_key, entries[num][1])
            print("Success")
        except IndexError:
            print("Invalid index")
        except ValueError:
            print("Please enter an integer")
        except:
            print("Invalid")
    elif choice1 == "3":
        num = input("Enter the entry number: ")
        try:
            num = int(num) - 1
            pwd1 = getpass("Enter new value:")
            pwd2 = getpass("Re-enter new value:")
            if pwd1 != pwd2:
                print("Values don't match")
            else:
                entries[num] = (entries[num][0], pwd1)
                print("Success")
        except IndexError:
            print("Invalid index")
        except ValueError:
            print("Please enter an integer")
        except:
            print("Invalid")
    elif choice1 == "4":
        key = input("Enter the key: ")
        pwd1 = getpass("Enter value:")
        pwd2 = getpass("Re-enter value:")
        if pwd1 != pwd2:
            print("Values don't match")
        else:
            entries.append((key, pwd1))
            print("Success")
    elif choice1 == "5":
        num = input("Enter the entry number: ")
        try:
            num = int(num) - 1
            sure = input("Are you sure you want to delete the value for '" + entries[num][0] + "'?(yes/no)")
            if sure == "yes":
                deleted = entries.pop(num)
                print("Deleted entry for", deleted[0])
            else:
                print("Did not delete anything")
        except IndexError:
            print("Invalid index")
        except ValueError:
            print("Please enter an integer")
        except:
            print("Invalid")
    elif choice1 == "6":
        term = input("Enter the search term: ")
        search_term = term
        print("search term", term, "applied. Press enter to clear it.")
    elif choice1 == "7":
        pwd1 = getpass("Enter new password:")
        pwd2 = getpass("Re-enter new password:")
        if pwd1 != pwd2:
            print("Passwords don't match")
        else:
            pwd = pwd1
            print("Password changed successfully")
    elif choice1 == "8":
        text = ""
        for entry in entries:
            text += entry[0] + '\n'
            text += entry[1] + '\n'
        save_entries(text, pwd)
        exit(0)
    elif choice1 == "":
        search_term = ""
    else:
        print("Invalid option")
    print("\n")
