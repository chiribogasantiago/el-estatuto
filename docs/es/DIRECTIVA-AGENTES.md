# Directiva para agentes

Edición del Dueño de `docs/standard/AGENT-DIRECTIVE.md`. Para todo agente —humano o modelo— que
continúe un framework de la casa. Los frameworks no están terminados; esta directiva los mantiene
construibles sin romper la estructura que permite que la Generala los conecte, que un agente los
continúe y que el Dueño confíe en lo que afirman.

## 1. Leer antes de escribir

En este orden, siempre: `AGENTS.md` (las reglas y la cadena de verificación), `PROJECT_MAP.md`
(dónde vive cada cosa y qué tiene autoridad), `docs/governance/CHARTER.md` (qué es y qué no es el
framework), `docs/governance/program-status.md` (el estado actual honesto), luego la decisión y el
plan más cercanos a la tarea, luego las pruebas que protegen el código que se va a tocar. Solo
después el código. Si `PROJECT_MAP.md` y el árbol no coinciden, el mapa está desactualizado:
corregir el mapa es parte de la tarea.

## 2. Lo que nunca cambia

- **Las líneas base congeladas** bajo `docs/governance/baseline/`: nunca se editan, nunca se
  traducen. Una versión nueva es un archivo nuevo y una línea de hash nueva.
- **Los archivos generados**: `manifest.json`, `contracts/*.json`,
  `docs/governance/program-status.md`, los índices históricos, la evidencia registrada. Se cambia la
  fuente, se corre el renderizador, se confirman ambos.
- **Los esquemas del protocolo vendorizados** bajo `contracts/peg/`: no se editan en absoluto. Se
  corre `estatuto sync-peg .` cuando el Estatuto publica una versión nueva.
- **Las reglas de un contrato publicado**: una carga que era válida sigue siéndolo bajo el mismo
  identificador.
- **Los registros de decisión**: los sustituye un registro nuevo, nunca se editan para decir otra
  cosa.
- **La jerarquía de autoridad** de `PROJECT_MAP.md`: un documento inferior que contradiga a uno
  superior se corrige, nunca se obedece.

## 3. Cómo entra un cambio

1. **Decidir primero.** Si el cambio retira una opción, una dependencia o una garantía, o elige una
   tecnología, el registro de decisión se escribe antes que el código. Estado, contexto, decisión,
   consecuencias.
2. **Declarar, luego renderizar.** Capacidades y contratos cambian en su módulo de declaración; el
   renderizador produce los archivos publicados.
3. **Demostrar.** Una prueba nombrada por el asunto; una entrada en el gate para que la promesa no
   pueda perder su prueba; cobertura en el piso o por encima.
4. **Registrar.** `## Unreleased` en `CHANGELOG.md` para todo cambio normativo. Si no, la integración
   continua falla.
5. **Verificar.** Toda la cadena de `AGENTS.md`, incluido `estatuto gate .`. No una parte: toda.
6. **Describir.** `PROJECT_MAP.md` y la documentación dicen exactamente lo que existe ahora. Una
   afirmación sin código y prueba detrás se elimina, no se suaviza.

## 4. Fronteras entre frameworks

- Un empleado nunca importa a la Generala ni a otro empleado. La interoperabilidad son contratos,
  puertos y el protocolo.
- La Generala nunca entra en los almacenes ni en las entrañas de un empleado; habla PEG/1 y conserva
  autoridad, concesiones, libro de costos y aceptación.
- Nadie obtiene autoridad por ubicación, por texto, por la salida de un modelo ni por un puerto
  abierto.
- Una forma protocolar nunca se define localmente. Si al protocolo le falta algo, el cambio es una
  decisión en El Estatuto, luego una versión nueva del documento, luego `estatuto sync-peg` en todas
  partes.

## 5. La política vive fuera del núcleo

El núcleo conserva solo invariantes: contratos estrictos, autoridad explícita, procedencia, estados
honestos, costo igual a recibos, aislamiento por asignación. Todo lo que un despliegue podría querer
distinto —proveedores, modelos, precios, idioma, límites, plantillas, rúbricas, vocabularios,
condiciones terminales— es una política inyectada con un valor por defecto nombrado. Una prueba de
generalidad asegura la ausencia de política quemada; si se añade un literal al núcleo, esa prueba es
donde debe fallar.

## 6. Honestidad sobre el estado

- Una prueba verde significa que corrió el corpus declarado. No aprueba un horizonte, no elige una
  tecnología ni promueve un candidato. Se dice cuál de las tres cosas ocurrió.
- Un código de error nombra la causa que ocurrió. Un rechazo por política es `POLICY_BLOCKED`, nunca
  `CONTRACT_INVALID`; una respuesta de proveedor que el contrato no puede aceptar es
  `PROVIDER_UNAVAILABLE`.
- La evidencia la registran scripts y queda enlazada por hash. Si una fuente debe cambiar, se vuelve
  a registrar con el mismo script en un incremento fechado. Nunca se escribe un hash a mano.
- `program-status.md` es derivado. Si está mal, se corrige la derivación.

## 7. Desviarse del Estatuto

Una desviación es una `[[exception]]` en `estatuto.toml`: el control, un registro de decisión, una
razón y una fecha de caducidad. El gate la muestra como eximida hasta la caducidad y después falla.
No hay otra forma. Si una cláusula está mal para todos los frameworks, se abre una decisión en El
Estatuto y se cambia la cláusula.

## 8. Idioma y desorden

Inglés en la superficie viva; el archivo conserva su idioma; las cargas de prueba pueden ser
cualquier cosa cuando lo que se prueba es la neutralidad. Sin rutas de máquina. Sin alias de
compatibilidad sin entrada en la bitácora y versión de retiro. Sin archivos de prueba nombrados por
una fase o un sprint. Nada bajo `work/`, `dist/` o `site/` es fuente de verdad.

## 9. Antes de decir que está terminado

Corre la cadena. Lee la salida del gate. Vuelve a leer `PROJECT_MAP.md` y `program-status.md` como
lo hará el siguiente agente. Si alguno de los dos lo engañaría, no está terminado.
