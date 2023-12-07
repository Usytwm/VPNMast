from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Crear un motor que almacena los datos en el archivo VPNMast.db
engine = create_engine('sqlite:///VPNMast.db')

# Crear una fábrica de sesiones vinculada al motor
Session = sessionmaker(bind=engine)
