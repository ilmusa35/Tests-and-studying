
balance = 1000.0
pin = 1111


def main_menu():
    print("----Main Menu-----")
    print("1. Display balance")
    print("2. Withdraw Money")
    print("3. Deposit Money")
    print("4. Exit")


def withdraw_menu():
    print("----Withdraw Menu-----")
    print("1. 10 GBP")
    print("2. 20 GBP")
    print("3. 30 GBP")
    print("4. 50 GBP")
    print("5. Enter Other Amount")
    sub_choice = int(input("Select an option:"))
    if sub_choice == 1:
        return 10
    elif sub_choice == 2:
        return 20
    elif sub_choice == 3:
        return 30
    elif sub_choice == 4:
        return 50
    elif sub_choice == 5:
        with_amount = int(input(f"Enter the amount (no more {balance}):"))
        if with_amount <= balance:
            if with_amount % 10 == 0:
                return with_amount
            else:
                print("Amount must be multiplied by 10, try another amount")
                return withdraw_menu()
        else:
            print("You have not enough money")
            return 0

    else:
        return 0


def enter_pin(attempt):
    user_pin = input("Enter your PIN code:")
    if int(user_pin) != pin and attempt < 2:
        attempt += 1
        print(f"Your PIN is incorrect, try again. {3-attempt} attempts left")
        user_pin = enter_pin(attempt)
    elif attempt >= 2:
        print("Your card is blocked! Call to your bank")
        user_pin = 0.00001
    return user_pin


def main():
    global balance
    print("Welcome to the London City Bank")
    print("For any operations with your account")
    user_pin = enter_pin(0)
    if user_pin == 0.00001:
        return False

    no_break = True
    while no_break:
        main_menu()
        choice = int(input("Select an option:"))
        if choice > 4:
            if int(choice) == 9:
                print("Good bye!")
            else:
                print("wrong option")
            no_break = False
        else:
            if choice == 1:
                print(f"Your balance:{balance}")
                answer = input("Would you like to continue? Y/N")
                if answer == "Y":
                    pass
                else:
                    print("Good bye!")
                    no_break = False
            elif choice == 2:
                withdraw_amount = withdraw_menu()
                balance = balance - withdraw_amount
                print(f"Your new balance is {balance}")
                answer = input("Would you like to continue? Y/N")
                if answer == "Y":
                    pass
                else:
                    print("Good bye!")
                    no_break = False
            elif choice == 3:
                deposit_sum = int(input("Deposit amount:"))
                balance = balance + deposit_sum
                print(f"Your new balance is {balance}")
                answer = input("Would you like to continue? Y/N")
                if answer == "Y":
                    pass
                else:
                    print("Good bye!")
                    no_break = False
            else:
                print("Good bye!")
                no_break = False


main()
