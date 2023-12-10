from models import Company, Dev, Freebie

company = Company(name='Fake co',founding_year=1993)
session.add(company)
session.commit()

dev = Dev(name='John Doe')
session.add(dev)
session.commit()

freebie = Freebie(item_name = 'fake item',value = 9,dev_id = dev.id,company_id = company.id)

print(freebie)