"use client";

import { FeatureHero } from "@/components/features/feature-hero";
import { FeatureDetail } from "@/components/features/feature-detail";
import { Database, Link2, GitBranch, CheckCircle, Table, Network } from "lucide-react";

export default function RelationalDataPage() {
  return (
    <>
      <FeatureHero
        title="Relational Data"
        subtitle="Smart Relationships"
        description="Generate complex datasets with foreign keys and referential integrity. Create realistic multi-table schemas that mirror your production database."
        icon={Database}
        features={[
          "Foreign keys",
          "Referential integrity",
          "Multi-table schemas",
          "Custom relationships",
          "Data consistency",
          "Schema import",
        ]}
        ctaText="Explore"
        ctaLink="/auth/login"
      />
      <FeatureDetail
        title="Complex Relationships Made Simple"
        description="Real-world data isn't flat. Generate synthetic data that maintains all the complex relationships between tables, just like your production database."
        stats={[
          { value: "Unlimited", label: "Tables" },
          { value: "Auto", label: "FK Resolution" },
          { value: "100%", label: "Integrity" },
          { value: "Multi-DB", label: "Support" },
        ]}
        benefits={[
          {
            icon: Link2,
            title: "Foreign Key Support",
            description: "Automatically maintain foreign key relationships across tables. Our engine ensures all references are valid and consistent throughout your dataset.",
          },
          {
            icon: CheckCircle,
            title: "Referential Integrity",
            description: "100% referential integrity guaranteed. No orphaned records, no broken relationships. Your synthetic data behaves exactly like production data.",
          },
          {
            icon: Table,
            title: "Multi-Table Schemas",
            description: "Generate entire database schemas with dozens of interconnected tables. Perfect for testing complex applications with realistic data relationships.",
          },
          {
            icon: GitBranch,
            title: "Custom Relationships",
            description: "Define one-to-many, many-to-many, and hierarchical relationships. Our flexible schema designer handles any relationship complexity.",
          },
          {
            icon: Database,
            title: "Schema Import",
            description: "Import your existing database schema automatically. We'll analyze relationships and generate matching synthetic data in minutes.",
          },
          {
            icon: Network,
            title: "Cross-Database Support",
            description: "Works with PostgreSQL, MySQL, SQL Server, and more. Generate synthetic data that matches your database's specific constraints and data types.",
          },
        ]}
      />
    </>
  );
}
