# --- Mini Password Generator & Manager MVP V0.1 ---
# Core Focus: Demonstrate basic Python logic, file I/O, and user interaction.
# Simplicity is key. No complex encryption or GUI in this version.

import random
import string # For character sets (e.g., letters, digits)
import csv    # For simple data storage in a CSV file

# --- Configuration ---
PASSWORD_FILE = "passwords_vault.csv" # File to store password entries
FIELD_NAMES = ["platform", "username", "password"] # CSV Header

# --- Core Functions ---

def generate_password(length: int = 12, use_uppercase: bool = True, use_digits: bool = True) -> str:
    """
    Generates a random password based on specified criteria.
    V0.1: Uses only letters (upper/lower if specified) and digits. No special symbols.
    """
    characters = string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    
    if not characters: # Fallback if no character types are selected
        return "Error:NoCharacterTypesSelected"

    # (总司令，这里用了一个列表推导式和 .join() 来生成密码，简洁高效！)
    # (random.choice(characters) 会从 characters 字符串中随机选一个字符)
    # (for _ in range(length) 表示重复 length 次)
    password = "".join([random.choice(characters) for _ in range(length)])
    return password

def add_password_entry():
    """Adds a new password entry to the vault."""
    print("\n--- Add New Password Entry ---")
    platform = input("Enter platform/service name: ").strip()
    username = input(f"Enter username for {platform}: ").strip()
    
    # Password generation option
    choice = input("Generate a password automatically? (yes/no, default: yes): ").lower().strip()
    if choice == "no":
        password = input(f"Enter password for {username}@{platform}: ").strip()
    else:
        # (总司令，这里调用了我们上面定义的 generate_password 函数！)
        pw_length_str = input("Enter desired password length (e.g., 12, default: 12): ").strip()
        try:
            pw_length = int(pw_length_str) if pw_length_str else 12
            if pw_length < 4: # Basic sanity check
                print("Password length too short, defaulting to 12.")
                pw_length = 12
        except ValueError: # (总司令，这是简单的错误处理，如果用户输入的不是数字)
            print("Invalid length, defaulting to 12.")
            pw_length = 12
            
        password = generate_password(length=pw_length)
        print(f"Generated password: {password}")

    # (总司令，这里我们将用 'a' 模式 (append) 打开文件，在末尾追加新行)
    # (newline='' 是为了防止csv写入时产生空行)
    # (try...except...finally 结构，确保文件操作的稳健性)
    try:
        with open(PASSWORD_FILE, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
            # If the file is empty, write the header first
            # (总司令，csvfile.tell() 返回文件指针当前位置，如果是0，说明文件是空的)
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow({"platform": platform, "username": username, "password": password})
        print(f"Entry added for {platform} successfully!")
    except IOError:
        print(f"Error: Could not write to password file '{PASSWORD_FILE}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def view_all_entries():
    """Views all password entries from the vault."""
    print("\n--- All Stored Password Entries ---")
    try:
        with open(PASSWORD_FILE, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            entries_found = False
            # (总司令，这里用 for 循环逐行读取和处理CSV文件中的数据)
            for row_number, row_dict in enumerate(reader, 1): # enumerate 额外给出行号
                print(f"Entry {row_number}:")
                print(f"  Platform: {row_dict['platform']}")
                print(f"  Username: {row_dict['username']}")
                print(f"  Password: {row_dict['password']}")
                print("-" * 20) # Separator
                entries_found = True
            
            if not entries_found:
                print("No entries found in the vault. It's empty or the file doesn't exist yet.")
    except FileNotFoundError:
        print(f"Password file '{PASSWORD_FILE}' not found. Add an entry to create it.")
    except IOError:
        print(f"Error: Could not read password file '{PASSWORD_FILE}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def search_entries():
    """Searches for entries by platform name."""
    print("\n--- Search Password Entries ---")
    search_term = input("Enter platform name to search for (case-insensitive): ").lower().strip()
    if not search_term:
        print("Search term cannot be empty.")
        return

    found_count = 0
    try:
        with open(PASSWORD_FILE, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row_dict in reader:
                # (总司令，这里用 .lower() 实现不区分大小写搜索)
                if search_term in row_dict['platform'].lower(): 
                    print(f"\nFound matching entry:")
                    print(f"  Platform: {row_dict['platform']}")
                    print(f"  Username: {row_dict['username']}")
                    print(f"  Password: {row_dict['password']}") # In a real app, we wouldn't print passwords like this!
                    found_count += 1
            
            if found_count == 0:
                print(f"No entries found matching '{search_term}'.")
            else:
                print(f"\nFound {found_count} entry/entries matching your search.")
    except FileNotFoundError:
        print(f"Password file '{PASSWORD_FILE}' not found. Nothing to search.")
    except IOError:
        print(f"Error: Could not read password file '{PASSWORD_FILE}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Main Application Loop (总司令，这是我们程序的核心驱动，一个while True无限循环) ---
def main_application_loop():
    """Main loop for the password manager application."""
    print("\nWelcome to the AI Legion's Secure Password Vault V0.1!")
    print("=" * 50)

    while True: # Infinite loop until user quits
        print("\nAvailable actions:")
        print("1. Add new password entry")
        print("2. View all entries")
        print("3. Search for an entry")
        print("4. Generate a standalone password")
        print("5. Quit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            add_password_entry()
        elif choice == '2':
            view_all_entries()
        elif choice == '3':
            search_entries()
        elif choice == '4':
            pw_length_str = input("Enter desired password length (e.g., 12, default: 12): ").strip()
            try:
                pw_length = int(pw_length_str) if pw_length_str else 12
                if pw_length < 4:
                    print("Password length too short, defaulting to 12.")
                    pw_length = 12
            except ValueError:
                print("Invalid length, defaulting to 12.")
                pw_length = 12
            generated_pw = generate_password(length=pw_length)
            print(f"Standalone Generated Password: {generated_pw}")
        elif choice == '5':
            print("Exiting Secure Password Vault. Stay vigilant, Commander!")
            break # Exit the while loop
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
        
        # Pause for readability before showing menu again
        if choice != '5': # Don't pause if quitting
            input("\nPress Enter to continue...")


# --- Program Execution Start ---
# (总司令，这句 if __name__ == "__main__": 是Python的惯用写法，
# 意思是“只有当这个脚本被直接运行时，才执行下面的代码块”。
# 如果这个脚本被其他脚本作为模块导入(import)，则不自动执行。)
if __name__ == "__main__":
    main_application_loop()