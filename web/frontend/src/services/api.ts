const API_URL = import.meta.env.VITE_API_URL ;

export interface CleanOptions {
  remove_duplicates: boolean;
  normalize_null_strings: boolean;
  trim_whitespace: boolean;
  fill_missing_numeric: boolean;
  numeric_strategy: 'mean' | 'median' | 'zero';
}



export const inspectDataset = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/dataset/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Error al inspeccionar el dataset');
  }

  return response.json();
};


/**
 * Envía el archivo y las opciones al endpoint de limpieza de FastAPI.
 */
export const processDataset = async (file: File, options: CleanOptions) => {
  const formData = new FormData();
  formData.append('file', file);
  
  formData.append('options', JSON.stringify(options));

  const response = await fetch(`${API_URL}/clean/process`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    
    if (errorData.detail && Array.isArray(errorData.detail)) {
      const msg = errorData.detail.map((err: any) => `${err.loc.join('.')}: ${err.msg}`).join(', ');
      throw new Error(`Error de validación: ${msg}`);
    }

    throw new Error(errorData.detail || 'Error al procesar el archivo en el servidor');
  }

  return response.json();
};

/**
 * Descarga el archivo procesado 
 */
export const downloadExport = async (
  file: File,
  options: CleanOptions,
  endpoint: 'export-file' | 'export-audit',
  format: string,
  filename: string
) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('options', JSON.stringify(options));
  
  if (endpoint === 'export-file') {
    formData.append('export_format', format);
  }

  const response = await fetch(`${API_URL}/reports/${endpoint}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Error al descargar el reporte o archivo procesado');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};