import datetime
from colorama import Fore
from dateutil import parser

from infrastructure.switchlang import switch
import infrastructure.state as state
import services.data_service as svc


def run():
    print(' ****************** Welcome host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', create_account)
            s.case('l', log_into_account)
            s.case('y', list_cages)
            s.case('r', register_cage)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an [a]ccount')
    print('[L]ogin to your account')
    print('List [y]our cages')
    print('[R]egister a cage')
    print('[U]pdate cage availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ****************** REGISTER **************** ')
    name = input('Name: ')
    email = input('Email: ').strip().lower()
    
    # Check if the email is already registered
    old_account = svc.find_account_by_email(email)
    if old_account:
        error_msg(f'ERROR: This email ({email}) is already registered.')
        return # Doesn´t create the account
    
    state.active_account = svc.create_account(name, email)
    success_msg(f'Your account has been successfully created with the id {state.active_account.id}.')

def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input('User email: ').strip().lower()
    account = svc.find_account_by_email(email)

    if not account:
        error_msg(f'Account with email {email} does not exist.')
        return

    state.active_account = account
    success_msg('You are logged in!')

def register_cage():
    print(' ****************** REGISTER CAGE **************** ')

    if not state.active_account:
        error_msg('You have to login first.')
        return
    
    meters = input('How many square meters does the cage have? ')
    if not meters:
        error_msg('Cancelled!')
        return
    meters = float(meters) # Covert it to float type

    price = input('Define a price for your cage: ')
    if not price:
        error_msg('Cancelled!')
        return
    price = float(price) # Covert it to float type

    carpeted = input('Is the cage carpeted? [y \ n]').lower().startswith('y')
    toys = input('The cage has toys? [y \ n]').lower().startswith('y')
    allow_dangerous = input('The cage allows dangerous snakes? [y \ n]').lower().startswith('y')
    name = input('Assign a name to your cage: ')

    cage = svc.register_cage(state.active_account, meters, price, carpeted, toys, allow_dangerous, name)

    state.reload_account()
    success_msg(f'Cage registered successfully with id {cage.id}!')

def list_cages(suppress_header=False):
    if not suppress_header:
        print(' ******************     Your cages     **************** ')

    if not state.active_account:
        error_msg('You have to login first.')
        return
    
    cages = svc.find_cages_for_user(state.active_account)
    print(f'You have a total of {len(cages)} cages.')
    for idx,c in enumerate(cages):
        print(f' {idx+1}. {c.name} is {c.square_meters} meters.')
        print(f' {idx+1}. {c.name} costs {c.price} euros.')
        print(f' {idx+1}. {c.name} is carpeted? {c.is_carpeted}')
        print(f' {idx+1}. {c.name} has toys? {c.has_toys}')
        print(f' {idx+1}. {c.name} allow dangerous snakes? {c.allow_dangerous_snakes}')
        for b in c.bookings:
            print(f'   * Booking {b.check_in_date}, {(b.check_out_date - b.check_in_date).days} days, booked? {'Yes' if b.booked_date is not None else 'No'}')



def update_availability():
    print(' ****************** Add available date **************** ')

    if not state.active_account:
        error_msg('You have to login first.')
        return
    
    list_cages(suppress_header=True)

    cage_num = input('Enter the cage number: ')
    if not cage_num.strip():
        error_msg('Cancelled!')
        return
    
    cage_num = int(cage_num)

    cages = svc.find_cages_for_user(state.active_account)
    select_cage = cages[cage_num-1]

    success_msg(f'You selected the cage {select_cage.name}.')

    start_date = parser.parse(input('Enter available date [yyyy-mm-dd]: ')) 
    days = int(input('How many days is this block of time? '))

    svc.add_available_date(select_cage, start_date, days)

    success_msg(f'Date added to the availability of cage {select_cage.name}')


def view_bookings():
    print(' ****************** Your bookings **************** ')

    if not state.active_account:
        error_msg('You have to login first.')
        return

    # Get the cages and nested bookings as a flat list
    cages = svc.find_cages_for_user(state.active_account)

    # List of all the bookings from all of the host cages, we just want the ones that have been booked, so they have a booked_date set
    bookings =[
        (c, b)
        for c in cages
        for b in c.bookings
        if b.booked_date is not None
    ]

    #  Print the details of each
    print(f"You have {len(bookings)} bookings.")
    for c, b in bookings:
        print(' * Cage: {}, booked date: {}, from {} for {} days.'.format(
            c.name,
            datetime.date(b.booked_date.year, b.booked_date.month, b.booked_date.day),
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            b.duration_in_days
        ))

def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()

def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()

def unknown_command():
    print("Sorry we didn't understand that command.")

def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)

def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
