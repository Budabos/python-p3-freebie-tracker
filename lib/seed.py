#!/usr/bin/env python3

# Script goes here!
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create the engine and session
engine = create_engine('sqlite:///freebies.db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Define the models
class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    founding_year = Column(Integer)

    devs = relationship("Dev", secondary='company_devs', backref="companies")
    freebies = relationship("Freebie", backref="company")

    def give_freebie(self, dev, item_name, value):
        freebie = Freebie(dev=dev, company=self, item_name=item_name, value=value)
        session.add(freebie)
        session.commit()

    @classmethod
    def oldest_company(cls):
        return session.query(cls).order_by(cls.founding_year).first()


class Dev(Base):
    __tablename__ = 'devs'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    companies = relationship("Company", secondary='company_devs', backref="devs")
    freebies = relationship("Freebie", backref="dev")

    def received_one(self, item_name):
        return any(freebie.item_name == item_name for freebie in self.freebies)

    def give_away(self, dev, freebie):
        if freebie.dev == self:
            freebie.dev = dev
            session.commit()


class Freebie(Base):
    __tablename__ = 'freebies'
    id = Column(Integer, primary_key=True)
    item_name = Column(String)
    value = Column(Integer)
    dev_id = Column(Integer, ForeignKey('devs.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))

    dev = relationship("Dev", backref="freebies")
    company = relationship("Company", backref="freebies")

    def print_details(self):
        return f"{self.dev.name} owns a {self.item_name} from {self.company.name}"


company_devs = Table('company_devs', Base.metadata,
    Column('company_id', Integer, ForeignKey('companies.id'), primary_key=True),
    Column('dev_id', Integer, ForeignKey('devs.id'), primary_key=True)
)

# Create the database tables
Base.metadata.create_all(engine)

# Seed data
def seed_data():
    company1 = Company(name="Company 1", founding_year=2000)
    company2 = Company(name="Company 2", founding_year=2010)
    dev1 = Dev(name="Dev 1")
    dev2 = Dev(name="Dev 2")

    company1.devs.append(dev1)
    company1.devs.append(dev2)

    session.add_all([company1, company2, dev1, dev2])
    session.commit()

seed_data()

# Test the methods
print("---- Company ----")
company = session.query(Company).first()
print(f"Company: {company.name}")
print("Devs:")
for dev in company.devs:
    print(f"- {dev.name}")
print("Freebies:")
for freebie in company.freebies:
    print(f"- {freebie.item_name}")
print("Give Freebie:")
company.give_freebie(company.devs[0], "T-shirt", 10)
for freebie in company.freebies:
    print(f"- {freebie.item_name} (Dev: {freebie.dev.name})")
print("Oldest Company:")
oldest_company = Company.oldest_company()
print(f"Oldest Company: {oldest_company.name}")

print("---- Dev ----")
dev = session.query(Dev).first()
print(f"Dev: {dev.name}")
print("Companies:")
for company in dev.companies:
    print(f"- {company.name}")
print("Freebies:")
for freebie in dev.freebies:
    print(f"- {freebie.item_name}")
print("Received One:")
print(f"Received T-shirt: {dev.received_one('T-shirt')}")
print(f"Received Hat: {dev.received_one('Hat')}")
print("Give Away:")
dev2 = session.query(Dev).filter(Dev.name == "Dev 2").first()
freebie = dev.freebies[0]
dev.give_away(dev2, freebie)
print(f"Freebie Dev: {freebie.dev.name}")

print("---- Freebie ----")
freebie = session.query(Freebie).first()
print(f"Freebie: {freebie.item_name}")
print(f"Dev: {freebie.dev.name}")
print(f"Company: {freebie.company.name}")
print("Print Details:")
print(freebie.print_details())
