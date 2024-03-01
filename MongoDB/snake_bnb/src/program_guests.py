import datetime
from dateutil import parser

from infrastructure.switchlang import switch
import program_hosts as hosts
import services.data_service as svc
from program_hosts import success_msg, error_msg
import infrastructure.state as state


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_snake)
            s.case('y', view_your_snakes)
            s.case('b', book_a_cage)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a cage')
    print('[A]dd a snake')
    print('View [y]our snakes')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_snake():
    print(' ****************** Add a snake **************** ')
    if not state.active_account:
        error_msg('You must log in first to add a snake')
        return

    name = input('Snake name: ')
    if not name:
        error_msg('cancelled')
        return

    length = float(input('How long is your snake (in meters)? '))
    species = input('Species? ')
    is_venomous = input('Is your snake venomous [y]es, [n]o? ').lower().startswith('y')

    snake = svc.add_snake(state.active_account, name, length, species, is_venomous)
    state.reload_account()
    success_msg(f'Created {snake.name} with id {snake.id}')


def view_your_snakes():
    print(' ****************** Your snakes **************** ')
    if not state.active_account:
        error_msg('You must log in first to view your snakes')
        return

    snakes = svc.get_snakes_for_user(state.active_account.id)
    print(f'You have {len(snakes)} snakes.')
    for s in snakes:
        print(f' * {s.name} is a {s.species} that is {s.length}m long and is {'' if s.is_venomous else 'not '}venomous.')


def book_a_cage():
    print(' ****************** Book a cage **************** ')
    if not state.active_account:
        error_msg('You must log in first to book a cage')
        return

    snakes = svc.get_snakes_for_user(state.active_account.id)
    if not snakes:
        error_msg('You must [a]dd a snake first, before booking a cage.')
        return
    
    print('Finding available cages.')
    start_text = input('Check-in date [yyyy-mm-dd]: ')
    if not start_text:
        error_msg('Cancelled')
        return
    
    checkin = parser.parse(start_text)
    checkout = parser.parse(input("Check-out date [yyyy-mm-dd]: "))
    if checkin >= checkout:
        error_msg('Check-in date should be before check-out date.')
        return

    # From the list of the guest snakes, which snake does he want to book
    print()
    for idx, s in enumerate(snakes):
        print(f'{idx + 1}. {s.name} (species: {s.species}, lenghth: {s.length}m, venomous: {'yes' if s.is_venomous else 'no'})')

    snake = snakes[int(input('Which snake do you want to book (number)')) - 1]

    # Find cages available across the date range
    cages = svc.get_available_cages(checkin, checkout, snake)

    # Let the user choose the cage from the available cages
    print(f'There are {len(cages)} available for the choosen dates.')
    for idx, c in enumerate(cages):
        print(f'{idx + 1}. {c.name} with {c.square_meters}m, carpeted: {'yes' if c.is_carpeted else 'no'} and toys: {'yes' if c.has_toys else 'no'}')

    if not cages:
        error_msg("Sorry! There aren't any available cages at the moment.")
        return
    
    cage = cages[int(input('Which cage do you want to book (number)')) - 1]
    svc.book_cage(state.active_account, snake, cage, checkin, checkout)

    success_msg(f'You successfully booked the cage {cage.name} at {cage.price}$ per night.')

def view_bookings():
    print(' ****************** Your bookings **************** ')
    if not state.active_account:
        error_msg("You must log in first to register a cage")
        return
    
    # List the booking info along with the snake info
    # Get the snake given a snake id for all the snakes belonging to the guest - key: snake id; value: snake
    snakes = {s.id: s for s in svc.get_snakes_for_user(state.active_account.id)}
    bookings = svc.get_bookings_for_user(state.active_account.email)

    print(f'You have {len(bookings)} bookings.')
    for b in bookings:
        print('  * Snake: {} is booked at {} from {} for {} days'.format(
            snakes.get(b.guest_snake_id).name,
            b.cage.name,
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            (b.check_out_date - b.check_in_date).days
        ))
