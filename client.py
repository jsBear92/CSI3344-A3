import re
from xmlrpc.client import ServerProxy


class Error(Exception):
    pass


class OutOfRangeError(Error):
    pass

# global variable for sending login id information to server
login_id = None


# First menu (no Login status)
def first_menu():
    while True:
        print("")
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


# Client side input validation
# We use 36 as max length because of the common UUID length
def prompt_user(input_type):
    try:
        data = input("Enter " + input_type + ": ")
        if len(data) <= 0 or len(data) > 36:
            raise OutOfRangeError
    except OutOfRangeError:
        print("Out of range " + input_type + "! Please enter valid non-empty " + input_type + " with length less than 36.")
        prompt_user(input_type)
    return data


# sign up menu
def sign_up_menu():
    print("")
    print("********************************************************")
    print("Please enter proper information")
    while True:
        login_id = prompt_user("ID")
        login_password = prompt_user("Password")
        last_name = prompt_user("Last Name")
        try:
            student = input("Are you EOU student? [yes/no]: ").lower()

            # for EOU Student
            if student == "yes":
                regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]+eou.edu.au$'
                while True:
                    eou_email = prompt_user("EOU email(***@eou.edu.au)")
                    if re.search(regex, eou_email):
                        proxy.sign_up_eou(login_id, login_password, last_name, eou_email)
                        break
                    else:
                        print("Please enter proper EOU email address.")
                print("")
                print("Thank you for inputting your information.")
                print("You are signed up now.")
                print("")
                break

            # for Non-EOU Student
            elif student == "no":

                # give student information first to the server
                proxy.sign_up(login_id, login_password, last_name)
                print("Enter the unit ID and the mark")
                while True:
                    try:
                        units = int(input("How many units did you enrol? (12 ~ 30): "))
                        list_id = []
                        list_mark = []
                        if 12 <= units <= 30:
                            for i in range(units):

                                # unit ID is being converted to upper case
                                list_id.append(input(f"[{i+1}] ID: ").upper())
                                while True:
                                    try:
                                        mark = int(input(f"[{i + 1}] Mark (0 ~ 100): "))
                                        if 0 <= mark <= 100:
                                            list_mark.append(mark)
                                            break
                                    except ValueError as e:
                                        print("")
                                        print(f"Please enter a number between 0 ~ 100 -> {e}")
                                        print("")

                            # send unit information of Non-EOU student to the server
                            statement = proxy.manual_add(list_id, list_mark, login_id)
                            print(statement)
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
            else:
                print("")
                print("Please enter 'yes' or 'no'")
                print("")
        except TypeError as e:
            print("")
            print("Please enter yes or no -> ", e)
            print("")


# Login menu
def login_menu():
    while True:
        global login_id
        print("")
        print("********************************************************")
        print("Please login to access the system")
        print("If you want to exit, Please enter 'exit'")
        login_id = input("ID: ").lower()

        # exit to first menu
        if login_id == "exit":
            break
        else:
            login_password = input("Password: ")

            # send user id and password to the server to check information is in the db
            if login_token(proxy.authenticate_login(login_id, login_password)):
                print("You are successfully logged")

                # go to main menu after success login process
                main_menu()
                break
            else:
                print("Your login information is wrong")


def login_token(token):
    if token:
        return True  # login information matches the db
    else:
        return False  # login information doesn't match the db


# main menu after success login process
def main_menu():

    # get this data for global variables for getting unit data
    global login_id
    while True:
        print("")
        print("********************************************************")
        print("Welcome to HEPaS Unit inquiry")
        print("********************************************************")
        print("1. Individual Scores")
        print("2. Course Average")
        print("3. Best 8 marks and Average")
        print("4. Honors Evaluation")
        print("5. Single unit score")
        print("6. Logout")
        print("")
        try:
            answer = int(input("Menu: "))
            if answer == 1:
                individual_score(login_id)
            elif answer == 2:
                average_mark(login_id)
            elif answer == 3:
                best_mark(login_id)
                best_mark_avg(login_id)
            elif answer == 4:
                evaluation_criteria(login_id)
            elif answer == 5:
                unit_id = str(input("Unit ID: ").upper())
                single_score(login_id, unit_id)
            elif answer == 6:  # Exit to first menu
                proxy.alert(login_id)
                break
            else:
                print("Please Select proper menu number 1 ~ 5")
        except ValueError as e:
            print("Please Select proper menu number 1 ~ 5 -> ", e)


def individual_score(login_id):
    row_list = proxy.inquiry_mark(login_id)
    i = 1
    # ex) 1. ['CSP1234', 65.0]
    for data in row_list:
        print(f"{i}.", data)
        i += 1


def average_mark(login_id):
    average = proxy.average_mark(login_id)
    print("The Course Average: ", average)


def best_mark(login_id):
    best = proxy.best_mark(login_id)
    print("The best 8 marks")
    i = 1
    # ex) 1. ['CSI1234', 86.0]
    for data in best:
        print(f"{i}.", data)
        i += 1


def best_mark_avg(login_id):
    best_avg = proxy.best_mark_avg(login_id)
    print("The average of best 8 marks: ", best_avg)


def evaluation_criteria(login_id):
    evaluation = proxy.evaluation_criteria(login_id)
    print(evaluation)


def single_score(login_id, unit_id):
    score = proxy.single_score(login_id, unit_id)
    print(f"The {unit_id.upper()} score: ", score)


# client starts
if __name__ == '__main__':
    # Connect from the server
    proxy = ServerProxy('http://localhost:9999')

    # Enter to First menu
    first_menu()



