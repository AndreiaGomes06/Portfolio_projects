import datetime
import bson
from typing import Optional, List
from data.owners import Owner
from data.cages import Cage
from data.bookings import Booking
from data.snakes import Snake

def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save() # When we call save all the default values are set and its saved to the collection owners
                 # Also atributes an _id
    return owner

def find_account_by_email(email: str) -> Owner:
    # Query the dataset to find if the email is already resgistered
    owner = Owner.objects().filter(email=email).first()

    return owner

def register_cage(active_account: Owner, meters: float, price: float, carpeted: bool, toys: bool, allow_dangerous: bool, name: str) -> Cage:
    cage = Cage()

    cage.name = name
    cage.price = price
    cage.square_meters = meters
    cage.is_carpeted = carpeted
    cage.has_toys = toys
    cage.allow_dangerous_snakes = allow_dangerous

    cage.save() # Save it in the database

    # We have to get the lastest account from the database
    account = find_account_by_email(active_account.email)
    # cage.id is the generated value by MongoDB
    account.cage_ids.append(cage.id)
    # Save the alterations made in the account (Owner) back in MongoDB
    account.save()

    return cage

def find_cages_for_user(account: Owner) -> List[Cage]:
    # Special query that searches for an id in the list of cages ids
    query = Cage.objects(id__in=account.cage_ids)
    cages = list(query)

    return cages

def add_available_date(cage: Cage, start_date: datetime.datetime, days: int) -> Cage:
    booking = Booking()

    booking.check_in_date = start_date
    # To get the check out date, we have to add the days to the check in date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    cage = Cage.objects(id=cage.id).first()
    # Bookings are not top levels items, are embedded in the cage collection
    cage.bookings.append(booking)
    cage.save()

    return cage

def add_snake(account: Owner, name: str, length: float, species: str, is_venomous: bool) -> Snake:
    snake = Snake()

    snake.species = species
    snake.length = length
    snake.name = name
    snake.is_venomous = is_venomous

    snake.save()

    # The relationship between snake and owners is managed by the snake_ids
    owner = find_account_by_email(account.email)
    owner.snake_ids.append(snake.id)
    owner.save()

    return snake

def get_snakes_for_user(user_id: bson.ObjectId) -> List[Snake]:
    owner = Owner.objects(id=user_id).first()
    snakes = Snake.objects(id__in=owner.snake_ids).all()
    
    # To run the querie-list()
    return list(snakes)

def get_available_cages(checkin: datetime.datetime, checkout: datetime.datetime, snake: Snake) -> List[Cage]:
    # Find the cages that are not booked between check-in and check-out
    # Check if the cage is a fit for the snake (size and venomous)
    min_size = snake.length / 4                 # Has to be at least 1/4 of the size of the snake
    
    # We have to make sure that the date for checking in precives/is equal to the date the guest wants to check in (same whith check out)
    query = Cage.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)
    
    # For venomous snakes we augment the previous query
    if snake.is_venomous:
        query = query.filter(allow_dangerous_snakes=True)

    # Order by price (lowest to highest) and if same price order by square meters (largest ones first)
    cages = query.order_by('price', '-square_meters')

    # We have to make sure that the check in and check out conditions on teh query are both met at the same time by one singular new booking
    # $elemmatch would do the same
    final_cages = []
    for c in cages:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_snake_id is None:
                final_cages.append(c)

    return final_cages

def book_cage(account: Owner, snake: Snake, cage: Cage, checkin: datetime.datetime, checkout: datetime.datetime) -> Cage:
    # We have to go trougth the bookings to find the available cage that meet the requirements and set it as a booking
    booking: Optional[Booking] = None

    for b in cage.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_snake_id is None:
            booking = b
            break

    # Set the parameters in Booking
    booking.guest_owner_id = account.id
    booking.guest_snake_id = snake.id
    booking.booked_date = datetime.datetime.now()

    cage.save()

def get_bookings_for_user(email: str) -> List[Booking]:
    # Find the owner
    account = find_account_by_email(email)

    # Find all the cages that have been booked by this owner, just want the bookings and the name
    booked_cages = Cage.objects() \
        .filter(bookings__guest_owner_id=account.id) \
        .only('bookings', 'name')
    
    # Function to reverse the booking.cage, cause booking  doens't have cage
    def map_cage_to_booking(cage, booking):
        booking.cage = cage
        return booking
    
    # List of the booking made by the owner
    # Take the entire list of cages that nested inside have the bookings, flatten that list with a double loop
    # Go inside each cage and each booking and show the ones the guest had booked
    bookings = [
        map_cage_to_booking(cage, booking)
        for cage in booked_cages
        for booking in cage.bookings
        if booking.guest_owner_id == account.id
    ]

    return bookings
