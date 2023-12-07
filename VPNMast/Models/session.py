from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from VPNMast.session import Session

Base = declarative_base()
session = Session()

class SesionVPN(Base):
    __tablename__ = 'sesiones_vpn'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    servidor_id = Column(Integer, ForeignKey('servidores_vpn.id'))
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    duracion = Column(Integer)
    ubicacion_usuario = Column(String)
    calidad_conexion = Column(String)
    datos_transmitidos = Column(Integer)

    usuario = relationship('Usuario', back_populates='sesiones')
    servidor = relationship('ServidorVPN', back_populates='sesiones')