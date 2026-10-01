# AI Usage Log — ADA-06

**Proyecto:** ADA-06 MCP Tool Integration with GitHub  
**Estudiante:** Carlos Ruz (`XxCharlyRuzxX`)  
**Asistente IA:** Antigravity CLI / Agentic AI Pair Programmer  
**Regla de Seguridad:** Ninguna credencial, token PAT o fragmento de autenticación ha sido registrado en este documento.

---

## Registro de Interacciones Significativas

### Entrada 1 — Configuración de MCP y Definición de Permisos
- **Etapa del Flujo:** Configuración del Servidor GitHub MCP y Principio de Mínimo Privilegio.
- **Contexto y Prompt Inicial:**
  > *"Configurar el GitHub MCP Server oficial en modo READ-ONLY dentro del perfil global de Antigravity, limitando las capacidades a los toolsets repos, issues y pull_requests. No almacenar tokens en el repositorio."*
- **Acción Realizada por la IA:**
  - Inspección del archivo de configuración global `~/.gemini/config/mcp_config.json`.
  - Configuración del servidor `github-readonly` apuntando a `https://api.githubcopilot.com/mcp/` con los encabezados:
    - `Authorization: Bearer <GITHUB_PAT>`
    - `X-MCP-Readonly: true`
    - `X-MCP-Toolsets: repos,issues,pull_requests`
  - Realización del handshake MCP y verificación de las 22 herramientas retornadas por `tools/list`.
- **Decisión y Verificación Humana:**
  - El estudiante verificó que el token fuera configurado en el perfil global del sistema operativo (`~/.gemini/config/`) y no en la carpeta del proyecto ni en variables expuestas al repositorio.
  - Se confirmó que el token en GitHub cuente únicamente con permisos de lectura (`Read-only`) sobre el repositorio de la práctica, garantizando el aislamiento de privilegios.

---

### Entrada 2 — Análisis Remoto del Repositorio (Repository Understanding)
- **Etapa del Flujo:** Inspección arquitectónica del repositorio vía GitHub MCP.
- **Contexto y Prompt Inicial:**
  > *"Using the GitHub MCP server, inspect repository: XxCharlyRuzxX/ada-06-github-mcp. This is a READ-ONLY engineering analysis. Do not modify GitHub. Analyze repository purpose, main directories, entry points, components, test organization, and relevant documentation."*
- **Acción Realizada por la IA:**
  - Invocación de `get_file_contents` para recuperar `README.md`, `spec.md`, `src/main.py`, `src/api/v1/customers.py` y `src/services/customer_service.py`.
  - Invocación de `list_branches` y `list_commits` para identificar ramas activas (`main`, `feature/search-limit`).
  - Extracción y síntesis de la arquitectura por capas (API -> Service -> Repository -> Schemas).
- **Decisión y Verificación Humana:**
  - El estudiante contrastó el reporte de arquitectura con el código real del microservicio FastAPI, confirmando que la suite de pruebas unitarias e integración en `tests/` cubre la especificación original de `ada-05`.
  - Se validó que las herramientas utilizadas por el agente fueron exclusivamente de lectura pasiva.

---

### Entrada 3 — Análisis de Issue y Revisión de Pull Request (Issue / PR Analysis)
- **Etapa del Flujo:** Lectura de Issue #1 y revisión técnica del Pull Request #2.
- **Contexto y Prompt Inicial:**
  > *"Using GitHub MCP, read Issue #1 and inspect Pull Request #2 in XxCharlyRuzxX/ada-06-github-mcp. READ ONLY. Evaluate changed behavior, affected files, tests present, edge cases, and classify findings into OBSERVATION, RISK, QUESTION, POTENTIAL DEFECT."*
- **Acción Realizada por la IA:**
  - Llamada a `issue_read` con método `get` para extraer el requerimiento de limitación de resultados de búsqueda (Issue #1).
  - Llamada a `pull_request_read` con métodos `get_files` y `get_diff` para auditar los cambios implementados en PR #2.
  - La IA clasificó los hallazgos:
    - `[OBSERVATION]`: 19 archivos modificados, incluyendo 15 archivos bytecode `.pyc`.
    - `[POTENTIAL DEFECT]`: Falta de exclusión de `__pycache__/` en `.gitignore`.
    - `[RISK]`: Generación de conflictos de fusión por archivos binarios compilados en ramas de Git.
- **Decisión y Verificación Humana:**
  - El estudiante validó la discrepancia detectada por la IA sobre los archivos `.pyc` en el commit del PR, reconociendo el riesgo de versionar binarios y adoptando la recomendación para futuros commits.
  - Respecto al código de error ante `limit` inválido, el estudiante decidió deliberadamente mantener `HTTP 422` (validación de FastAPI/Pydantic) frente a la sugerencia inicial de la IA de forzar un `HTTP 400`.

---

### Entrada 4 — Revisión de Permisos y Análisis de Seguridad (Security Review)
- **Etapa del Flujo:** Auditoría de fronteras de autorización, mitigación de riesgos y Lockdown Mode.
- **Contexto y Prompt Inicial:**
  > *"Inspect the GitHub MCP capabilities available in this session. Could you create an Issue, comment on a PR, or modify files? Explain using the actual tools available. Do not execute any write action. Analyze risks and investigate Lockdown Mode."*
- **Acción Realizada por la IA:**
  - Verificación negativa de capacidades de mutación: comprobación de que el catálogo de 22 herramientas carece de `create_issue`, `add_comment`, `pull_request_write`, etc.
  - Elaboración de la matriz comparativa de las 3 capas: Autenticación, Autorización y Exposición MCP.
  - Investigación técnica de *Lockdown Mode* del GitHub MCP Server y su papel como mitigación *best-effort* frente a inyecciones de prompts indirectas.
- **Decisión y Verificación Humana:**
  - El estudiante analizó la distinción fundamental entre controles probabilísticos (filtros de contenido en lenguaje natural) y controles deterministas (fronteras de autorización con tokens de solo lectura y supresión de herramientas).
  - Se formalizó la decisión de mantener siempre el principio de defensa en profundidad en cualquier integración futura de agentes de IA con sistemas de control de versiones.
