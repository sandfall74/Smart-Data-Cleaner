import React, { useState } from "react";
import {
  Upload,
  AlertCircle,
  RefreshCw,
  Download,
  FileSearch,
  Sparkles,
  FileSpreadsheet,
  Table as TableIcon,
  CheckCircle2,
  Info,
  ArrowRight,
  FileChartColumn,
  Lock,
  LayoutDashboard,
} from "lucide-react";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../components/ui/tabs";
import {
  inspectDataset,
  processDataset,
  downloadExport,
  type CleanOptions,
} from "../services/api";
import { DatasetCharts } from "../components/analytics/DatasetCharts";
import { pdf} from "@react-pdf/renderer";
import { AnalyticsReportPDF } from "../components/analytics/AnalyticseportPDF";
import { toPng } from "html-to-image";

export const AppCleaner: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [inspectLoading, setInspectLoading] = useState(false);
  const [processLoading, setProcessLoading] = useState(false);
  const [isExportingPDF, setIsExportingPDF] = useState(false);
  const [inspectionData, setInspectionData] = useState<any>(null);
  const [cleanResult, setCleanResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("original");
  const [chartImages, setChartImages] = useState<string[]>([]);

  const [options, setOptions] = useState<CleanOptions>({
    remove_duplicates: true,
    normalize_null_strings: true,
    trim_whitespace: true,
    fill_missing_numeric: false,
    numeric_strategy: "mean",
  });

  const handleGenerateChartImages = async () => {
    const chartElement = document.getElementById("charts-container");
    if (chartElement) {
      try {
        const dataUrl = await toPng(chartElement, { cacheBust: true });
        setChartImages([dataUrl]);
      } catch (err) {
        console.error("Error convirtiendo gráficos a imagen:", err);
      }
    }
  };

  const handleExportPDF = async () => {
    setIsExportingPDF(true);
    try {
      const chartElement = document.getElementById("charts-container");
      let capturedImages: string[] = [];

      if (chartElement) {
        const dataUrl = await toPng(chartElement, {
          pixelRatio: 2,
          cacheBust: true,
        });
        capturedImages.push(dataUrl);
      }

      const blob = await pdf(
        <AnalyticsReportPDF
          columnsSummary={inspectionData?.columns_summary || []}
          totalRows={
            (cleanResult?.preview || inspectionData?.preview || []).length
          }
          chartImages={capturedImages}
        />,
      ).toBlob();

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `reporte_analisis_${Date.now()}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error generando reporte PDF:", err);
    } finally {
      setIsExportingPDF(false);
    }
  };
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setError(null);
      setCleanResult(null);
      setInspectionData(null);
      setInspectLoading(true);
      setActiveTab("original");

      try {
        const result = await inspectDataset(selectedFile);
        setInspectionData(result);
      } catch (err: any) {
        setError(err.message || "Error al inspeccionar el dataset");
      } finally {
        setInspectLoading(false);
      }
    }
  };

  const handleProcess = async () => {
    if (!file) return setError("Selecciona un archivo primero.");
    setProcessLoading(true);
    setError(null);

    try {
      const data = await processDataset(file, options);
      setCleanResult(data);

      setActiveTab("clean");
    } catch (err: any) {
      setError(err.message || "Error al procesar los datos");
    } finally {
      setProcessLoading(false);
    }
  };

  const handleDownload = async (
    type: "export-file" | "export-audit",
    format: string,
  ) => {
    if (!file) return;
    try {
      await downloadExport(
        file,
        options,
        type,
        format,
        `dataset_limpio.${format}`,
      );
    } catch (err: any) {
      setError("Error en la descarga del archivo");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <header className="border-b border-slate-200 dark:border-[var(--color-neon-border)] pb-4">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <FileSpreadsheet className="text-sky-500 dark:text-[var(--color-neon-blue)]" />
          Módulo de Limpieza & Análisis Visual
        </h1>
        <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">
          Inspecciona la estructura inicial, aplica transformaciones y analiza
          los gráficos finales.
        </p>
      </header>

      {error && (
        <div className="p-4 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Panel Izquierdo */}
        <div className="space-y-6">
          <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Upload className="w-4 h-4 text-sky-500 dark:text-[var(--color-neon-blue)]" />
                1. Seleccionar Dataset
              </CardTitle>
            </CardHeader>
            <CardContent>
              <label className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-sky-300 dark:border-sky-500/40 rounded-lg cursor-pointer hover:bg-sky-50 dark:hover:bg-slate-800 transition-colors">
                <Upload className="w-8 h-8 text-sky-500 dark:text-[var(--color-neon-blue)] mb-2" />
                <span className="text-xs font-medium text-slate-700 dark:text-slate-300 text-center">
                  {file ? file.name : "Subir CSV o Excel"}
                </span>
                <input
                  type="file"
                  accept=".csv, .xlsx"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </label>
              {inspectLoading && (
                <div className="flex items-center justify-center gap-2 text-xs text-sky-500 mt-3 animate-pulse">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Analizando
                  estructura...
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-sky-500 dark:text-[var(--color-neon-blue)]" />
                2. Reglas de Limpieza
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={options.remove_duplicates}
                  onChange={(e) =>
                    setOptions({
                      ...options,
                      remove_duplicates: e.target.checked,
                    })
                  }
                />
                <span>Eliminar Duplicados</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={options.trim_whitespace}
                  onChange={(e) =>
                    setOptions({
                      ...options,
                      trim_whitespace: e.target.checked,
                    })
                  }
                />
                <span>Recortar Espacios en Blanco</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={options.normalize_null_strings}
                  onChange={(e) =>
                    setOptions({
                      ...options,
                      normalize_null_strings: e.target.checked,
                    })
                  }
                />
                <span>Normalizar Textos Nulos</span>
              </label>

              <Button
                onClick={handleProcess}
                disabled={processLoading || !file}
                className="w-full font-bold dark:bg-[var(--color-neon-blue)] dark:text-black dark:hover:bg-cyan-400 mt-4 gap-2"
              >
                {processLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <ArrowRight className="w-4 h-4" />
                )}
                Limpiar Dataset
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Panel Derecho*/}
        <div className="lg:col-span-2">
          {!inspectionData ? (
            <div className="h-64 border-2 border-dashed rounded-xl flex flex-col items-center justify-center text-slate-400 text-sm border-slate-300 dark:border-slate-800 space-y-2">
              <Info className="w-8 h-8 text-slate-400" />
              <span>
                Sube un archivo CSV o Excel para activar el flujo de trabajo.
              </span>
            </div>
          ) : (
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="w-full space-y-6"
            >
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger
                  value="original"
                  className="flex items-center gap-2"
                >
                  <TableIcon className="w-4 h-4" /> Original
                </TabsTrigger>

                <TabsTrigger
                  value="clean"
                  disabled={!cleanResult}
                  className="flex items-center gap-2"
                >
                  {!cleanResult && <Lock className="w-3 h-3 opacity-60" />}
                  <CheckCircle2 className="w-4 h-4" /> Datos Limpios
                </TabsTrigger>

                <TabsTrigger
                  value="charts"
                  disabled={!cleanResult}
                  className="flex items-center gap-2"
                >
                  {!cleanResult && <Lock className="w-3 h-3 opacity-60" />}
                  <FileChartColumn className="w-4 h-4" /> Gráficos
                </TabsTrigger>
              </TabsList>

              {/* PESTAÑA 1: DATASET ORIGINAL */}
              <TabsContent value="original" className="space-y-6">
                <div className="grid sm:grid-cols-4 gap-4">
                  <Card className="dark:bg-[var(--color-neon-card)] p-4 text-center">
                    <span className="text-xs text-slate-500">
                      Salud del Dataset
                    </span>
                    <p className="text-2xl font-extrabold text-sky-500">
                      {inspectionData.data_health_score}%
                    </p>
                  </Card>
                  <Card className="dark:bg-[var(--color-neon-card)] p-4 text-center">
                    <span className="text-xs text-slate-500">
                      Filas × Columnas
                    </span>
                    <p className="text-2xl font-bold">
                      {inspectionData.total_rows} ×{" "}
                      {inspectionData.total_columns}
                    </p>
                  </Card>
                  <Card className="dark:bg-[var(--color-neon-card)] p-4 text-center">
                    <span className="text-xs text-slate-500">
                      Valores Nulos
                    </span>
                    <p className="text-2xl font-bold text-amber-500">
                      {inspectionData.total_missing_values}
                    </p>
                  </Card>
                  <Card className="dark:bg-[var(--color-neon-card)] p-4 text-center">
                    <span className="text-xs text-slate-500">Duplicados</span>
                    <p className="text-2xl font-bold text-red-500">
                      {inspectionData.duplicates_count}
                    </p>
                  </Card>
                </div>

                <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center gap-2">
                      <FileSearch className="w-4 h-4 text-sky-500" />{" "}
                      Diagnóstico de Columnas Iniciales
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-0 overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Columna</TableHead>
                          <TableHead>Tipo</TableHead>
                          <TableHead>Faltantes (%)</TableHead>
                          <TableHead>Sugerencia</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {inspectionData.columns_summary.map((col: any) => (
                          <TableRow key={col.name}>
                            <TableCell className="font-medium">
                              {col.name}
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline">{col.data_type}</Badge>
                            </TableCell>
                            <TableCell>
                              <span
                                className={
                                  col.missing_count > 0
                                    ? "text-amber-500 font-semibold"
                                    : "text-slate-500"
                                }
                              >
                                {col.missing_count} ({col.missing_percentage}%)
                              </span>
                            </TableCell>
                            <TableCell className="text-xs text-slate-500">
                              {col.reason}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>

                <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center gap-2">
                      <TableIcon className="w-4 h-4 text-sky-500" /> Muestra del
                      Dataset Original
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-0 overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {inspectionData.columns_summary.map((col: any) => (
                            <TableHead key={col.name}>{col.name}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {inspectionData.preview.map((row: any, idx: number) => (
                          <TableRow key={idx}>
                            {inspectionData.columns_summary.map((col: any) => (
                              <TableCell key={col.name} className="text-xs">
                                {row[col.name] === "" ||
                                row[col.name] === null ? (
                                  <span className="text-red-400 italic">
                                    [Vacío]
                                  </span>
                                ) : (
                                  String(row[col.name])
                                )}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* PESTAÑA 2: DATASET LIMPIO */}
              <TabsContent value="clean" className="space-y-6">
                {cleanResult && (
                  <>
                    <Card className="dark:bg-[var(--color-neon-card)] border-emerald-500/40">
                      <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                          <CardTitle className="text-lg text-emerald-400 flex items-center gap-2">
                            <CheckCircle2 className="w-5 h-5" /> Dataset
                            Procesado Exitosamente
                          </CardTitle>
                          <CardDescription className="text-xs">
                            Se aplican las reglas de negocio y sanitización
                            solicitadas.
                          </CardDescription>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDownload("export-file", "csv")}
                          >
                            <Download className="w-4 h-4 mr-1" /> CSV
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              handleDownload("export-audit", "pdf")
                            }
                          >
                            <Download className="w-4 h-4 mr-1" /> Auditoría PDF
                          </Button>
                        </div>
                      </CardHeader>
                    </Card>

                    <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-base flex items-center gap-2">
                          <LayoutDashboard className="w-4 h-4 text-emerald-400" />{" "}
                          Previsualización de Datos Sanitizados
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="p-0 overflow-x-auto">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              {inspectionData.columns_summary.map(
                                (col: any) => (
                                  <TableHead key={col.name}>
                                    {col.name}
                                  </TableHead>
                                ),
                              )}
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {(
                              cleanResult.preview || inspectionData.preview
                            ).map((row: any, idx: number) => (
                              <TableRow key={idx}>
                                {inspectionData.columns_summary.map(
                                  (col: any) => (
                                    <TableCell
                                      key={col.name}
                                      className="text-xs"
                                    >
                                      {String(row[col.name] ?? "")}
                                    </TableCell>
                                  ),
                                )}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </CardContent>
                    </Card>
                  </>
                )}
              </TabsContent>

              {/* PESTAÑA 3: GRÁFICOS  */}
              <TabsContent value="charts" className="space-y-6">
                {cleanResult && (
                  <>
                    <div
                      id="charts-container"
                      className="p-4 bg-white dark:bg-slate-900 rounded-lg"
                    >
                      <DatasetCharts
                        previewData={
                          cleanResult?.preview || inspectionData?.preview
                        }
                        columnsSummary={inspectionData?.columns_summary}
                      />
                    </div>
                    <div className="flex justify-end mt-4">
                      <Button
                        onClick={handleExportPDF}
                        disabled={isExportingPDF}
                        variant="outline"
                        className="gap-2"
                      >
                        {isExportingPDF ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin text-sky-500" />
                            Procesando Gráficos y PDF...
                          </>
                        ) : (
                          <>
                            <FileChartColumn className="w-4 h-4 text-sky-500" />
                            Exportar Gráficos a PDF
                          </>
                        )}
                      </Button>
                    </div>
                  </>
                )}
              </TabsContent>
            </Tabs>
          )}
        </div>
      </div>
    </div>
  );
};
