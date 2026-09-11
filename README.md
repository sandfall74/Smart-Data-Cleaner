#  Data Clean & Visual Analytics Module

Un módulo web interactivo para la inspección, sanitización, análisis visual y exportación de datos (CSV / Excel). Permite a los usuarios evaluar la salud de sus datasets, aplicar reglas de limpieza configurables y generar reportes ejecutivos en formato PDF vectorial con gráficos integrados.

---

##  Características Principales

* **Diagnóstico de Integridad:**
  * Cálculo automático del *Health Score* del dataset.
  * Conteo de filas, columnas, valores nulos y registros duplicados.
  * Análisis columna por columna con detección de tipos de datos y sugerencias de tratamiento.
* **Reglas de Limpieza Personalizables:**
  * Eliminación de registros duplicados.
  * Recorte de espacios en blanco (*trimming*).
  * Normalización de cadenas nulas o vacías (`"null"`, `"N/A"`, `""`).
  * Estrategias opcionales para imputación de datos faltantes.
* **Análisis Visual & Gráficos:**
  * Visualización interactiva de distribuciones y relaciones de variables tras el proceso de limpieza.
* **Exportación de Reportes Completo:**
  * Descarga del dataset sanitizado en CSV.
  * Generación de **Reporte PDF Ejecutivo** utilizando `@react-pdf/renderer` y capturas de alta definición de las visualizaciones.

---

##  Tecnologías Utilizadas

* **Frontend:** React 18, TypeScript, Tailwind CSS
* **Componentes de UI:** Lucide React (iconografía), componentes accesibles estilo Shadcn UI
* **Generación de PDF:** `@react-pdf/renderer`
* **Captura de Visualizaciones:** `html-to-image`
* **Procesamiento / API Backend:** Servicio asíncrono para inspección y limpieza de datos (`inspectDataset`, `processDataset`)

---

##  Instalación y Configuración

### 1. Requisitos Previos
Asegúrate de tener instalado:
* **Node.js** (v18.x o superior)
* **npm** / **yarn** / **pnpm**

## 🚧 Desafíos Pendientes & Roadmap

Buscamos colaboración en las siguientes áreas:

- [ ] **Generación de Gráficos Vectoriales en PDF:** Actualmente los gráficos se exportan como imagen PNG comprimida. Queremos pasar a renderizado vectorial nativo con `@react-pdf/renderer`.
- [ ] **Soporte para Datasets Grandes:** Optimización del rendimiento al procesar archivos de más de 50k filas.

Si tienes ideas o quieres resolver alguno de estos puntos, ¡te invitamos a abrir un Issue o Pull Request!

---

##  Cómo Contribuir

1. Haz un **Fork** del proyecto.
2. Crea una rama para tu funcionalidad (`git checkout -b feature/MiContribucion`).
3. Haz Commit de tus cambios (`git commit -m 'feat: agrega renderizado SVG'`).
4. Haz Push a la rama (`git push origin feature/MiContribucion`).
5. Abre un **Pull Request**.

### 2. Clonar el Repositorio
```bash
git clone https://github.com/sandfall74/Smart-Data-Cleaner.git
cd Smart-Data-Cleaner ```



