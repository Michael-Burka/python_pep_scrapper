import requests
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL of the Python Enhancement Proposals site
PEP_URL = 'https://peps.python.org/'

# Create the base class for models
Base = declarative_base()

# Define the Pep model
class Pep(Base):
    __tablename__ = 'pep'
    id = Column(Integer, primary_key=True)
    type_status = Column(String(2))
    number = Column(Integer, unique=True)
    title = Column(String(200))
    authors = Column(String(200))

# Create the database engine and bind it to the models
engine = create_engine('sqlite:///pep_sqlite.db')
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)

def main():
    session = Session()

    # Load the page
    response = requests.get(PEP_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the section with the numerical index
    numerical_index_section = soup.find('section', id='numerical-index')
    # Find the table in this section
    pep_table = numerical_index_section.find('table', class_='pep-zero-table')
    # Skip the table header and iterate over the rows
    rows = pep_table.find_all('tr')[1:]

    # Extract and insert data into the database
    for row in rows:
        cols = row.find_all('td')
        if cols:
            status_abbr = cols[0].find('abbr')
            type_status = status_abbr.text.strip() if status_abbr else None
            pep_number = int(cols[1].text.strip())
            pep_title = cols[2].text.strip()
            authors = cols[3].text.strip()

            # Create and add a Pep object
            pep = Pep(type_status=type_status, number=pep_number, title=pep_title, authors=authors)
            session.add(pep)

    # Commit changes and close the session
    session.commit()
    session.close()

if __name__ == '__main__':
    main()
