# Crear un empleado desde cero

Edición del Dueño de `docs/standard/NEW-EMPLOYEE.md`. Un empleado es un framework con un oficio.
Nace conforme: la fábrica produce un repositorio completo que pasa el gate del Estatuto y sus
propias pruebas desde el primer minuto, y el trabajo que sigue es el oficio, el Núcleo Rector y el
diseño —nunca el andamiaje—.

## 1. Antes del primer comando

Responde en un párrafo cada una, en inglés, y guarda las respuestas; se convierten en el Núcleo
Rector:

- ¿Qué convierte el empleado en qué, para quién, y dónde se detiene?
- ¿Qué capacidades ofrece, cada una con un contrato de entrada, uno de salida y uno de evidencia?
- ¿Qué se niega a hacer, y qué códigos de error nombran sus rechazos?
- ¿Qué costos incurre, en qué unidad, y cómo lo prueba un recibo?

Elige la persona (`El` o `La` y un nombre con mayúscula), el slug (minúsculas, el nombre sin
artículo) y, si difiere, el paquete.

## 2. Créalo

```bash
uvx --from git+https://github.com/chiribogasantiago/el-estatuto estatuto new-employee ../el-archivero --name "El Archivero" --slug archivero
cd ../el-archivero
git init && git add -A && git commit -m "feat: scaffold El Archivero under El Estatuto"
uv sync --all-groups
uv run pytest
uv run python conformance.py
uvx --from git+https://github.com/chiribogasantiago/el-estatuto estatuto gate .
```

El gate pasa. Lo que tienes es un empleado completo, honesto y vacío: una capacidad de relleno, el
adaptador PEG/1 con sus tres rutas, dos transportes en proceso demostrados equivalentes,
conformidad ejecutable, un corpus de gate, el esqueleto de la documentación, la integración
continua. Lee `PROJECT_MAP.md`: se escribió para ti.

## 3. Escribe el Núcleo Rector

`docs/governance/CHARTER.md` es la fuente normativa de lo que el empleado es y no es. Completa cada
sección con las respuestas del paso 1. Luego escribe la descripción de diseño bajo
`docs/governance/baseline/` como un archivo nuevo y congélala:

```bash
cd docs/governance/baseline && shasum -a 256 SDD-*.md > BASELINE.sha256 && cd -
```

Un archivo congelado no se edita nunca más; una versión nueva es un archivo nuevo y una línea de
hash nueva.

## 4. Declara las capacidades

En `src/<paquete>/contracts.py`, define cada contrato de entrada, salida y evidencia como un modelo
Pydantic cerrado con un literal `schema` de la forma `<slug>.<nombre>/1.0.0`. En
`capabilities.py`, registra los contratos y las capacidades (`cap_<slug>_<nombre>01`), los modos y
los códigos de error. Renderiza:

```bash
uv run <slug> render
```

`manifest.json` y `contracts/*.json` son ahora proyecciones de tus declaraciones. Nunca los edites.

## 5. Escribe el oficio

`src/<paquete>/employee.py` es dueño de los invariantes: contratos estrictos, estados honestos,
costo igual a la suma de recibos, `proposed: true`. Todo lo que un despliegue podría querer distinto
—proveedores, modelos, límites, vocabularios, plantillas— es una política inyectada con un valor por
defecto nombrado, alcanzada por puertos. Una capacidad nueva llega por declaraciones, puertos y
políticas, nunca ramificando el núcleo según un caso de uso.

Cada pieza de evidencia lleva digest y referencia. Cada recibo lleva unidad, cantidad y costo. Un
resultado que no sea `completed` nombra su código de error, al menos una limitación y un siguiente
paso. Un rechazo es un documento tipado, nunca un resultado disfrazado.

## 6. Demuéstralo

Las pruebas se nombran por el asunto que protegen. Para cada capacidad: el método con entrada
válida, el rechazo con entrada inválida, el cable (asignación que entra, resultado que sale, rechazos
ante manipulación y ante capacidades no declaradas) y la equivalencia de transportes. Añade las
pruebas a `gates/<slug>-gate-…json` para que una promesa no pueda perder su prueba en silencio.
Mantén la cobertura de ramas en el piso o por encima; sube el piso cuando suba la cobertura; nunca
lo bajes.

## 7. Documéntalo

Diátaxis: un tutorial que lleve a un lector hasta una asignación servida y respondida; páginas
cómo-hacer para las tareas de un integrador; temas para los conceptos; referencia para contratos,
rutas, códigos de error y línea de comandos. Registra toda decisión de la que dependa el código
bajo `docs/decisions/`. Registra todo cambio normativo bajo `## Unreleased`.

## 8. Conéctalo a la Generala

La Generala descubre al empleado por su manifiesto, negocia una demanda de compatibilidad contra
cada capacidad, admite la versión por tenant mediante su plano administrativo y solo entonces
asigna. El empleado nunca depende del código de la Generala. Pide a quienes mantienen la Generala
que añadan al empleado a su composición; entrégales el manifiesto, los contratos y la URL base.

## 9. Publica

`src/<paquete>/version.py` es la única fuente. Súbela, mueve `## Unreleased` bajo `## <versión> —
<fecha>`, renderiza otra vez (`<slug> render`), corre la cadena de `AGENTS.md`, etiqueta. Un
empleado actualizado es una versión nueva admitida junto a la anterior hasta que el rollback quede
demostrado.

## Lo que nunca ocurre

- Editar a mano `contracts/peg/`, `manifest.json`, `contracts/*.json`, una línea base congelada o un
  archivo de evidencia registrado.
- Depender en tiempo de ejecución de la Generala o de otro empleado.
- Aceptar, cerrar o gobernar nada. El empleado propone.
- Afirmar en un documento lo que el código y una prueba no demuestran.
- Escribir español, o una ruta de máquina, en la superficie viva.
