import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
  ScatterChart,
  Scatter,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import {
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  Flame,
  Radar as RadarIcon,
  ScatterChart as ScatterIcon,
} from "lucide-react";

interface DatasetChartsProps {
  previewData: Record<string, any>[];
  columnsSummary: Array<{
    name: string;
    data_type: string;
    missing_count: number;
    missing_percentage: number;
    unique_values_count: number;
  }>;
}

const COLORS = [
  "#00E5FF",
  "#3B82F6",
  "#8B5CF6",
  "#EC4899",
  "#10B981",
  "#F59E0B",
  "#6366F1",
  "#14B8A6",
];

export const DatasetCharts: React.FC<DatasetChartsProps> = ({
  previewData,
  columnsSummary,
}) => {
  // 1. Filtrar columnas numéricas
  const numericCols = columnsSummary.filter(
    (c) => c.data_type.includes("int") || c.data_type.includes("float"),
  );

  // 2. Filtrar columnas categóricas
  const categoricalCols = React.useMemo(() => {
    return columnsSummary.filter((c) => {
      const type = c.data_type.toLowerCase();
      return (
        type.includes("str") ||
        type.includes("string") ||
        type.includes("object")
      );
    });
  }, [columnsSummary]);

  const [selectedCategory, setSelectedCategory] = React.useState<string>(
    categoricalCols[0]?.name ?? "",
  );

  // Sincronizar el estado 
  React.useEffect(() => {
    if (categoricalCols.length > 0 && !categoricalCols.some(c => c.name === selectedCategory)) {
      setSelectedCategory(categoricalCols[0].name);
    }
  }, [categoricalCols, selectedCategory]);

  // 3. Calculo de Matriz de Correlación para el mapa de calor
  const correlationMatrix = React.useMemo(() => {
    if (numericCols.length < 2 || !previewData.length) return null;

    const keys = numericCols.map((c) => c.name);
    const matrix: { x: string; y: string; value: number }[] = [];

    keys.forEach((keyX) => {
      keys.forEach((keyY) => {
        const pairs = previewData
          .map((row) => [Number(row[keyX]), Number(row[keyY])])
          .filter(([vx, vy]) => !isNaN(vx) && !isNaN(vy));

        if (pairs.length === 0) {
          matrix.push({ x: keyX, y: keyY, value: 0 });
          return;
        }

        const meanX = pairs.reduce((acc, [x]) => acc + x, 0) / pairs.length;
        const meanY = pairs.reduce((acc, [, y]) => acc + y, 0) / pairs.length;

        let num = 0;
        let denX = 0;
        let denY = 0;

        pairs.forEach(([x, y]) => {
          const dx = x - meanX;
          const dy = y - meanY;
          num += dx * dy;
          denX += dx * dx;
          denY += dy * dy;
        });

        const den = Math.sqrt(denX * denY);
        const r = den === 0 ? (keyX === keyY ? 1 : 0) : num / den;

        matrix.push({
          x: keyX,
          y: keyY,
          value: Number(r.toFixed(2)),
        });
      });
    });

    return { keys, matrix };
  }, [numericCols, previewData]);

  // Función de color para la intensidad del Mapa de Calor
  const getHeatmapColor = (value: number) => {
    if (value === 1) return "bg-sky-500 text-white font-bold";
    if (value > 0.6) return "bg-sky-400/80 text-slate-900 font-semibold";
    if (value > 0.2)
      return "bg-sky-200/50 dark:bg-sky-900/40 text-slate-800 dark:text-slate-200";
    if (value < -0.2) return "bg-red-400/40 text-red-900 dark:text-red-200";
    return "bg-slate-100 dark:bg-slate-800 text-slate-500";
  };

  // 4. Datos para Radar Chart de Integridad por Columna 
  const radarData = columnsSummary.map((col) => ({
    columna: col.name,
    integridad: Math.max(0, 100 - col.missing_percentage),
  }));

  // 5. Datos de Frecuencia Categórica 
  const categoryFrequency = React.useMemo(() => {
    if (!selectedCategory || !previewData.length) return [];
    const counts: Record<string, number> = {};

    previewData.forEach((row) => {
      const val = String(row[selectedCategory] ?? "Sin Valor").trim();
      if (val) {
        counts[val] = (counts[val] || 0) + 1;
      }
    });

    return Object.entries(counts)
      .map(([name, cantidad]) => ({ name, cantidad }))
      .sort((a, b) => b.cantidad - a.cantidad)
      .slice(0, 8); 
  }, [selectedCategory, previewData]);

  return (
    <div id="analytics-section" className="space-y-6 pt-4">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-3">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Activity className="w-5 h-5 text-sky-500 dark:text-[var(--color-neon-blue)]" />
          Suite Completa de Análisis Visual
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Evaluación de correlaciones, integridad estructural, distribuciones y
          dispersión de variables.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* 1. MAPA DE CALOR */}
        {correlationMatrix && (
          <Card className="md:col-span-2 dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Flame className="w-4 h-4 text-amber-500" />
                Mapa de Calor: Matriz de Correlación de Pearson
              </CardTitle>
              <CardDescription className="text-xs">
                Mide el grado de relación lineal entre variables numéricas (-1 a
                1).
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-4 overflow-x-auto">
              <div className="inline-block min-w-full align-middle">
                <div
                  className="grid gap-2 text-center text-xs font-mono"
                  style={{
                    gridTemplateColumns: `120px repeat(${correlationMatrix.keys.length}, minmax(80px, 1fr))`,
                  }}
                >
                  <div className="font-bold text-slate-400 p-2 text-left">
                    Variables
                  </div>
                  {correlationMatrix.keys.map((key) => (
                    <div
                      key={key}
                      className="font-bold text-slate-700 dark:text-slate-200 p-2 truncate"
                    >
                      {key}
                    </div>
                  ))}

                  {correlationMatrix.keys.map((rowKey) => (
                    <React.Fragment key={rowKey}>
                      <div className="font-semibold text-slate-700 dark:text-slate-300 p-2 text-left truncate flex items-center">
                        {rowKey}
                      </div>
                      {correlationMatrix.keys.map((colKey) => {
                        const cell = correlationMatrix.matrix.find(
                          (m) => m.x === rowKey && m.y === colKey,
                        );
                        const val = cell ? cell.value : 0;
                        return (
                          <div
                            key={`${rowKey}-${colKey}`}
                            className={`p-3 rounded-md transition-all flex items-center justify-center ${getHeatmapColor(val)}`}
                            title={`Correlación entre ${rowKey} y ${colKey}: ${val}`}
                          >
                            {val}
                          </div>
                        );
                      })}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 2. GRÁFICO DE RADAR*/}
        <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <RadarIcon className="w-4 h-4 text-sky-500" />
              Integridad Estructural por Columna (%)
            </CardTitle>
            <CardDescription className="text-xs">
              Porcentaje de completitud de datos (sin nulos)
            </CardDescription>
          </CardHeader>
          <CardContent className="h-64 pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis
                  dataKey="columna"
                  stroke="#94a3b8"
                  fontSize={11}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[0, 100]}
                  stroke="#64748b"
                />
                <Radar
                  name="Integridad"
                  dataKey="integridad"
                  stroke="#00E5FF"
                  fill="#00E5FF"
                  fillOpacity={0.4}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    color: "#fff",
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* 3. GRÁFICO DE BARRAS */}
        <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-amber-500" />
              Faltantes por Columna
            </CardTitle>
            <CardDescription className="text-xs">
              Conteo de celdas nulas o vacías
            </CardDescription>
          </CardHeader>
          <CardContent className="h-64 pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={columnsSummary}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                <XAxis dataKey="name" stroke="#888888" fontSize={11} />
                <YAxis stroke="#888888" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    color: "#fff",
                  }}
                />
                <Bar
                  dataKey="missing_count"
                  fill="#f59e0b"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* 4. GRÁFICO DE DISPERSIÓN  */}
        {numericCols.length >= 2 && (
          <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <ScatterIcon className="w-4 h-4 text-emerald-400" />
                Dispersión: {numericCols[0].name} vs {numericCols[1].name}
              </CardTitle>
              <CardDescription className="text-xs">
                Identificación visual de sesgos y outliers
              </CardDescription>
            </CardHeader>
            <CardContent className="h-64 pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                  <XAxis
                    dataKey={numericCols[0].name}
                    name={numericCols[0].name}
                    stroke="#888888"
                    fontSize={11}
                  />
                  <YAxis
                    dataKey={numericCols[1].name}
                    name={numericCols[1].name}
                    stroke="#888888"
                    fontSize={11}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3" }}
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "#334155",
                      color: "#fff",
                    }}
                  />
                  <Scatter data={previewData} fill="#10B981" />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* 5. DISTRIBUCIÓN CATEGÓRICA */}
        {categoricalCols.length > 0 && (
          <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
            <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
              <div>
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <PieChartIcon className="w-4 h-4 text-sky-400" />
                  Distribución Categórica
                </CardTitle>
                <CardDescription className="text-xs">
                  Proporción de categorías en la muestra ({previewData.length}{" "}
                  registros)
                </CardDescription>
              </div>

              {/* Selector de columna si hay más de una */}
              {categoricalCols.length > 1 && (
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="text-xs bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded px-2 py-1 font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500"
                >
                  {categoricalCols.map((col) => (
                    <option key={col.name} value={col.name}>
                      {col.name}
                    </option>
                  ))}
                </select>
              )}
            </CardHeader>

            <CardContent className="h-64 pt-2">
              {categoryFrequency.length === 0 ? (
                <div className="h-full flex items-center justify-center text-xs text-slate-500">
                  Sin datos categóricos disponibles
                </div>
              ) : categoryFrequency.length === 1 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-4">
                  <p className="text-xs text-amber-500 font-semibold mb-1">
                    Un solo valor detectado en la muestra
                  </p>
                  <span className="text-sm font-bold text-slate-700 dark:text-slate-200">
                    "{categoryFrequency[0].name}" ({categoryFrequency[0].cantidad} filas)
                  </span>
                  <p className="text-[11px] text-slate-500 mt-2">
                    Selecciona otra columna en el desplegable superior para evaluar otras distribuciones.
                  </p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryFrequency}
                      cx="50%"
                      cy="45%"
                      innerRadius={45}
                      outerRadius={65}
                      paddingAngle={3}
                      dataKey="cantidad"
                    >
                      {categoryFrequency.map((_, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        borderColor: "#334155",
                        color: "#fff",
                      }}
                      formatter={(value: any) => [`${value} filas`, "Cantidad"]}
                    />
                    <Legend
                      layout="horizontal"
                      verticalAlign="bottom"
                      align="center"
                      wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};