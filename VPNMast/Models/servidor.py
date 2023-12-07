from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from VPNMast.session import Session

Base = declarative_base()
session = Session()

class ServidorVPN(Base):
    __tablename__ = 'servidores_vpn'

    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    ubicacion = Column(String)
    direccion_ip = Column(String)
    capacidad = Column(Integer)
    uso_actual = Column(Integer)
    estado = Column(String)

    sesiones = relationship('SesionVPN', back_populates='servidor')
