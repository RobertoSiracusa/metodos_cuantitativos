"""Tests de las entidades de red: Paquete, Servidor, Enlace y Cluster."""

import pytest

from src.core.network_entities import CapacidadExcedidaError, Enlace, Paquete, Servidor
from src.core.red import Cluster
from src.utils.validators import ErrorValidacion


def _paquete(id_: str, requerimiento: int, prioridad: int = 5, destino_cluster: str = "C1") -> Paquete:
    return Paquete(id=id_, requerimiento=requerimiento, prioridad=prioridad, destino_cluster=destino_cluster)


class TestPaquete:
    def test_paquete_valido(self):
        p = _paquete("P1", 5, 7)
        assert p.id == "P1"
        assert p.requerimiento == 5
        assert p.prioridad == 7

    def test_requerimiento_invalido_lanza_error(self):
        with pytest.raises(ErrorValidacion):
            _paquete("P1", 0)
        with pytest.raises(ErrorValidacion):
            _paquete("P1", -3)

    def test_prioridad_fuera_de_rango_lanza_error(self):
        with pytest.raises(ErrorValidacion):
            _paquete("P1", 5, prioridad=0)
        with pytest.raises(ErrorValidacion):
            _paquete("P1", 5, prioridad=11)

    def test_t_creacion_negativa_lanza_error(self):
        with pytest.raises(ErrorValidacion):
            Paquete(id="P1", requerimiento=5, prioridad=5, destino_cluster="C1", t_creacion=-1.0)


class TestServidor:
    def test_asignar_mueve_de_cola_a_en_proceso(self):
        s = Servidor(id="S1", capacidad=10, tasa_servicio=2.0, posicion=(0, 0))
        p1 = _paquete("P1", 4)
        s.encolar(p1)
        s.asignar([p1])
        assert p1 in s.en_proceso
        assert p1 not in s.cola
        assert s.carga_actual == 4
        assert s.capacidad_libre == 6

    def test_asignar_paquete_no_en_cola_lanza_value_error_y_no_mueve_nada(self):
        s = Servidor(id="S1", capacidad=10, tasa_servicio=2.0, posicion=(0, 0))
        p1 = _paquete("P1", 4)
        p2 = _paquete("P2", 3)
        s.encolar(p1)
        with pytest.raises(ValueError):
            s.asignar([p1, p2])
        assert s.cola == (p1,)
        assert s.en_proceso == ()

    def test_asignar_que_excede_capacidad_es_atomico(self):
        s = Servidor(id="S1", capacidad=10, tasa_servicio=2.0, posicion=(0, 0))
        p1 = _paquete("P1", 6)
        p2 = _paquete("P2", 6)
        s.encolar(p1)
        s.encolar(p2)
        with pytest.raises(CapacidadExcedidaError):
            s.asignar([p1, p2])
        assert s.cola == (p1, p2)
        assert s.en_proceso == ()

    def test_liberar_quita_de_en_proceso(self):
        s = Servidor(id="S1", capacidad=10, tasa_servicio=2.0, posicion=(0, 0))
        p1 = _paquete("P1", 4)
        s.encolar(p1)
        s.asignar([p1])
        s.liberar("P1")
        assert s.en_proceso == ()
        assert s.capacidad_libre == 10

    def test_liberar_id_inexistente_lanza_key_error(self):
        s = Servidor(id="S1", capacidad=10, tasa_servicio=2.0, posicion=(0, 0))
        with pytest.raises(KeyError):
            s.liberar("NO_EXISTE")

    def test_tiempo_servicio_es_requerimiento_sobre_tasa(self):
        s = Servidor(id="S1", capacidad=10, tasa_servicio=2.0, posicion=(0, 0))
        p1 = _paquete("P1", 6)
        assert s.tiempo_servicio(p1) == pytest.approx(3.0)


class TestEnlace:
    def test_ocupacion_topea_en_0_95(self):
        e = Enlace(origen_id="A", destino_id="B", latencia_base=2.0, capacidad=10)
        for i in range(20):
            e.entrar(_paquete(f"P{i}", 1))
        assert e.ocupacion == pytest.approx(0.95)

    def test_salir_sin_haber_entrado_lanza_key_error(self):
        e = Enlace(origen_id="A", destino_id="B", latencia_base=2.0, capacidad=10)
        with pytest.raises(KeyError):
            e.salir(_paquete("P1", 1))

    def test_costo_actual_crece_con_la_congestion(self):
        e = Enlace(origen_id="A", destino_id="B", latencia_base=4.0, capacidad=10)
        assert e.costo_actual() == pytest.approx(4.0)
        for i in range(5):
            e.entrar(_paquete(f"P{i}", 1))
        assert e.costo_actual() == pytest.approx(8.0)


class TestCluster:
    def test_demanda_ignora_servidores_caidos(self):
        s1 = Servidor(id="S1", capacidad=10, tasa_servicio=2.0, posicion=(0, 0))
        s2 = Servidor(id="S2", capacidad=10, tasa_servicio=2.0, posicion=(0, 0))
        p1 = _paquete("P1", 4)
        p2 = _paquete("P2", 5)
        s1.encolar(p1)
        s1.asignar([p1])
        s2.encolar(p2)

        cluster = Cluster(id="C1", tor_id="T1", servidores=[s1, s2])
        assert cluster.demanda() == pytest.approx(9.0)

        s2.fallar()
        assert cluster.demanda() == pytest.approx(4.0)

    def test_energia_asignada_rechaza_negativos(self):
        s1 = Servidor(id="S1", capacidad=10, tasa_servicio=2.0, posicion=(0, 0))
        cluster = Cluster(id="C1", tor_id="T1", servidores=[s1])
        assert cluster.energia_asignada == 0.0
        cluster.energia_asignada = 5.0
        assert cluster.energia_asignada == 5.0
        with pytest.raises(ErrorValidacion):
            cluster.energia_asignada = -1.0
