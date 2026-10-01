# GitHub MCP Engineering Review — ADA-06

**Fecha del reporte:** 2026-10-01  
**Autor / Revisor:** Carlos Ruz (XxCharlyRuzxX) & Antigravity Agent  
**Práctica:** ADA-06 — MCP Tool Integration with GitHub (Read-Only)  
**Institución:** Facultad de Matemáticas, UADY  

---

## 1. Repository
- **Owner / Repo:** `XxCharlyRuzxX/ada-06-github-mcp`
- **Visibility:** Public
- **Branch / reference analyzed:** 
  - Rama base: `main` (commit SHA: `d227be52a2db496a75f28f09919f95d852a32ff5`)
  - Rama de funcionalidad / PR: `feature/search-limit` (commit SHA: `a5c7d54b9d8da9c51a42eb924ef90dd127ad9959`)
- **URL remota:** [https://github.com/XxCharlyRuzxX/ada-06-github-mcp](https://github.com/XxCharlyRuzxX/ada-06-github-mcp)

---

## 2. MCP Connection
- **Server:** GitHub Copilot MCP Remote Server (`https://api.githubcopilot.com/mcp/`)
- **Protocol Version:** `2024-11-05` (JSON-RPC over HTTP/SSE)
- **Mode:** READ-ONLY (`X-MCP-Readonly: "true"`)
- **Toolsets:**
  - `repos`
  - `issues`
  - `pull_requests`
- **Herramientas detectadas:** 22 herramientas activas (todas con `readOnlyHint: true`). Cero herramientas de escritura expuestas.

---

## 3. Repository Understanding
- **Purpose:** 
  Microservicio HTTP REST construido bajo la metodología *Spec-Driven Development* (Desarrollo Guiado por Especificaciones) utilizando **FastAPI**, **Python 3.12** y **pytest**. Su objetivo es proveer búsqueda en memoria de clientes mediante coincidencias parciales insensibles a mayúsculas y minúsculas sobre los campos `name` y `email`, implementando saneamiento de parámetros y validación estricta de entrada.
- **Architecture summary:**
  El diseño arquitectónico sigue una separación estricta en capas con inversión de dependencias:
  1. **Capa de Transporte / API (`src/api/v1/`):** Controladores FastAPI que definen el endpoint `GET /api/v1/customers/search`, manejan la inyección de dependencias (`Depends`) y formatean códigos de estado HTTP (200, 400, 422).
  2. **Capa de Servicios / Dominio (`src/services/`):** Contiene la lógica de negocio (`CustomerSearchService`), saneamiento de query (recorte de espacios en blanco) y validaciones de longitud (mínimo 2 caracteres, máximo 100 caracteres).
  3. **Capa de Acceso a Datos / Repositorio (`src/repositories/`):** Implementa `CustomerRepository`, almacenando en memoria una colección semilla de clientes para ejecución autónoma y rápida.
  4. **Capa de Esquemas y Excepciones (`src/schemas/`, `src/exceptions.py`):** Modelos Pydantic v2 (`Customer`, `CustomerResponse`, `ErrorResponse`) y excepciones de dominio personalizadas (`InvalidQueryException`).
- **Important files:**
  - `src/main.py`: Punto de entrada de la aplicación ASGI FastAPI con manejadores globales de excepciones.
  - `src/api/v1/customers.py`: Definición de rutas y esquemas de respuesta OpenAPI.
  - `src/services/customer_service.py`: Lógica central de filtrado y acotamiento de resultados.
  - `src/repositories/customer_repository.py`: Repositorio con datos iniciales.
  - `spec.md` & `requirements.md`: Especificación formal y requerimientos funcionales (FR-01 a FR-06) y no funcionales (NFR-01 a NFR-03).
- **Tests:**
  - `tests/test_customer_service.py`: 18 pruebas unitarias que validan el comportamiento de schemas, repositorios, coincidencias insensibles a mayúsculas y minúsculas y excepciones por queries inválidos.
  - `tests/test_api.py`: 20 pruebas de integración ejecutadas con `TestClient` de FastAPI, verificando códigos de respuesta HTTP, contratos JSON y cumplimiento de latencia $(< 150\text{ ms})$.
  - Total: **38 pruebas automatizadas passing** ($100\%$ de éxito).
- **Herramientas MCP utilizadas para esta fase:** `get_file_contents`, `list_branches`, `list_commits`.

---

## 4. Issue Analysis
- **Issue:** `#1 — Enhancement: Add limit query parameter to constrain search results`
- **URL del Issue:** [https://github.com/XxCharlyRuzxX/ada-06-github-mcp/issues/1](https://github.com/XxCharlyRuzxX/ada-06-github-mcp/issues/1)
- **Facts from Issue (Hechos observados en el Issue):**
  - El endpoint actual retornaba la totalidad de los clientes coincidentes sin mecanismo de corte o paginación.
  - En escenarios con datasets amplios, esto puede ocasionar sobrecarga de memoria y payloads de red innecesariamente grandes.
  - Se solicita incorporar un parámetro opcional `limit`: entero, con valor por defecto de 50, valor mínimo de 1 y valor máximo de 100.
  - Si un usuario consulta `limit=1`, el endpoint debe retornar únicamente un cliente aunque existan múltiples coincidencias.
- **Ambiguities (Preguntas o ambigüedades identificadas):**
  - La descripción del Issue mencionaba que valores fuera de rango debían retornar `"HTTP 400 Bad Request or validation error"`. En FastAPI, las validaciones de tipo y rango en `Query(..., ge=1, le=100)` producen automáticamente un código `HTTP 422 Unprocessable Entity`. Se optó por preservar el estándar nativo de FastAPI (HTTP 422) para errores de validación de esquema, manteniendo HTTP 400 únicamente para reglas de negocio semánticas de `q`.
- **Related requirements/spec:**
  - Extensión directa de los requerimientos **FR-01** (endpoint de búsqueda) y **NFR-02** (escalabilidad y consumo eficiente de memoria) documentados en `spec.md` y `requirements.md`.
- **Related code:**
  - `src/api/v1/customers.py`: Para exponer el nuevo parámetro en la firma del endpoint.
  - `src/services/customer_service.py`: Para aplicar la operación de rebanado (*slice*) sobre la lista filtrada de resultados.
- **Related tests:**
  - `tests/test_customer_service.py`: Adición de prueba unitaria `test_search_with_limit`.
  - `tests/test_api.py`: Adición de pruebas de integración `test_search_limit_success` y `test_search_limit_invalid_values`.
- **Herramienta MCP utilizada para esta fase:** `issue_read` (método `get`).

---

## 5. Pull Request Review
- **PR:** `#2 — feat(search): add optional limit query parameter to search endpoint`
- **URL del Pull Request:** [https://github.com/XxCharlyRuzxX/ada-06-github-mcp/pull/2](https://github.com/XxCharlyRuzxX/ada-06-github-mcp/pull/2)
- **Branch:** `feature/search-limit` hacia `main`
- **Changed behavior:**
  - El endpoint `/api/v1/customers/search` ahora acepta un parámetro `limit` opcional.
  - El servicio aplica `results[:limit]` cuando el parámetro se encuentra presente.
  - La API rechaza peticiones con `limit <= 0` o `limit > 100` con `HTTP 422`.
- **Changed files:**
  1. `src/api/v1/customers.py` (código fuente)
  2. `src/services/customer_service.py` (código fuente)
  3. `tests/test_api.py` (tests de integración)
  4. `tests/test_customer_service.py` (tests unitarios)
  5. 15 archivos binarios compilados dentro de directorios `__pycache__/`
- **Tests present for behavior:**
  - `TestCustomerSearchService.test_search_with_limit`: valida que el rebanado reduzca una colección de múltiples resultados a exactamente 1 elemento.
  - `TestCustomerSearchAPI.test_search_limit_success`: valida petición HTTP real con `?q=example.com&limit=1`.
  - `TestCustomerSearchAPI.test_search_limit_invalid_values`: valida rechazo con código 422 ante `limit=0` y `limit=101`.
- **Observations:**
  - `[OBSERVATION]` El Pull Request modifica 19 archivos en total, de los cuales 15 corresponden a archivos `.pyc` dentro de carpetas `__pycache__`.
- **Risks:**
  - `[RISK]` La inclusión de archivos binarios `.pyc` en el control de versiones provoca ruido excesivo en los diffs de revisión, aumenta el tamaño del repositorio y puede provocar inconsistencias entre desarrolladores que usen versiones menores distintas del intérprete de Python.
- **Questions:**
  - `[QUESTION]` ¿Debería documentarse el nuevo parámetro `limit` en el archivo `spec.md` formalizando un nuevo criterio `AC-08`? Se recomienda actualizar `spec.md` en el repositorio para mantener la trazabilidad viva.
- **Potential defects:**
  - `[POTENTIAL DEFECT]` Ausencia de una regla en `.gitignore` para ignorar `__pycache__/` y `*.pyc`. Esto ocasionó que una invocación indiscriminada de `git add` agregara los binarios compilados de la sesión de pruebas local al commit del PR.
- **Herramientas MCP utilizadas para esta fase:** `pull_request_read` (métodos `get`, `get_diff`, `get_files`).

---

## 6. Traceability (Trazabilidad: Issue → Spec → PR → Code → Test)

| Issue / Necesidad | Especificación / Criterio | Pull Request | Código / Archivos Modificados | Tests y Evidencia | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Issue #1**: Evitar payloads de búsqueda gigantescos limitando el número de resultados. | `spec.md` (Extensión FR-01 / NFR-02) / Criterio inferido: retorno máximo de `limit` registros (1-100). | **PR #2** (`feat(search): add optional limit query parameter`) | `src/api/v1/customers.py`<br>`src/services/customer_service.py` | `tests/test_customer_service.py` (`test_search_with_limit`)<br>`tests/test_api.py` (`test_search_limit_success`, `test_search_limit_invalid_values`) | **Covered** |
| **FR-01**: Endpoint `GET /api/v1/customers/search` | `spec.md` / `AC-01` | Rama `main` | `src/api/v1/customers.py` | `tests/test_api.py` (`test_search_success_ac01`) | **Covered** |
| **FR-02 / FR-03**: Coincidencias en nombre y correo | `spec.md` / `AC-02`, `AC-03` | Rama `main` | `src/services/customer_service.py` | `tests/test_api.py` (`test_search_matches_name_and_email_ac02`, `test_search_case_insensitive_ac03`) | **Covered** |
| **FR-04**: Atributos completos del cliente | `spec.md` / `AC-04` | Rama `main` | `src/schemas/customer.py` | `tests/test_api.py` (`test_search_item_fields_ac04`) | **Covered** |
| **FR-05**: Validación de longitud mínima y blancos | `spec.md` / `AC-05` | Rama `main` | `src/services/customer_service.py` | `tests/test_api.py` (`test_search_short_or_blank_query_ac05`) | **Covered** |
| **FR-06**: Búsqueda vacía retorna lista vacía | `spec.md` / `AC-06` | Rama `main` | `src/services/customer_service.py` | `tests/test_api.py` (`test_search_non_existent_returns_empty_list_ac06`) | **Covered** |
| **NFR-01**: Latencia inferior a 150 ms | `spec.md` / `AC-07` | Rama `main` | `src/main.py` | `tests/test_api.py` (`test_search_response_latency_nfr01`) | **Covered** |

*Nota de rigor:* Todas las relaciones indicadas entre el Issue #1 y los archivos de código fueron verificadas contractualmente a través de los diffs recuperados vía `pull_request_read`.

---

## 7. Permission Review
- **Authentication:** Cuenta de GitHub identificada como `XxCharlyRuzxX` (ID numérico: `142615933`).
- **GitHub token permissions:** Personal Access Token configurado con ámbito `repo` / fine-grained con permisos estrictos de lectura (`Contents: Read`, `Issues: Read`, `Pull requests: Read`).
- **MCP read-only:** Activado server-side mediante el header `X-MCP-Readonly: "true"`.
- **Enabled toolsets:** Exclusivamente `repos`, `issues`, `pull_requests` mediante `X-MCP-Toolsets: "repos,issues,pull_requests"`.
- **Write capabilities exposed:** **0 (Cero)**. El servidor eliminó automáticamente cualquier capacidad mutable (`create_issue`, `add_comment`, `pull_request_write`, `push_files`).

---

## 8. Security Notes
- **Credential exposure (Exposición de credenciales):**
  Las credenciales jamás deben alojarse en el directorio del proyecto ni registrarse en el árbol de Git. La configuración del servidor MCP se mantuvo aislada en el perfil global (`~/.gemini/config/mcp_config.json`), asegurando que ni `AI_USAGE_LOG.md` ni los reportes técnicos contengan tokens.
- **Prompt injection (Inyección de instrucciones en datos externos):**
  El contenido de los issues, pull requests y comentarios de GitHub debe considerarse **no confiable por diseño**. Un atacante podría redactar un issue que contenga instrucciones imperativas al agente. La arquitectura mitigó este riesgo limitando las herramientas a modo pasivo de lectura y tratando los textos de GitHub como datos a parsear, no instrucciones a obedecer.
- **Excess permissions (Exceso de privilegios):**
  Se mitigó mediante la selección explícita de toolsets (`repos,issues,pull_requests`), evitando habilitar herramientas innecesarias como administración de runners de CI/CD, gestión de webhooks o administración de secretos organizacionales.
- **Repository scope (Alcance del repositorio):**
  Para evitar confusión de contexto o filtración de información entre proyectos del usuario, cada prompt y llamada de herramienta MCP fijó explícitamente `owner: XxCharlyRuzxX` y `repo: ada-06-github-mcp`.

---

## 9. Human Review
- **What did you verify yourself? (¿Qué verificó el estudiante personalmente?):**
  1. Que la ejecución local del suite de pruebas con `pytest -v` pasara exitosamente con 38/38 pruebas en verde.
  2. Que la rama `feature/search-limit` y el PR #2 estuvieran correctamente publicados en la interfaz web de GitHub.
  3. Que el archivo de configuración global `~/.gemini/config/mcp_config.json` no fuera versionado dentro del repositorio del proyecto.
  4. Que la advertencia sobre los archivos `.pyc` en el PR #2 fuera real, identificando la necesidad de incorporar un `.gitignore` en el proyecto.
- **What AI conclusions did you reject or modify? (¿Qué conclusiones de la IA se rechazaron o modificaron?):**
  - La IA inicialmente sugirió que el código de error para `limit <= 0` debía ser `HTTP 400 Bad Request` para imitar las excepciones de negocio de `q`. Como revisor humano, se corrigió y decidió mantener `HTTP 422 Unprocessable Entity`, dado que en FastAPI las validaciones de tipo/rango numérico administradas por `Query(..., ge=1, le=100)` forman parte del estándar del validador de Pydantic/FastAPI, preservando la consistencia semántica del framework.

---

## 10. Conclusion
### What did MCP add to the engineering workflow?
El Model Context Protocol (MCP) transformó radicalmente el flujo de trabajo de ingeniería de software respecto al paradigma tradicional de copiar y pegar fragmentos de código en un chat:
1. **Acceso a Fuente de Verdad Viva y Estructurada:** En lugar de depender de transcripciones manuales propensas a errores, el agente consultó de manera determinista el árbol de directorios real, el diff unificado del PR y los metadatos oficiales del Issue directo de la API de GitHub.
2. **Trazabilidad de Extremo a Extremo:** Hizo posible correlacionar el requerimiento planteado en el Issue #1 con los archivos de código fuente y las suites de pruebas automatizadas, facilitando una verificación formal de cobertura.
3. **Gobierno y Seguridad Verificable:** Demostró que un agente de IA puede integrarse a repositorios corporativos de forma segura cuando se establecen controles server-side (`read-only`) y políticas de mínimo privilegio, garantizando que el asistente de ingeniería inspeccione y audite sin riesgo de alterar o corromper el entorno de producción.
