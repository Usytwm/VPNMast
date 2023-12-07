from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from VPNMast.session import Session

Base = declarative_base()
session = Session()

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    correo_electronico = Column(String)
    contrasena = Column(String)
    fecha_creacion = Column(DateTime)
    ultimo_login = Column(DateTime)
    estado = Column(String)

    sesiones = relationship('SesionVPN', back_populates='usuario')
