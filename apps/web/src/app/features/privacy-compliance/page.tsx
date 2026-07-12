"use client";

import { FeatureHero } from "@/components/features/feature-hero";
import { FeatureDetail } from "@/components/features/feature-detail";
import { Shield, Lock, FileCheck, Eye, Database, CheckCircle } from "lucide-react";

export default function PrivacyCompliancePage() {
  return (
    <>
      <FeatureHero
        title="Privacy Compliant"
        subtitle="Enterprise Security"
        description="100% synthetic data that's fully compliant with GDPR, HIPAA, and CCPA. No real customer data ever touches our platform."
        icon={Shield}
        features={[
          "GDPR compliant",
          "HIPAA ready",
          "CCPA compliant",
          "SOC2 certified",
          "Zero PII risk",
          "Audit logs",
        ]}
        ctaText="Learn More"
        ctaLink="/auth/login"
      />
      <FeatureDetail
        title="Enterprise-Grade Privacy & Compliance"
        description="Protect your business with synthetic data that eliminates privacy risks. Fully compliant with global regulations out of the box."
        stats={[
          { value: "100%", label: "Synthetic Data" },
          { value: "Zero", label: "PII Exposure" },
          { value: "SOC2", label: "Certified" },
          { value: "Global", label: "Compliance" },
        ]}
        benefits={[
          {
            icon: Shield,
            title: "GDPR Compliant",
            description: "Fully compliant with EU General Data Protection Regulation. Synthetic data means zero personal data processing, eliminating GDPR risks entirely.",
          },
          {
            icon: Lock,
            title: "HIPAA Ready",
            description: "Generate healthcare data without PHI concerns. Our synthetic data is perfect for healthcare applications requiring HIPAA compliance.",
          },
          {
            icon: FileCheck,
            title: "CCPA Compliant",
            description: "Meet California Consumer Privacy Act requirements automatically. No personal information means no consumer data rights to manage.",
          },
          {
            icon: Eye,
            title: "Zero PII Risk",
            description: "Completely eliminate the risk of exposing personally identifiable information. Our synthetic data contains zero traces of real individuals.",
          },
          {
            icon: Database,
            title: "Audit Logs",
            description: "Complete audit trail of all data generation activities. Track who generated what, when, and how for compliance reporting and security monitoring.",
          },
          {
            icon: CheckCircle,
            title: "SOC2 Certified",
            description: "SOC2 Type II certified infrastructure. We maintain the highest security standards so you can trust us with your synthetic data generation.",
          },
        ]}
      />
    </>
  );
}
