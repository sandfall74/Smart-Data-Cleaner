import React from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Zap,
  FileCode2
} from "lucide-react";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../components/ui/card";

export const Home: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto px-4 py-12 space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-6">
        <div className="inline-block px-4 py-1.5 rounded-full text-xs font-semibold bg-sky-100 dark:bg-slate-800 text-sky-600 dark:text-[var(--color-neon-blue)] border border-sky-300 dark:border-sky-500/30">
          FastAPI + React 19 + TypeScript Engine
        </div>
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          Limpieza de Datos Empresarial <br />
          <span className="text-sky-500 dark:text-[var(--color-neon-blue)] dark:neon-text-glow">
            Automatizada y Precisa
          </span>
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
          Plataforma web para sanitizar, imputar valores nulos, eliminar
          duplicados y exportar datasets con reportes de auditoría listos para
          producción.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <Link to="/app">
            <Button
              size="lg"
              className="font-bold gap-2 dark:bg-[var(--color-neon-blue)] dark:text-black dark:hover:bg-cyan-400 dark:neon-glow"
            >
              Comenzar a Limpiar <ArrowRight className="w-5 h-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Origen del Proyecto */}
      <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl text-slate-900 dark:text-white">
            <Zap className="text-sky-500 dark:text-[var(--color-neon-blue)]" />
            ¿Cómo surgió el proyecto?
          </CardTitle>
        </CardHeader>
        <CardContent className="text-slate-600 dark:text-slate-300 leading-relaxed space-y-3">
          <p>
            El origen de esta plataforma surge con la meta de{" "}
            <strong>
              modernizar y escalar un proyecto universitario previo desarrollado
              en Streamlit
            </strong>
            . Aunque Streamlit resultaba útil para prototipos rápidos, limitaba
            la personalización visual, el rendimiento con datasets grandes y la
            arquitectura del sistema.
          </p>
          <p>
            Para llevar la herramienta a un nivel profesional y grado
            corporativo, se migró hacia una arquitectura desacoplada: un motor
            backend robusto en <strong>FastAPI con Pandas</strong> y un frontend
            dinámico en <strong>React, TypeScript y Tailwind CSS</strong>.
          </p>
        </CardContent>
      </Card>

      {/* Documentación */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <FileCode2 className="text-sky-500 dark:text-[var(--color-neon-blue)]" />
          Documentación de Operaciones
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
            <CardHeader>
              <CardTitle className="text-sky-500 dark:text-[var(--color-neon-blue)] text-xl">
                01. Carga
              </CardTitle>
              <CardDescription className="dark:text-slate-400">
                Archivos CSV o Excel
              </CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-slate-600 dark:text-slate-300">
              Soporte para múltiples encodigs (UTF-8, Latin-1) y autodetección
              de tipos de columnas.
            </CardContent>
          </Card>

          <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
            <CardHeader>
              <CardTitle className="text-sky-500 dark:text-[var(--color-neon-blue)] text-xl">
                02. Sanitización
              </CardTitle>
              <CardDescription className="dark:text-slate-400">
                Reglas configurables
              </CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-slate-600 dark:text-slate-300">
              Imputación por media/mediana, eliminación de duplicados, trimming
              de espacios y normalización de textos.
            </CardContent>
          </Card>

          <Card className="dark:bg-[var(--color-neon-card)] dark:border-[var(--color-neon-border)]">
            <CardHeader>
              <CardTitle className="text-sky-500 dark:text-[var(--color-neon-blue)] text-xl">
                03. Exportación
              </CardTitle>
              <CardDescription className="dark:text-slate-400">
                Formatos y Auditoría
              </CardDescription>
            </CardHeader>
            <CardContent className="text-sm text-slate-600 dark:text-slate-300">
              Descarga del dataset corregido y generación instantánea de reporte
              PDF de auditoría con FPDF2.
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
