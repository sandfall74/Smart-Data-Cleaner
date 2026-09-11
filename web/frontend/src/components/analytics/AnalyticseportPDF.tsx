import React from 'react';
import { Document, Page, Text, View, Image, StyleSheet } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  page: { padding: 35, fontFamily: 'Helvetica', backgroundColor: '#FFFFFF' },
  header: { marginBottom: 20, borderBottomWidth: 1, borderBottomColor: '#E2E8F0', pb: 10 },
  title: { fontSize: 20, fontWeight: 'bold', color: '#0F172A' },
  subtitle: { fontSize: 10, color: '#64748B', marginTop: 4 },
  section: { marginTop: 15, marginBottom: 15 },
  sectionTitle: { fontSize: 12, fontWeight: 'bold', color: '#0284C7', marginBottom: 8 },
  statsGrid: { flexDirection: 'row', gap: 15, marginBottom: 15 },
  statCard: { flex: 1, backgroundColor: '#F8FAFC', padding: 10, borderRadius: 4, borderWidth: 1, borderColor: '#E2E8F0' },
  statLabel: { fontSize: 8, color: '#64748B' },
  statValue: { fontSize: 14, fontWeight: 'bold', color: '#0F172A', marginTop: 2 },
  chartImage: { width: '100%', height: 'auto', borderRadius: 4, marginTop: 10 }
});

interface PDFProps {
  columnsSummary: any[];
  totalRows: number;
  chartImages?: string[];
}

export const AnalyticsReportPDF: React.FC<PDFProps> = ({ columnsSummary, totalRows, chartImages = [] }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      {/* Encabezado */}
      <View style={styles.header}>
        <Text style={styles.title}>Reporte de Análisis & Calidad de Datos</Text>
        <Text style={styles.subtitle}>Generado automáticamente por el Módulo de Limpieza</Text>
      </View>

      {/* Resumen Métrico */}
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={styles.statLabel}>TOTAL REGISTROS</Text>
          <Text style={styles.statValue}>{totalRows}</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statLabel}>TOTAL COLUMNAS</Text>
          <Text style={styles.statValue}>{columnsSummary.length}</Text>
        </View>
      </View>

      {/* Visualización de Gráficos */}
      {chartImages.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Visualizaciones Sanitizadas</Text>
          {chartImages.map((img, index) => (
            <Image key={index} src={img} style={styles.chartImage} />
          ))}
        </View>
      )}
    </Page>
  </Document>
);