import LegalLayout from "../layout-client";

export const metadata = {
  title: "Refund Policy | Synthesize.io",
  description: "Refund policy for Synthesize.io synthetic data generation platform",
};

export default function RefundPolicyPage() {
  return (
    <LegalLayout title="Refund Policy" lastUpdated="January 15, 2025">
      <h2>1. Overview</h2>
      <p>
        At Synthesize.io, we want you to be completely satisfied with our service. This Refund 
        Policy outlines the terms and conditions for refunds on our subscription plans.
      </p>

      <h2>2. Free Trial</h2>
      <p>
        We offer a <strong>14-day free trial</strong> for new users to evaluate our platform. 
        During the trial period, you have access to all features of the plan you select. No 
        payment is required during the trial, and you can cancel at any time without charge.
      </p>
      <p>
        We strongly recommend using the trial period to ensure our service meets your needs 
        before committing to a paid subscription.
      </p>

      <h2>3. Subscription Refunds</h2>

      <h3>3.1 Monthly Subscriptions</h3>
      <ul>
        <li>
          <strong>Within 7 days:</strong> Full refund available if you're not satisfied with the 
          service and have not generated more than 100,000 rows of data
        </li>
        <li>
          <strong>After 7 days:</strong> No refunds available; you may cancel to prevent future charges
        </li>
      </ul>

      <h3>3.2 Annual Subscriptions</h3>
      <ul>
        <li>
          <strong>Within 14 days:</strong> Full refund available if you're not satisfied with the 
          service and have not generated more than 500,000 rows of data
        </li>
        <li>
          <strong>After 14 days:</strong> Pro-rated refund available for unused months, minus a 
          10% administrative fee
        </li>
        <li>
          <strong>After 30 days:</strong> No refunds available; you may cancel to prevent renewal
        </li>
      </ul>

      <h2>4. Enterprise Plans</h2>
      <p>
        Enterprise plan refunds are handled on a case-by-case basis according to the terms of 
        your contract. Please contact your account manager or email enterprise@synthesize.io 
        for assistance.
      </p>

      <h2>5. Eligible Refund Circumstances</h2>
      <p>We may issue refunds in the following circumstances:</p>
      <ul>
        <li>Technical issues preventing use of the service that we cannot resolve</li>
        <li>Accidental duplicate charges</li>
        <li>Significant service outages affecting your ability to use the platform</li>
        <li>Major feature changes that fundamentally alter the service you purchased</li>
      </ul>

      <h2>6. Non-Refundable Items</h2>
      <p>The following are not eligible for refunds:</p>
      <ul>
        <li>Partial month usage after the refund eligibility period</li>
        <li>Usage that exceeds the data generation thresholds mentioned above</li>
        <li>Accounts terminated due to Terms of Service violations</li>
        <li>Upgrades or add-ons purchased mid-billing cycle</li>
        <li>Customization or consulting services</li>
      </ul>

      <h2>7. How to Request a Refund</h2>
      <p>To request a refund:</p>
      <ol>
        <li>Log into your account and go to <strong>Settings → Billing</strong></li>
        <li>Click on <strong>"Request Refund"</strong></li>
        <li>Provide the reason for your refund request</li>
        <li>Submit your request</li>
      </ol>
      <p>
        Alternatively, you can email <strong>billing@synthesize.io</strong> with your account 
        email, subscription details, and reason for the refund request.
      </p>

      <h2>8. Refund Processing</h2>
      <ul>
        <li>
          <strong>Review Time:</strong> We will review refund requests within 3-5 business days
        </li>
        <li>
          <strong>Notification:</strong> You will receive an email notification with the outcome 
          of your request
        </li>
        <li>
          <strong>Processing Time:</strong> Approved refunds are processed within 5-10 business 
          days, depending on your payment method
        </li>
        <li>
          <strong>Currency:</strong> Refunds are issued in the original currency of payment
        </li>
      </ul>

      <h2>9. Cancellation vs. Refund</h2>
      <p>
        Please note the difference between cancellation and refund:
      </p>
      <ul>
        <li>
          <strong>Cancellation:</strong> Stops future billing; you retain access until the end 
          of your current billing period
        </li>
        <li>
          <strong>Refund:</strong> Returns payment for the current billing period; access is 
          terminated immediately upon refund approval
        </li>
      </ul>

      <h2>10. Disputes</h2>
      <p>
        If you dispute a charge with your bank or credit card company before contacting us, 
        this may affect your ability to receive a refund directly from us and may result in 
        account suspension.
      </p>
      <p>
        We encourage you to contact our support team first at billing@synthesize.io to resolve 
        any billing issues.
      </p>

      <h2>11. Changes to This Policy</h2>
      <p>
        We may update this Refund Policy from time to time. Changes will be posted on this page 
        with an updated "Last updated" date. Existing customers will be subject to the policy 
        in effect at the time of their purchase.
      </p>

      <h2>12. Contact Us</h2>
      <p>For questions about refunds or this policy:</p>
      <ul>
        <li><strong>Email:</strong> billing@synthesize.io</li>
        <li><strong>Support:</strong> support@synthesize.io</li>
      </ul>
    </LegalLayout>
  );
}
