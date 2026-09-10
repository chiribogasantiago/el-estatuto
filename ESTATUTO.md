# El Estatuto — 1.0.0

Edición del Dueño. Este documento establece la norma de la casa: cómo se ve, se nombra, se
documenta, se verifica y se comunica cada framework —la Generala que gobierna y cada empleado que
propone—. Las cláusulas llevan identificadores `E-n.m`. Una cláusula marcada **[gate]** la hace
cumplir el control del mismo identificador en `estatuto gate`; las demás obligan por revisión y por
la directiva para agentes. La versión normativa técnica, en inglés, es `docs/standard/STANDARD.md`;
ambas ediciones llevan los mismos identificadores y el propio gate verifica que no se separen.

Vocabulario: *debe* es un requisito; *debería* es una recomendación cuya omisión exige una razón
registrada; *puede* es un permiso.

## E-0 Propósito, alcance y autoridad

- **E-0.1 Alcance.** El Estatuto gobierna la *forma*: la figura del repositorio, la documentación,
  el nombrado, las herramientas, la verificación, el protocolo y la disciplina del cambio. Nunca
  gobierna el *fondo*: lo que un framework es, promete y rechaza pertenece a su propio Núcleo
  Rector.
- **E-0.2 Roles.** Un repositorio declara un solo rol: `governor` (La Generala: dueña de misiones,
  concesiones, presupuestos y aceptación), `employee` (un framework con un oficio, que propone y
  nunca acepta) o `standard` (únicamente este repositorio). Todo rol es un framework: autocontenido,
  neutral respecto al proveedor, instalable y probable sin el código de ningún otro framework.
- **E-0.3 Autoridad.** Dentro de un framework, su Núcleo Rector manda sobre el fondo y el Estatuto
  sobre la forma. Cuando chocan, se abre una decisión en el Estatuto; una excepción local nunca es
  la primera respuesta.
- **E-0.4 Conformidad.** La conformidad se declara (`estatuto.toml`), se mide (`estatuto gate`) y es
  continua (el gate corre en la integración continua en cada envío). Un repositorio que no puede
  medirse no es conforme.
- **E-0.5 Excepciones.** Una desviación respecto a un control se registra como excepción fechada,
  respaldada por un registro de decisión y con fecha de caducidad (E-8.1). La deriva silenciosa es un
  defecto.

## E-1 Identidad

- **E-1.1 Declaración [gate].** `estatuto.toml` en la raíz declara `name` (la persona: `El` o `La`
  seguido de un nombre con mayúscula), `slug` (identificador en minúsculas), `role`, `package`
  (paquete Python) y `standard` (la versión del Estatuto que sigue). Tablas opcionales:
  `[language]` con los globs de `archive` y los `proper_nouns`; `[changelog]` con
  `normative_prefixes` y `normative_files`; entradas `[[exception]]`. Solo El Estatuto declara
  `role = "standard"`.
- **E-1.2 Nombres y disposición [gate].** La distribución se llama `<slug>-framework` (el propio
  Estatuto es `estatuto`); el paquete vive en `src/<package>/` y se importa con ese nombre. La
  persona aparece en la prosa; el slug, en identificadores, espacios de nombres y archivos.
- **E-1.3 Una sola versión [gate].** `src/<package>/version.py` es la única fuente de la versión, una
  versión semántica. `pyproject.toml`, `CHANGELOG.md` (una sección `## <versión>`) y, en un
  empleado, `manifest.json` coinciden con ella; la conformidad falla cuando se separan.
- **E-1.4 Identidad del repositorio.** Un framework se identifica por su persona, su slug y su
  remoto git. Las rutas locales son descriptivas y nunca aparecen en la superficie viva. El
  `registry/frameworks.json` del Estatuto registra los frameworks de la casa.

## E-2 Raíz del repositorio

- **E-2.1 Archivos obligatorios [gate].** `README.md`, `AGENTS.md`, `CONTRIBUTING.md`,
  `CHANGELOG.md`, `PROJECT_MAP.md`, `pyproject.toml`, `uv.lock`, `mkdocs.yml`, `.gitignore`,
  `.python-version`, `estatuto.toml`; en un empleado, `manifest.json`; en la Generala o en un
  empleado, `conformance.py` o un comando `<cli> conformance` documentado.
- **E-2.2 Directorios obligatorios [gate].** `src/`, `tests/`, `docs/`, `.github/workflows/` con al
  menos un flujo, `gates/` con al menos un corpus `<nombre>-gate-v<semver>.json`; en la Generala o
  en un empleado, `contracts/`.
- **E-2.3 Árboles desechables ignorados [gate].** `.gitignore` ignora al menos `.venv/`, `work/`,
  `dist/` y `site/`. Nada bajo un árbol desechable es fuente de verdad.
- **E-2.4 Archivos generados.** `manifest.json`, `contracts/*.json`,
  `docs/governance/program-status.md`, los índices históricos y la evidencia registrada se generan
  con un comando nombrado en `CONTRIBUTING.md` y nunca se editan a mano. Editar a mano un archivo
  generado es un defecto aunque su contenido sea correcto.

## E-3 Documentación

- **E-3.1 Diátaxis [gate].** `docs/index.md` y los cuatro cuadrantes —`tutorials/` (aprender),
  `howto/` (tareas), `topics/` (comprender), `reference/` (hechos)— cada uno con al menos una
  página. Una página pertenece a exactamente un cuadrante.
- **E-3.2 Registros de decisión [gate].** `docs/decisions/` guarda registros llamados
  `NNNN-slug.md` (una serie heredada como `DK0-NNN-slug.md` puede continuar en un framework que ya
  la tenga) y un `index.md` que lista cada registro. Un registro tiene estado, contexto, decisión y
  consecuencias; lo sustituye un registro nuevo, nunca se edita para decir otra cosa.
- **E-3.3 Gobierno [gate].** `docs/governance/CHARTER.md` dice qué es y qué no es el framework (su
  Núcleo Rector). `docs/governance/baseline/` guarda las descripciones de diseño congeladas;
  `BASELINE.sha256` registra `<sha256>  <archivo>` por cada una y el gate verifica los hashes.
  `docs/governance/program-status.md` es derivado, nunca editado a mano. Un ledger de requisitos
  (`docs/governance/requirement-ledger.json`) debería existir en un framework cuya línea base
  contenga requisitos.
- **E-3.4 Mapa del proyecto [gate].** `PROJECT_MAP.md` permite que otro agente continúe sin el
  historial de la conversación. Tiene secciones sobre identidad y estado actual, jerarquía de
  autoridad, disposición, cómo cambiar el framework y verificación.
- **E-3.5 Reglas para agentes [gate].** `AGENTS.md` apunta a `docs/governance/CHARTER.md`, lista la
  cadena de verificación que se corre antes de declarar un trabajo terminado, y esa cadena incluye
  `estatuto gate`. Dice qué se genera, qué está congelado y qué nunca se hace.
- **E-3.6 README [gate].** `README.md` tiene secciones que dicen qué hace el framework (y qué se
  niega a hacer), un arranque rápido, el mapa de la documentación, cómo verificar un cambio y el
  estado actual con sus límites honestos.
- **E-3.7 Sitio [gate].** `mkdocs.yml` construye en modo estricto (`strict: true`) a partir de una
  `nav` explícita. El tema Material es el tema de la casa; el material de archivo se excluye del
  sitio y se indexa.
- **E-3.8 Bitácora de cambios [gate].** `CHANGELOG.md` sigue Keep a Changelog y siempre tiene una
  sección `## Unreleased`; cada versión publicada tiene una sección `## <versión> — <fecha>`.
- **E-3.9 Jerarquía de autoridad.** `PROJECT_MAP.md` establece la jerarquía en este orden: el
  Estatuto (forma) · el Núcleo Rector · la línea base congelada · las decisiones · la superficie
  pública declarada (contratos, capacidades) · pruebas, conformidad y gates · estado derivado ·
  README. Un documento inferior que contradiga a uno superior se corrige, nunca se obedece.
- **E-3.10 Historia.** Los planes, la evidencia y los informes de incrementos pasados se quedan donde
  los gates los hashearon, se indexan con un `docs/history/INDEX.md` derivado cuando existen y nunca
  se reescriben. Un plan declara alcance y gate; por sí solo no crea obligación normativa.

## E-4 Idioma

- **E-4.1 Superficie viva en inglés [gate].** Todo archivo Markdown de la raíz y toda página bajo
  `docs/` no cubierta por un glob de archivo es prosa en inglés. Identificadores, docstrings,
  comentarios, mensajes, descripciones de datos y mensajes de commit están en inglés.
- **E-4.2 Sin rutas de máquina [gate].** La superficie viva no contiene la ruta absoluta de ninguna
  máquina.
- **E-4.3 El archivo conserva su idioma.** Las líneas base congeladas, los planes históricos, la
  evidencia, los índices históricos y los registros de decisión aceptados antes de adoptar el
  Estatuto conservan el idioma en que se escribieron y se listan en `[language].archive`. Un
  documento congelado nunca se traduce: su hash es su identidad; un registro de decisión nunca se
  edita, así que tampoco se traduce.
- **E-4.4 Fixtures.** Las cargas de prueba pueden estar en cualquier idioma cuando lo que se prueba
  es la neutralidad de idioma; en otro caso, las nuevas prefieren el inglés.
- **E-4.5 La edición del Dueño.** La edición en español del Estatuto es el único documento vivo en
  español de la casa. Lleva los mismos identificadores de cláusula que el texto normativo y el gate
  verifica la paridad (E-9.1).

## E-5 Nombrado

- **E-5.1 Archivos de contrato [gate].** Todo archivo bajo `contracts/` es un JSON Schema llamado
  `<nombre>-v<semver>.json` cuyo `$id` es `<propietario>.<nombre>/<semver>`; el propietario es `peg`
  bajo `contracts/peg/` y el slug del framework en el resto. Los archivos se renderizan desde
  modelos (E-2.4).
- **E-5.2 Pruebas [gate].** Los archivos de prueba son `tests/**/test_<asunto>.py`, nombrados por el
  asunto que protegen, nunca por el proceso que los produjo (`phase`, `sprint`, `session`, …).
- **E-5.3 Identificadores del protocolo [gate].** `emp_<slug>01` es el identificador del empleado;
  los de capacidad cumplen `cap_[a-z0-9][a-z0-9_-]{7,63}`; los de pack `pack_…`; los de tenant
  `ten_…`; los de misión `mis_…`. El sufijo `01` es la instancia de la persona; un segundo despliegue
  de la misma persona es `02`.
- **E-5.4 Planes [gate].** Los planes de incremento, cuando se conservan, son
  `docs/plans/<FAMILIA>-<NN>-slug.md`, la familia en mayúsculas y el slug en minúsculas.
- **E-5.5 Identificadores de esquema.** Un documento publicado se identifica como
  `<propietario>.<nombre-kebab>/<semver>`. Los documentos del protocolo usan campos en snake_case.
  Un contrato de dominio conserva la convención de su propietario, pero publica un identificador y un
  JSON Schema bajo `contracts/`.
- **E-5.6 Códigos de error.** Los códigos de error van en `MAYÚSCULAS_CON_GUIÓN_BAJO`, publicados en
  el manifiesto, cada uno con su propia redacción de limitación y siguiente paso. El protocolo
  reserva el significado de `CONTRACT_INVALID`, `PROTOCOL_UNSUPPORTED`, `CAPABILITY_UNSUPPORTED`,
  `AUTHORITY_REQUIRED`, `POLICY_BLOCKED`, `BUDGET_EXCEEDED`, `PROVIDER_UNAVAILABLE`,
  `DEPENDENCY_UNAVAILABLE`, `EVIDENCE_INSUFFICIENT`, `HUMAN_INTERVENTION_REQUIRED`,
  `TERMINAL_CONDITION_UNMET`, `IDEMPOTENCY_CONFLICT`, `CANCELLED`. Un rechazo por política es
  `POLICY_BLOCKED`, nunca `CONTRACT_INVALID`; una respuesta de proveedor que el contrato no puede
  aceptar es `PROVIDER_UNAVAILABLE`.
- **E-5.7 Casos y gates.** Los casos de conformidad son `<FAMILIA>-NNN`; los identificadores de gate
  son `<Letra><n>-slug`; un corpus de gate es `gates/<nombre>-gate-v<semver>.json` con `schema`,
  `purpose`, `cases` que atan requisitos a identificadores de prueba y `required_score` igual al
  número de casos. No hay promedios.
- **E-5.8 Commits.** Los mensajes de commit son `tipo: resumen` en inglés, con tipo en
  `feat · fix · docs · refactor · test · evidence · release · chore · style`, y un cuerpo que dice por
  qué cuando el resumen no alcanza.

## E-6 Herramientas y verificación

- **E-6.1 Construcción [gate].** uv resuelve y bloquea; hatchling construye; `requires-python`
  declara un piso de al menos 3.12 y `.python-version` fija 3.12 o más nuevo. Un framework puede
  exigir un intérprete más nuevo y registra por qué en una decisión.
- **E-6.2 Herramientas [gate].** `ruff`, `mypy`, `pytest`, `pytest-cov`, `mkdocs` y `pip-audit` son
  dependencias de desarrollo declaradas.
- **E-6.3 Pisos [gate].** `[tool.ruff]` está configurado; `[tool.mypy] strict = true`; la cobertura
  de ramas tiene un piso de al menos 80 que nunca se baja. Deberían existir pisos por módulo que
  suban con la cobertura.
- **E-6.4 Integración continua [gate].** El flujo corre, en cada envío y solicitud de integración: el
  gate de bitácora, `ruff check`, `ruff format --check`, `mypy`, `pytest` con cobertura, la
  conformidad y los gates propios del repositorio, `estatuto gate`, `pip-audit`, `uv build` y
  `mkdocs build --strict`.
- **E-6.5 Definición de terminado.** Una tarea está terminada cuando su comportamiento es una
  abstracción general y no un caso especial; todo cambio que cruza la frontera pública está
  versionado; los estados de fallo son honestos; costos y evidencia se rastrean por recibos; existen
  pruebas deterministas en proporción al riesgo; toda la cadena de verificación pasa; y la
  documentación describe exactamente lo que existe, otra vez.
- **E-6.6 Gates.** Toda promesa de un framework tiene un gate ejecutable: `<cli> gate <nombre>
  --output work/<nombre>.json` produce un documento de resultado con identificador de esquema. Una
  prueba verde significa que corrió el corpus declarado; por sí sola nunca significa que un horizonte
  esté aprobado.
- **E-6.7 Evidencia.** La evidencia la registran scripts, queda enlazada por hash a las fuentes que
  observó y nunca se edita a mano. Cuando una fuente cambia legítimamente, la evidencia se vuelve a
  registrar en un incremento fechado con el mismo script; un hash registrado que no corresponde a
  nada es un defecto.

## E-7 El protocolo: PEG/1

- **E-7.1 Propiedad y vendorización [gate].** El Protocolo de Empleado Gobernado pertenece al
  Estatuto. Sus documentos se publican bajo el espacio de nombres `peg.`, se renderizan desde
  `estatuto.peg.contracts` a `schemas/peg/` y los vendoriza literalmente cada Generala y cada empleado
  bajo `contracts/peg/`; el gate compara bytes. Ningún framework define una forma protocolar propia.
- **E-7.2 Manifiesto [gate].** Un empleado publica `manifest.json`, un documento
  `peg.manifest/1.0.0` renderizado desde sus declaraciones, cuyo `integrity_digest` es el SHA-256 del
  JSON canónico del manifiesto sin el campo del digest (E-7.14). Cualquier consumidor puede
  recomputarlo.
- **E-7.3 Contratos referenciados [gate].** Todo identificador de contrato que nombre el manifiesto
  —entrada, salida, evidencia, entradas deprecadas— que no sea un documento `peg.` tiene un JSON
  Schema en `contracts/<nombre>-v<semver>.json`.
- **E-7.4 Superficie documentada [gate].** `docs/reference/` documenta las tres rutas —`POST
  /peg/v1/assignments`, `GET /peg/v1/manifest`, `GET /peg/v1/health`— y el identificador del
  manifiesto.
- **E-7.5 Códigos reservados [gate].** Un empleado publica al menos `CONTRACT_INVALID` y nunca
  publica un código reservado con otra grafía ni con otro significado.
- **E-7.6 Perfiles.** Todo empleado implementa `CORE` (identidad y versiones, capacidades,
  negociación, estados, evidencia, errores, costo, idempotencia, cancelación y resultado propuesto).
  `FRAMEWORK` añade un servicio persistente con administración y salud propias; `CONTEXT_PROVIDER`
  añade contexto solicitado y entregado con procedencia, suficiencia, parcialidad, recibo y vigencia,
  sin convertirse en autoridad sobre la misión.
- **E-7.7 Negociación.** La Generala envía un `peg.compatibility-demand/1.0.0`; la compatibilidad
  exige que todo campo material coincida exactamente con una capacidad declarada —versión del
  protocolo, perfiles, modo, identificador y versión de capacidad, contratos de entrada, salida y
  evidencia, checkpoint—. La decisión es `accept` o `reject` con razones estables, antes de que exista
  una asignación. No hay `latest` ni degradación silenciosa. Compartir un identificador de capacidad
  nunca implica sustituibilidad.
- **E-7.8 Transportes.** Un empleado ofrece el protocolo por un puerto en proceso y, cuando corre como
  servicio, por HTTP en las tres rutas. Un viaje de ida y vuelta por JSON no cambia nada; una prueba
  demuestra la equivalencia. Los cuerpos de solicitud están acotados; nadie obtiene autoridad por
  alcanzar un puerto abierto.
- **E-7.9 Asignación, resultado, rechazo.** Un `peg.assignment/1.0.0` lleva la cápsula exacta de
  contexto y su digest y no transporta autoridad. Un `peg.result/1.0.0` atestigua el mismo tenant,
  misión, obligación, asignación, generación y digest de contexto, lleva referencias de evidencia,
  procedencia, costo observado y pendiente y la carga de dominio bajo el contrato de salida de la
  capacidad; siempre es una propuesta. Un `peg.refusal/1.0.0` se devuelve cuando nada puede
  ejecutarse, con el estado HTTP de su código de error: `CONTRACT_INVALID` 400, `BUDGET_EXCEEDED`
  402, `AUTHORITY_REQUIRED` y `POLICY_BLOCKED` 403, `IDEMPOTENCY_CONFLICT` 409,
  `PROTOCOL_UNSUPPORTED` y `CAPABILITY_UNSUPPORTED` 422, `PROVIDER_UNAVAILABLE` y
  `DEPENDENCY_UNAVAILABLE` 503, cualquier otro código 422.
- **E-7.10 Obligaciones de la Generala.** La Generala negocia antes de entregar; admite cada versión
  de empleado por tenant mediante un plano administrativo con eventos inmutables (publicar, validar,
  probar, certificar, admitir, observar, canary, rollback, suspender, cuarentena, retirar); rechaza un
  resultado que transporte autoridad o cuyos campos de identidad difieran de la asignación; lleva el
  libro de costos; y solo ella acepta o rechaza el trabajo.
- **E-7.11 Obligaciones del empleado.** El empleado no depende en tiempo de ejecución de la Generala;
  propone y nunca acepta; hace que el costo sea igual a la suma de sus recibos; mantiene estados
  honestos; trata `assignment_id` con `generation` como clave de idempotencia; y acota la cancelación
  a la asignación sin revocar ninguna concesión.
- **E-7.12 Vínculos y concesiones.** La identidad de tenant y la identidad de workload nunca se
  infieren una de otra ni del texto. Un `peg.tenant-binding/1.0.0` declara la correspondencia entre
  el tenant de la Generala y el de un proveedor; un `peg.workload-binding/1.0.0` autentica un
  workload y no transporta tenant. Un `CONTEXT_PROVIDER` se consume bajo dos concesiones —la de
  asignación de la Generala y la de contexto del propio proveedor— y un paquete de contexto es
  evidencia, nunca autoridad.
- **E-7.13 Versionado del protocolo.** Las versiones son exactas. Un cambio aditivo en un documento
  es una nueva versión menor negociada explícitamente con ventana de coexistencia; un cambio
  incompatible es una nueva versión mayor. Toda misión activa fija sus versiones. Las capacidades
  aditivas, como el transporte de contexto compuesto, se publican como documentos separados
  (`peg.context-transport-support/1.0.0`), nunca se infieren de un perfil ni de un nombre.
- **E-7.14 JSON canónico.** Donde el protocolo hashea un documento, el digest es SHA-256 sobre los
  bytes UTF-8 de la serialización JSON con claves ordenadas, separadores `,` y `:` sin espacios y
  caracteres no ASCII sin escapar.

## E-8 Disciplina del cambio

- **E-8.1 Excepciones [gate].** Toda `[[exception]]` nombra un control existente, cita un registro
  de decisión existente, declara una razón y una fecha de caducidad futura. Una excepción vencida no
  exime de nada y es en sí misma un hallazgo.
- **E-8.2 Gate de bitácora [gate].** La integración continua corre `estatuto changelog-gate --base
  <ref>`: un cambio bajo un prefijo normativo o en un archivo normativo se registra bajo
  `## Unreleased` o la construcción falla. Los archivos de flujo y el archivo de bloqueo son
  herramientas y pueden cambiar solos.
- **E-8.3 Deprecación [gate].** `CONTRIBUTING.md` declara la política: un elemento deprecado sigue
  funcionando al menos una versión menor después de la que lo depreca, se lista con su reemplazo y su
  versión de retiro, y mientras tanto no cambia nada en silencio.
- **E-8.4 Decisiones.** Una decisión de la que depende el código es un registro (E-3.2) antes de que
  el código entre. Un cambio que retira una opción, una dependencia o una garantía necesita una
  alternativa, un análisis de compatibilidad, una ventana de deprecación y un camino de migración.
- **E-8.5 Contratos públicos.** Las reglas de validación de un contrato publicado nunca cambian en el
  mismo lugar. Una carga que era válida sigue siéndolo bajo el mismo identificador; de lo contrario se
  publica una versión nueva, se congela la anterior y se declara deprecada.
- **E-8.6 Cambiar el Estatuto.** Una cláusula que se vuelve más estricta, o un documento del
  protocolo cuya forma cambia, es una versión mayor del Estatuto: cada framework se vuelve a medir y
  la bitácora nombra la migración. Una cláusula o documento aditivo es una versión menor. Redacción y
  herramientas son parches. Todo cambio es primero un registro de decisión aquí.

## E-9 El Estatuto mismo

- **E-9.1 Paridad [gate].** `ESTATUTO.md` y `docs/standard/STANDARD.md` llevan el mismo conjunto de
  identificadores de cláusula.
- **E-9.2 Automedición.** El Estatuto declara `role = "standard"` y pasa su propio gate.
- **E-9.3 La plantilla es el Estatuto ejecutable.** `estatuto new-employee` produce un repositorio
  que pasa el gate y sus propias pruebas al nacer; una cláusula que la plantilla no pueda satisfacer
  es un defecto de una de las dos.
- **E-9.4 Registro.** `registry/frameworks.json` lista los frameworks de la casa con persona, slug,
  rol, paquete, remoto y resumen del Núcleo Rector. Describe; el gate mide.
