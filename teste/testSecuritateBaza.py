from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_sql_injection_vulnerability():
    db_uri = 'mysql://root:password@localhost/efactura'
    engine = create_engine(db_uri)

    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # input vulnerabil as per doc
        input_username = "' OR 1=1 --"

        # paramtrizare sql injection
        query = text("select * from users where username = :username")
        
        result = session.execute(query, {'username': input_username})
        data = result.fetchall()
        print(data)
        # daca afiseaza ceva in interfata e vulnerabila, daca nu afiseaza, nu e
        if data:
            print("vulnerabil la SQL injection")
        else:
            print("NU e vulnerabil la SQL injection")

    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    test_sql_injection_vulnerability()
