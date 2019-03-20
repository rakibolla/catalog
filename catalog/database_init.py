from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///colleges.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Delete DepartmentName if exisitng.
session.query(DepartmentName).delete()
# Delete EmployName if exisitng.
session.query(EmployName).delete()
# Delete User if exisitng.
session.query(User).delete()

# Create sample users data
User1 = User(name="Bolla Rakesh",
             email="rakeshbolla123@gmail.com")
session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample Departments
Department1 = DepartmentName(name="CSE",
                             user_id=1)
session.add(Department1)
session.commit()

Department2 = DepartmentName(name="ECE",
                             user_id=1)
session.add(Department2)
session.commit

Department3 = DepartmentName(name="MECH",
                             user_id=1)
session.add(Department3)
session.commit()

Department4 = DepartmentName(name="EEE",
                             user_id=1)
session.add(Department4)
session.commit()

Department5 = DepartmentName(name="CIVIL",
                             user_id=1)
session.add(Department5)
session.commit()

Department6 = DepartmentName(name="MCA",
                             user_id=1)
session.add(Department6)
session.commit()

# Popular a employs
# Using different users for employs
Employ1 = EmployName(name="Subash",
                     description="Fully Experienced",
                     salary="45000",
                     feedback="Good",
                     date=datetime.datetime.now(),
                     departmentnameid=1,
                     user_id=1)
session.add(Employ1)
session.commit()

Employ2 = EmployName(name="Ramana Reddy",
                     description="Junior Professor ",
                     salary="15000",
                     feedback="Very Good",
                     date=datetime.datetime.now(),
                     departmentnameid=2,
                     user_id=1)
session.add(Employ2)
session.commit()

Employ3 = EmployName(name="Sandhya Subramanyam",
                     description="Senior Professor",
                     salary="30000",
                     feedback="Good",
                     date=datetime.datetime.now(),
                     departmentnameid=3,
                     user_id=1)
session.add(Employ3)
session.commit()

Employ4 = EmployName(name="Siva Kalyan Murthy",
                     description="Principal",
                     salary="250000",
                     feedback="Good",
                     date=datetime.datetime.now(),
                     departmentnameid=4,
                     user_id=1)
session.add(Employ4)
session.commit()

Employ5 = EmployName(name="Rama Raju",
                     description="Department Head",
                     salary="100000",
                     feedback="Excellent",
                     date=datetime.datetime.now(),
                     departmentnameid=5,
                     user_id=1)
session.add(Employ5)
session.commit()

Employ6 = EmployName(name="Kalyan Srinivas",
                     description="Department Head",
                     salary="100000",
                     feedback="Excellent",
                     date=datetime.datetime.now(),
                     departmentnameid=6,
                     user_id=1)
session.add(Employ6)
session.commit()

print("Your database has been inserted!")
