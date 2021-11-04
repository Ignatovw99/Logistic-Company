from app import app, db, models
from faker import Faker


@app.cli.command("create-database")
def create_database():
    # TODO: the administator should only delete and create the database tables in the PROD environment
    db.drop_all()
    db.create_all()


@app.cli.command("seed-database")
def seed_database():
    if app.config["ENV"] != "development":
        return
    
    fake = Faker()


    def generate_users():
        users = []
        for _ in range(10):
            user = models.User(first_name=fake.first_name(),
                               last_name=fake.last_name(),
                               address=fake.address(),
                               phone_number=fake.phone_number(),
                               email=fake.email(),
                               password=fake.password())
            db.session.add(user)
            users.append(user)

        db.session.commit()
        return users


    def generate_offices():
        offices = []
        for _ in range(10):
            office = models.Office(name=fake.name(), address=fake.address())
            db.session.add(office)
            offices.append(office)
        
        db.session.commit()
        return offices


    def generate_employees(users, offices):
        employees = []
        for i in range(5):
            office = None
            if i % 2 == 0:
                office = offices[i]

            employee = models.Employee(user=users[i], office=office)
            db.session.add(employee)
            employees.append(employee)
        
        db.session.commit()
        return employees


    def generate_shipments(acceptor, deliverer, users, offices):
        shipments = []

        for i in range(9):
            from_office = None
            to_office = offices[i]
            from_address = fake.address()
            to_address = None
            if i % 2 == 0:
                from_office = offices[i]
                from_address = None
                to_office = None
                to_address = fake.address()
            
            from_address = models.ShippingAddress(office=from_office, address=from_address)
            to_address = models.ShippingAddress(office=to_office, address=to_address)

            shipment = models.Shipment(weight=abs(fake.pyfloat()),
                                       from_address=from_address,
                                       to_address=to_address,
                                       sender=users[i],
                                       receiver=users[i+1],
                                       acceptor=acceptor,
                                       deliverer=deliverer)
            db.session.add(shipment)
            shipments.append(shipment)

        db.session.commit()
        return shipments


    users = generate_users()
    offices = generate_offices()
    employees = generate_employees(users, offices)
    generate_shipments(employees[0], employees[1], users, offices)