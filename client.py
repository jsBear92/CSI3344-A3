from xmlrpc.client import ServerProxy

# Connect from the server
proxy = ServerProxy('http://localhost:9999')

# Variables


def first_menu():
    while True:
        print("********************************************************")
        print("Welcome to Honor Enrolment Pre-assessment System (HEPaS)")
        print("1. Sign up")
        print("2. Login")
        print("3. Exit")
        print("********************************************************")
        try:
            answer = int(input("Menu: "))
            if answer <= 0:
                print("Please enter a number is greater than 0")
            elif answer == 1:
                sign_up_menu()
            elif answer == 2:
                login_menu()
            elif answer == 3:
                break
            else:
                print("Please enter a number between 1 ~ 3")
        except ValueError as e:
            print("")
            print(f"Please enter a number -> {e}")
            print("")


def sign_up_menu():
    print("********************************************************")
    print("Please enter proper information")
    login_id = input("ID: ")
    login_password = input("Password: ")
    last_name = input("Last Name: ")
    while True:
        try:
            student = input("Are you EOU student? [yes/no]: ").lower()
            if student == "yes":
                student_id = input("EOU Student ID: ")
                eou_email = input("EOU email: ")
                print("")
                print("Thank you for inputting your information.")
                print("You are signed up now.")
                print("")
                break
            elif student == "no":
                print("Enter the unit ID and the mark")
                while True:
                    try:
                        units = int(input("How many units did you enrol?: "))
                        list_id = []
                        list_mark = []
                        if 12 <= units <= 30:
                            for i in range(units):
                                list_id.append(input(f"[{i+1}] ID: "))
                                mark = int(input(f"[{i + 1}] Mark: "))
                                if 0 <= mark <= 100:
                                    list_mark.append(mark)
                            break
                    except ValueError as e:
                        print("")
                        print(f"Please enter a number between 12 ~ 30 -> {e}")
                        print("")
                print("")
                print("Thank you for inputting your information.")
                print("You are signed up now.")
                print("")
                break
        except TypeError as e:
            print("")
            print("Please enter yes or no")
            print("")



def login_menu():
    while True:
        print("********************************************************")
        print("Please login to access the system")
        print("If you want to exit, Please enter 'exit'")
        login_id = input("ID: ").lower()
        if login_id == "exit":
            break
        else:
            login_password = input("Password: ")
            if login_token(proxy.authorize_login(login_id, login_password)):
                print("You are successfully logged")
                main_menu()
                break
            else:
                print("Your login information is wrong")


def login_token(token):
    if token:
        return True
    else:
        return False


def main_menu():
    print("********************************************************")
    print("Welcome to ")


if __name__ == '__main__':
    first_menu()



