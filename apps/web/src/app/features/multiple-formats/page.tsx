"use client";

import { FeatureHero } from "@/components/features/feature-hero";
import { FeatureDetail } from "@/components/features/feature-detail";
import { FileJson, FileText, Database, Table, File, Download } from "lucide-react";

export default function MultipleFormatsPage() {
  return (
    <>
      <FeatureHero
        title="Multiple Formats"
        subtitle="Flexible Exports"
        description="Export your synthetic data in any format you need. From CSV and JSON to SQL scripts and Parquet files, we've got you covered."
        icon={FileJson}
        features={[
          "CSV export",
          "JSON format",
          "SQL scripts",
          "Parquet files",
          "Excel support",
          "Custom formats",
        ]}
        ctaText="Try Export"
        ctaLink="/auth/login"
      />
      <FeatureDetail
        title="Export in Any Format You Need"
        description="Different tools need different formats. Export your synthetic data in the format that works best for your workflow."
        stats={[
          { value: "6+", label: "Format Options" },
          { value: "Instant", label: "Downloads" },
          { value: "Any Size", label: "Export Limit" },
          { value: "Custom", label: "Delimiters" },
        ]}
        benefits={[
          {
            icon: FileText,
            title: "CSV Export",
            description: "Industry-standard CSV format with customizable delimiters, quote characters, and encoding. Perfect for spreadsheets and data analysis tools.",
          },
          {
            icon: FileJson,
            title: "JSON Format",
            description: "Export as JSON or JSONL (newline-delimited) for easy integration with APIs, NoSQL databases, and modern web applications.",
          },
          {
            icon: Database,
            title: "SQL Scripts",
            description: "Ready-to-execute SQL INSERT statements for any database. Includes CREATE TABLE statements and proper escaping for safe imports.",
          },
          {
            icon: Table,
            title: "Parquet Files",
            description: "Columnar storage format optimized for big data tools like Spark, Athena, and data warehouses. Compressed and incredibly fast.",
          },
          {
            icon: File,
            title: "Excel Support",
            description: "Export directly to XLSX format for business users. Includes formatted headers, data types, and works with Excel, Google Sheets, and Numbers.",
          },
          {
            icon: Download,
            title: "Custom Formats",
            description: "Need a specific format? Our API supports custom transformations and formatters. Contact us for enterprise-specific format requirements.",
          },
        ]}
      />
    </>
  );
}
