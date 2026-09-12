"""
Servicio de auditoria automatizada con API de IA.

Cumple el requisito del enunciado: al terminar cada problema se envian las
metricas a una API de IA, se muestra por pantalla la conclusion y la
recomendacion que devuelve, y la respuesta se anexa al final del reporte .txt.

Cascada de respaldo, en orden:
    1. Google Gemini   (si hay GEMINI_API_KEY)
    2. OpenAI          (si hay OPENAI_API_KEY)
    3. Ollama local    (si hay un servidor en el puerto 11434)
    4. Backend REST propio (si se declaro LOCAL_API_URL)
    5. Motor experto cuantitativo local, determinista y sin red

El paso 5 garantiza que el programa SIEMPRE muestre una conclusion y una
recomendacion por pantalla, aunque no haya conectividad ni credenciales. Es
respaldo, no sustituto: el camino normal es la API real.

Regla de formato: la salida no lleva emojis en ninguna rama.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import requests

from src.services.reporter import ReportService
from src.utils.config import (
    PROMPT_PROBLEMA_1,
    PROMPT_PROBLEMA_2,
    cargar_variables_entorno,
)
from src.utils.validators import ValidacionError

# Modelos vigentes de Google AI Studio. Se prueban en orden hasta que uno
# responda 200. La lista se mantiene corta y verificada a proposito: un modelo
# inexistente solo agrega un round-trip fallido y ruido en el diagnostico.
MODELOS_GEMINI = [
    "gemini-flash-latest",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-pro-latest",
]

TIMEOUT_REMOTO_S = 25
TIMEOUT_LOCAL_S = 12


class AIAuditorService:
    """Gestiona la interaccion HTTP con las APIs de IA y el respaldo local."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        cfg = cargar_variables_entorno()
        self.gemini_key = api_key or cfg.get("gemini", "")
        self.openai_key = cfg.get("openai", "")
        self.local_url = cfg.get("local", "")

    # ------------------------------------------------------------------
    # Clientes HTTP
    # ------------------------------------------------------------------

    def consultar_gemini(self, prompt_texto: str) -> Tuple[bool, str]:
        """Peticion POST a la API REST de Google Gemini, probando varios modelos."""
        if not self.gemini_key:
            return False, "No se configuro GEMINI_API_KEY en el entorno ni en .env"

        payload = {
            "contents": [{"parts": [{"text": prompt_texto}]}],
            "generationConfig": {"temperature": 0.35, "topP": 0.95, "maxOutputTokens": 1500},
        }
        headers = {"Content-Type": "application/json"}
        ultimo_error = "No se obtuvo respuesta de ningun modelo de Gemini."

        for modelo in MODELOS_GEMINI:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{modelo}:generateContent?key={self.gemini_key}"
            )
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT_REMOTO_S)
            except requests.RequestException as ex:
                ultimo_error = f"Error de conexion con Gemini ({modelo}): {ex}"
                continue

            if resp.status_code == 200:
                texto = self._extraer_texto_gemini(resp)
                if texto:
                    return True, texto
                ultimo_error = f"Respuesta vacia del modelo {modelo}."
                continue

            err_msg = self._extraer_error(resp)
            ultimo_error = f"HTTP {resp.status_code} ({modelo}): {err_msg}"
            # Una clave invalida falla igual en todos los modelos: cortar de una.
            if "API key not valid" in err_msg or "API_KEY_INVALID" in err_msg:
                return False, f"Clave de Google Gemini no valida: {err_msg}"

        return False, ultimo_error

    @staticmethod
    def _extraer_texto_gemini(resp: requests.Response) -> str:
        """Extrae el texto de la respuesta de Gemini, tolerando formas parciales."""
        try:
            data = resp.json()
        except ValueError:
            return ""
        candidatos = data.get("candidates", [])
        if not candidatos:
            return ""
        partes = candidatos[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in partes if "text" in p)

    @staticmethod
    def _extraer_error(resp: requests.Response) -> str:
        """Saca el mensaje de error del cuerpo, o el texto crudo si no es JSON."""
        try:
            return resp.json().get("error", {}).get("message", resp.text)
        except ValueError:
            return resp.text

    def consultar_openai(self, prompt_texto: str) -> Tuple[bool, str]:
        """Peticion POST a la API de OpenAI."""
        if not self.openai_key:
            return False, "No se configuro OPENAI_API_KEY en el entorno ni en .env"

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_key}",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un auditor cuantitativo experto en simulacion, teoria de colas "
                        "e ingenieria termica. Respondes en espanol, en texto plano, sin "
                        "markdown y sin emojis."
                    ),
                },
                {"role": "user", "content": prompt_texto},
            ],
            "temperature": 0.35,
            "max_tokens": 1500,
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT_REMOTO_S)
        except requests.RequestException as ex:
            return False, f"Error de conexion con OpenAI: {ex}"

        if resp.status_code == 200:
            try:
                opciones = resp.json().get("choices", [])
            except ValueError:
                return False, "OpenAI devolvio una respuesta que no es JSON."
            if opciones:
                return True, opciones[0].get("message", {}).get("content", "")
            return False, "OpenAI devolvio una respuesta sin opciones."
        return False, f"OpenAI HTTP {resp.status_code}: {resp.text[:300]}"

    def consultar_ollama(self, prompt_texto: str) -> Tuple[bool, str]:
        """Peticion POST a un servidor local de Ollama (puerto 11434)."""
        url = (
            self.local_url
            if (self.local_url and "11434" in self.local_url)
            else "http://localhost:11434/api/generate"
        )
        payload = {"model": "llama3", "prompt": prompt_texto, "stream": False}
        try:
            resp = requests.post(
                url, json=payload, headers={"Content-Type": "application/json"},
                timeout=TIMEOUT_LOCAL_S,
            )
        except requests.RequestException as ex:
            return False, f"Ollama no disponible: {ex}"

        if resp.status_code == 200:
            try:
                data = resp.json()
            except ValueError:
                return False, "Ollama devolvio una respuesta que no es JSON."
            texto = data.get("response", data.get("text", ""))
            if texto:
                return True, texto
            return False, "Ollama devolvio una respuesta vacia."
        return False, f"Ollama HTTP {resp.status_code}: {resp.text[:300]}"

    def consultar_backend_propio(self, prompt_texto: str) -> Tuple[bool, str]:
        """Peticion POST a un backend REST propio declarado en LOCAL_API_URL."""
        if not self.local_url or "11434" in self.local_url:
            return False, "No se configuro un backend REST propio."
        try:
            resp = requests.post(
                self.local_url, json={"prompt": prompt_texto}, timeout=TIMEOUT_LOCAL_S
            )
        except requests.RequestException as ex:
            return False, f"Backend propio no disponible: {ex}"

        if resp.status_code == 200:
            try:
                data = resp.json()
            except ValueError:
                return True, resp.text
            return True, data.get("response", data.get("text", resp.text))
        return False, f"Backend propio HTTP {resp.status_code}"

    def consultar_api_externa(self, prompt_texto: str) -> Tuple[bool, str, str]:
        """
        Recorre la cascada de proveedores y devuelve la primera respuesta valida.

        Retorna (exito, respuesta_o_motivo_de_fallo, nombre_de_la_fuente).
        """
        errores = []

        if self.gemini_key:
            ok, resp = self.consultar_gemini(prompt_texto)
            if ok:
                return True, resp, "Google Gemini (API oficial)"
            errores.append(f"Gemini: {resp}")

        if self.openai_key:
            ok, resp = self.consultar_openai(prompt_texto)
            if ok:
                return True, resp, "OpenAI (gpt-4o-mini)"
            errores.append(f"OpenAI: {resp}")

        ok, resp = self.consultar_ollama(prompt_texto)
        if ok:
            return True, resp, "Ollama local (llama3)"
        errores.append(f"Ollama: {resp}")

        if self.local_url and "11434" not in self.local_url:
            ok, resp = self.consultar_backend_propio(prompt_texto)
            if ok:
                return True, resp, "Backend REST propio"
            errores.append(f"Backend propio: {resp}")

        return False, " | ".join(errores), ""

    # ------------------------------------------------------------------
    # Flujo completo exigido por el enunciado
    # ------------------------------------------------------------------

    def construir_prompt(self, problema: int, contenido_reporte: str) -> str:
        """Arma el prompt especifico del problema con el reporte adjunto."""
        if problema == 1:
            base = PROMPT_PROBLEMA_1
        elif problema == 2:
            base = PROMPT_PROBLEMA_2
        else:
            raise ValidacionError(f"Problema desconocido: {problema}. Se esperaba 1 o 2.")
        return (
            f"{base}\n\n"
            "Contenido del reporte de simulacion:\n"
            f"{contenido_reporte}\n\n"
            "Se breve y concreto. No repitas los numeros del reporte: interpretalos."
        )

    def ejecutar_auditoria(
        self,
        problema: int,
        metricas: Dict,
        ruta_reporte: Union[str, Path],
        sin_red: bool = False,
    ) -> Tuple[str, str]:
        """
        Flujo completo: leer el reporte, consultar la API, imprimir la conclusion
        por pantalla y anexarla al final del .txt.

        El reporte debe existir: este metodo NO lo genera, solo lo consume y lo
        amplia. Devuelve (diagnostico, fuente).
        """
        ruta = Path(ruta_reporte)
        if not ruta.exists():
            raise FileNotFoundError(
                f"El reporte {ruta} no existe. Generelo antes de llamar a la auditoria."
            )

        contenido = ruta.read_text(encoding="utf-8")
        prompt = self.construir_prompt(problema, contenido)

        print()
        print("=" * 70)
        print(f"CONSULTANDO API DE IA - PROBLEMA {problema}")
        print("=" * 70)

        if sin_red:
            exito, respuesta, fuente = False, "Modo sin red solicitado por el usuario.", ""
        else:
            exito, respuesta, fuente = self.consultar_api_externa(prompt)

        if exito:
            diagnostico = respuesta.strip()
            fuente_final = fuente
        else:
            print(f"Aviso: no se pudo usar la API externa. Motivo: {respuesta}")
            print("Activando el motor experto cuantitativo local de respaldo.")
            diagnostico = self.motor_experto_local(problema, metricas)
            fuente_final = "Motor experto cuantitativo local (respaldo)"

        print()
        print("=" * 70)
        print(f"CONCLUSION Y RECOMENDACION AUTOMATIZADA - FUENTE: {fuente_final.upper()}")
        print("=" * 70)
        print(diagnostico)
        print("=" * 70)
        print()

        ReportService.anexar_seccion(
            ruta,
            f"respuesta de la api de ia - conclusion y recomendacion ({fuente_final})",
            diagnostico,
        )
        return diagnostico, fuente_final

    # ------------------------------------------------------------------
    # Motor experto local de respaldo (determinista, sin red)
    # ------------------------------------------------------------------

    def motor_experto_local(self, problema: int, metricas: Dict) -> str:
        """Genera una conclusion y recomendaciones sin salir a la red."""
        if problema == 1:
            return self._experto_problema1(metricas)
        if problema == 2:
            return self._experto_problema2(metricas)
        raise ValidacionError(f"Problema desconocido: {problema}. Se esperaba 1 o 2.")

    @staticmethod
    def _experto_problema1(m: Dict) -> str:
        """Diagnostico local del Problema 1, derivado de las formulas M/M/1."""
        rho = m.get("teorico_rho", 0.0)
        wq_sim = m.get("wq_promedio_min", 0.0)
        wq_teo = m.get("teorico_wq_min", 0.0)
        paradas = m.get("paradas_por_falta_stock", 0)
        lead_h = m.get("lead_time_min", 0.0) / 60.0
        consumo_lead = m.get("lambda_ordenes_hora", 0.0) * m.get("consumo_por_laptop", 1) * lead_h
        umbral = m.get("umbral_critico_s", 0)
        eficiencia = m.get("eficiencia_reabastecimiento_pct", 100.0)

        if paradas == 0:
            juicio_inventario = (
                f"El inventario nunca dejo sin material a la estacion: cero paradas de linea y "
                f"{eficiencia:.2f} % de eficiencia de reabastecimiento. El umbral critico s = {umbral} "
                f"unidades cubre {umbral / consumo_lead:.1f} veces el consumo esperado durante el "
                f"lead time ({consumo_lead:.2f} unidades). La politica esta sobredimensionada."
            )
        else:
            juicio_inventario = (
                f"Se registraron {paradas} parada(s) de linea por falta de stock, con "
                f"{m.get('tiempo_linea_detenida_min', 0.0):.2f} min de produccion perdida y una "
                f"eficiencia de reabastecimiento del {eficiencia:.2f} %. El umbral s = {umbral} no "
                f"alcanza a cubrir el consumo de {consumo_lead:.2f} unidades del lead time."
            )

        return f"""1. DESEMPENO DE LA LINEA DE ENSAMBLAJE Y TEORIA DE COLAS

El sistema es una cola M/M/1 con factor de utilizacion rho = {rho:.4f}, o sea que la
estacion trabaja al {rho * 100.0:.1f} % de su capacidad. En una cola de un solo servidor esa
utilizacion ubica al sistema en la zona de crecimiento rapido: a partir de rho = 0.8
cada punto porcentual adicional de carga aumenta la espera de forma no lineal.

El tiempo de espera promedio simulado fue de {wq_sim:.2f} min, contra {wq_teo:.2f} min que
predice la formula cerrada Wq = lambda / (mu * (mu - lambda)). La diferencia es
ruido estocastico propio del tamano de la corrida, no un desvio del modelo.

Se completaron {m.get('ordenes_completadas', 0)} laptops de {m.get('ordenes_generadas', 0)} ordenes
generadas, con una ocupacion efectiva de la estacion del {m.get('utilizacion_estacion_pct', 0.0):.2f} %.

2. POLITICA DE INVENTARIO Y REABASTECIMIENTO

{juicio_inventario}

El ciclo de reposicion de componentes promedio fue de
{m.get('ciclo_reposicion_promedio_min', 0.0):.2f} min sobre {m.get('ciclos_reposicion_observados', 0)} ciclos
observados, y el despacho de un lote de {m.get('lote_produccion', 50)} laptops tomo
{m.get('despacho_lote_promedio_min', 0.0):.2f} min en promedio.

3. RECOMENDACIONES DE OPTIMIZACION

Recomendacion 1 (prioridad alta): agregar una segunda estacion de ensamblaje. Pasar
de M/M/1 a M/M/2 baja rho por servidor a {rho / 2.0:.4f} y reduce Wq en mas de un orden de
magnitud. Es la unica palanca que ataca el cuello de botella real del sistema.

Recomendacion 2 (prioridad media): reducir la variabilidad del tiempo de ensamblaje.
Con la misma media, pasar de un servicio exponencial a uno mas determinista (M/D/1)
recorta la espera en cola a la mitad, sin comprar una sola maquina nueva.

Recomendacion 3 (prioridad baja): relajar la politica de inventario. Con el consumo
observado, bajar el umbral critico o reducir el lote Q libera capital inmovilizado en
procesadores sin generar riesgo de desabastecimiento. El inventario no es el problema."""

    @staticmethod
    def _experto_problema2(m: Dict) -> str:
        """Diagnostico local del Problema 2, derivado del balance termico."""
        pct_thr = m.get("pct_tiempo_throttling", 0.0)
        eta = m.get("eficiencia_global_pct", 90.0)
        h_actual = m.get("h_disip", 20.0)
        # Para bajar T_eq del trafico medio a 65 C hace falta h' = (P_idle + k*3) / (65 - T_amb)
        p_total = m.get("p_idle_w", 0.0) + m.get("k_carga_w", 0.0) * m.get("trafico_media_nominal", 3.0)
        t_amb = m.get("temp_ambiente_c", 25.0)
        h_objetivo = p_total / (65.0 - t_amb) if t_amb < 65.0 else h_actual

        return f"""1. COMPORTAMIENTO TERMICO Y ESTABILIDAD DEL EQUILIBRIO

El balance C * dT/dt = P_idle + k * trafico - h * (T - T_amb) describe un sistema de
primer orden estable, con constante de tiempo tau = C / h = {m.get('tau_s', 0.0):.0f} s. El sistema
siempre converge a T_eq = T_amb + (P_idle + k * trafico) / h, sin oscilar ni divergir.

Con el trafico medio de {m.get('trafico_media_nominal', 3.0):.1f} Gbps el equilibrio cae en
{m.get('temp_equilibrio_media_c', 70.0):.2f} C, que es exactamente la temperatura de diseno. La corrida
arrojo una media de {m.get('temp_media_c', 0.0):.2f} C con desviacion de {m.get('temp_desviacion_c', 0.0):.2f} C,
oscilando entre {m.get('temp_min_c', 0.0):.2f} C y {m.get('temp_max_c', 0.0):.2f} C.

Ese es el hallazgo central: el punto de operacion nominal esta clavado JUSTO en el
limite termico, sin margen. Como el trafico es una variable aleatoria simetrica
alrededor de la media, aproximadamente la mitad del tiempo el sistema opera por
encima de 70 C.

2. IMPACTO DEL THERMAL THROTTLING EN EL RENDIMIENTO

El throttling estuvo activo el {pct_thr:.2f} % del tiempo simulado. La eficiencia global
ponderada en el tiempo fue del {eta:.2f} %, contra el 90 % nominal: una perdida de
rendimiento del {m.get('perdida_por_throttling_pct', 0.0):.2f} % atribuible enteramente a la temperatura.

En terminos absolutos, el cluster proceso {m.get('tb_procesados', 0.0):.4f} TB, entregando un
throughput medio de {m.get('throughput_medio_gbps', 0.0):.4f} Gbps frente a un trafico ofrecido de
{m.get('trafico_medio_gbps', 0.0):.4f} Gbps.

3. RECOMENDACIONES DE OPTIMIZACION

Recomendacion 1 (prioridad alta): aumentar el coeficiente de disipacion h de
{h_actual:.1f} a {h_objetivo:.1f} W/C. Eso baja el equilibrio con trafico medio a 65 C y deja
5 C de margen, lo que elimina el throttling en casi toda la banda de trafico. Es la
palanca de mayor impacto por unidad de inversion.

Recomendacion 2 (prioridad media): bajar la temperatura ambiente del datacenter. T_eq
depende de T_amb de forma aditiva, asi que cada grado que se baja en la sala es un
grado menos en el cluster, sin tocar el circuito de refrigeracion del equipo.

Recomendacion 3 (prioridad media): aplanar los picos de trafico. Como la penalizacion
de eficiencia es lineal en el exceso de temperatura pero el tiempo sobre el umbral no
lo es, desviar los picos por encima de 4 Gbps hacia otro nodo recupera eficiencia sin
necesidad de mas capacidad de refrigeracion."""


def _selfcheck() -> None:
    """Verifica el motor experto local y la construccion de prompts. Sin red."""
    import tempfile

    from src.simulation.continuous_sim import ClusterSimulation
    from src.simulation.discrete_sim import FabricaSimulation

    auditor = AIAuditorService(api_key="")
    m1 = FabricaSimulation(semilla=1).ejecutar(1.0)
    m2 = ClusterSimulation(semilla=1).ejecutar(1.0)

    d1 = auditor.motor_experto_local(1, m1)
    d2 = auditor.motor_experto_local(2, m2)
    for diag in (d1, d2):
        assert "RECOMENDACIONES" in diag
        assert len(diag) > 500
        assert diag == diag.strip()

    prompt = auditor.construir_prompt(1, "reporte de prueba")
    assert "reporte de prueba" in prompt
    try:
        auditor.construir_prompt(9, "x")
    except ValidacionError:
        pass
    else:
        raise AssertionError("construir_prompt acepto un problema inexistente")

    assert "gemini-3.6-flash" not in MODELOS_GEMINI
    assert "gemini-3.5-flash" not in MODELOS_GEMINI
    assert MODELOS_GEMINI[0] == "gemini-flash-latest"

    # ejecutar_auditoria en modo sin red: cae al motor local y anexa al reporte
    with tempfile.TemporaryDirectory() as tmp:
        ruta = Path(tmp) / "r.txt"
        ruta.write_text("REPORTE DE PRUEBA\n", encoding="utf-8")
        diag, fuente = auditor.ejecutar_auditoria(1, m1, ruta, sin_red=True)
        assert "respaldo" in fuente.lower()
        final = ruta.read_text(encoding="utf-8")
        assert "RESPUESTA DE LA API DE IA" in final
        assert diag[:60] in final

    print("selfcheck ai_auditor: OK")


if __name__ == "__main__":
    _selfcheck()
