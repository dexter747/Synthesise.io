import LegalLayout from "../layout-client";

export const metadata = {
  title: "Cookie Policy | Synthesize.io",
  description: "Cookie policy for Synthesize.io synthetic data generation platform",
};

export default function CookiePolicyPage() {
  return (
    <LegalLayout title="Cookie Policy" lastUpdated="January 15, 2025">
      <h2>1. What Are Cookies?</h2>
      <p>
        Cookies are small text files that are placed on your device when you visit a website. 
        They are widely used to make websites work more efficiently, provide a better user 
        experience, and give website owners useful information about how their site is being used.
      </p>

      <h2>2. How We Use Cookies</h2>
      <p>
        Synthesize.io uses cookies and similar technologies for several purposes:
      </p>
      <ul>
        <li><strong>Essential functionality:</strong> To enable core features like authentication and security</li>
        <li><strong>Analytics:</strong> To understand how visitors interact with our platform</li>
        <li><strong>Personalization:</strong> To remember your preferences and settings</li>
        <li><strong>Marketing:</strong> To deliver relevant advertisements and measure campaign effectiveness</li>
      </ul>

      <h2>3. Types of Cookies We Use</h2>

      <h3>3.1 Necessary Cookies</h3>
      <p>
        These cookies are essential for the website to function properly. They enable basic 
        functions like page navigation, secure login, and access to secure areas. The website 
        cannot function properly without these cookies, and they cannot be disabled.
      </p>
      <table className="w-full border-collapse border border-white/10 my-4">
        <thead>
          <tr className="bg-white/5">
            <th className="border border-white/10 p-3 text-left">Cookie Name</th>
            <th className="border border-white/10 p-3 text-left">Purpose</th>
            <th className="border border-white/10 p-3 text-left">Duration</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="border border-white/10 p-3">synthesize_session</td>
            <td className="border border-white/10 p-3">Maintains user session</td>
            <td className="border border-white/10 p-3">Session</td>
          </tr>
          <tr>
            <td className="border border-white/10 p-3">synthesize_csrf</td>
            <td className="border border-white/10 p-3">Security token</td>
            <td className="border border-white/10 p-3">Session</td>
          </tr>
          <tr>
            <td className="border border-white/10 p-3">synthesize_cookie_consent</td>
            <td className="border border-white/10 p-3">Stores cookie preferences</td>
            <td className="border border-white/10 p-3">1 year</td>
          </tr>
        </tbody>
      </table>

      <h3>3.2 Analytics Cookies</h3>
      <p>
        These cookies help us understand how visitors interact with our website by collecting 
        and reporting information anonymously. This helps us improve our platform.
      </p>
      <table className="w-full border-collapse border border-white/10 my-4">
        <thead>
          <tr className="bg-white/5">
            <th className="border border-white/10 p-3 text-left">Cookie Name</th>
            <th className="border border-white/10 p-3 text-left">Provider</th>
            <th className="border border-white/10 p-3 text-left">Purpose</th>
            <th className="border border-white/10 p-3 text-left">Duration</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="border border-white/10 p-3">_ga</td>
            <td className="border border-white/10 p-3">Google Analytics</td>
            <td className="border border-white/10 p-3">Distinguishes users</td>
            <td className="border border-white/10 p-3">2 years</td>
          </tr>
          <tr>
            <td className="border border-white/10 p-3">_gid</td>
            <td className="border border-white/10 p-3">Google Analytics</td>
            <td className="border border-white/10 p-3">Distinguishes users</td>
            <td className="border border-white/10 p-3">24 hours</td>
          </tr>
          <tr>
            <td className="border border-white/10 p-3">mp_*</td>
            <td className="border border-white/10 p-3">Mixpanel</td>
            <td className="border border-white/10 p-3">Product analytics</td>
            <td className="border border-white/10 p-3">1 year</td>
          </tr>
        </tbody>
      </table>

      <h3>3.3 Functional Cookies</h3>
      <p>
        These cookies enable enhanced functionality and personalization, such as remembering 
        your preferences, language settings, and customizations.
      </p>
      <table className="w-full border-collapse border border-white/10 my-4">
        <thead>
          <tr className="bg-white/5">
            <th className="border border-white/10 p-3 text-left">Cookie Name</th>
            <th className="border border-white/10 p-3 text-left">Purpose</th>
            <th className="border border-white/10 p-3 text-left">Duration</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="border border-white/10 p-3">synthesize_theme</td>
            <td className="border border-white/10 p-3">Theme preference</td>
            <td className="border border-white/10 p-3">1 year</td>
          </tr>
          <tr>
            <td className="border border-white/10 p-3">synthesize_locale</td>
            <td className="border border-white/10 p-3">Language preference</td>
            <td className="border border-white/10 p-3">1 year</td>
          </tr>
        </tbody>
      </table>

      <h3>3.4 Marketing Cookies</h3>
      <p>
        These cookies are used to track visitors across websites to display relevant 
        advertisements and measure the effectiveness of advertising campaigns.
      </p>
      <table className="w-full border-collapse border border-white/10 my-4">
        <thead>
          <tr className="bg-white/5">
            <th className="border border-white/10 p-3 text-left">Cookie Name</th>
            <th className="border border-white/10 p-3 text-left">Provider</th>
            <th className="border border-white/10 p-3 text-left">Purpose</th>
            <th className="border border-white/10 p-3 text-left">Duration</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="border border-white/10 p-3">_fbp</td>
            <td className="border border-white/10 p-3">Facebook</td>
            <td className="border border-white/10 p-3">Ad targeting</td>
            <td className="border border-white/10 p-3">3 months</td>
          </tr>
          <tr>
            <td className="border border-white/10 p-3">_gcl_au</td>
            <td className="border border-white/10 p-3">Google Ads</td>
            <td className="border border-white/10 p-3">Conversion tracking</td>
            <td className="border border-white/10 p-3">3 months</td>
          </tr>
        </tbody>
      </table>

      <h2>4. Managing Cookie Preferences</h2>
      <p>
        You can manage your cookie preferences at any time by clicking the "Cookie Settings" 
        link in our website footer or by adjusting your browser settings.
      </p>

      <h3>4.1 Browser Settings</h3>
      <p>
        Most web browsers allow you to control cookies through their settings. Here are links 
        to instructions for common browsers:
      </p>
      <ul>
        <li><a href="https://support.google.com/chrome/answer/95647">Google Chrome</a></li>
        <li><a href="https://support.mozilla.org/en-US/kb/cookies-information-websites-store-on-your-computer">Mozilla Firefox</a></li>
        <li><a href="https://support.apple.com/guide/safari/manage-cookies-sfri11471/mac">Safari</a></li>
        <li><a href="https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09">Microsoft Edge</a></li>
      </ul>

      <h3>4.2 Opt-Out Tools</h3>
      <p>You can also opt out of specific tracking using these tools:</p>
      <ul>
        <li><a href="https://tools.google.com/dlpage/gaoptout">Google Analytics Opt-out</a></li>
        <li><a href="https://www.youronlinechoices.com/">Your Online Choices (EU)</a></li>
        <li><a href="https://optout.networkadvertising.org/">Network Advertising Initiative</a></li>
      </ul>

      <h2>5. Do Not Track</h2>
      <p>
        Some browsers have a "Do Not Track" feature that signals to websites that you do not 
        want to have your online activity tracked. Currently, there is no uniform standard for 
        how websites should respond to these signals. We do not currently respond to DNT signals.
      </p>

      <h2>6. Third-Party Cookies</h2>
      <p>
        In addition to our own cookies, we may also use various third-party cookies to report 
        usage statistics, deliver advertisements, and so on. These third parties have their 
        own privacy policies governing how they use information.
      </p>

      <h2>7. Updates to This Policy</h2>
      <p>
        We may update this Cookie Policy from time to time to reflect changes in technology, 
        legislation, or our data practices. When we make changes, we will update the "Last 
        updated" date at the top of this policy.
      </p>

      <h2>8. Contact Us</h2>
      <p>If you have questions about our use of cookies:</p>
      <ul>
        <li><strong>Email:</strong> privacy@synthesize.io</li>
        <li><strong>Address:</strong> Synthesize.io, [Company Address]</li>
      </ul>
    </LegalLayout>
  );
}
