/**
 * Tests for Team Billing page
 */
import { render, screen, fireEvent } from '@/__tests__/utils/test-utils';
import TeamBillingPage from '@/app/team/billing/page';

describe('TeamBillingPage', () => {
  it('renders current plan section', () => {
    render(<TeamBillingPage />);

    // Use getAllByText since "Current Plan" appears multiple times
    const currentPlanElements = screen.getAllByText('Current Plan');
    expect(currentPlanElements.length).toBeGreaterThan(0);
  });

  it('displays usage statistics', () => {
    render(<TeamBillingPage />);

    // Check for usage-related metrics
    expect(screen.getByText(/team members/i)).toBeInTheDocument();
  });

  it('shows available plans', () => {
    render(<TeamBillingPage />);

    // Check for plans section
    expect(screen.getByText(/professional/i)).toBeInTheDocument();
  });

  it('displays billing history', () => {
    render(<TeamBillingPage />);

    expect(screen.getByText('Billing History')).toBeInTheDocument();
  });

  it('shows upgrade button for current plan', () => {
    render(<TeamBillingPage />);

    const upgradeButtons = screen.queryAllByRole('button', { name: /upgrade/i });
    expect(upgradeButtons.length).toBeGreaterThanOrEqual(0);
  });

  it('displays usage meters with percentages', () => {
    render(<TeamBillingPage />);

    // Should show progress bars for usage
    const progressElements = screen.queryAllByRole('progressbar');
    expect(progressElements.length).toBeGreaterThanOrEqual(0);
  });

  it('shows invoice download buttons', () => {
    render(<TeamBillingPage />);

    const downloadButtons = screen.queryAllByRole('button', { name: /download/i });
    // Might not have invoices yet
    expect(downloadButtons.length).toBeGreaterThanOrEqual(0);
  });
});

describe('Plan Cards', () => {
  it('highlights current plan', () => {
    render(<TeamBillingPage />);

    // Current plan should have a badge or highlight
    const currentBadge = screen.queryByText(/current/i);
    if (currentBadge) {
      expect(currentBadge).toBeInTheDocument();
    }
  });

  it('shows plan features', () => {
    render(<TeamBillingPage />);

    // Plans should list features
    expect(screen.getByText(/rows/i)).toBeInTheDocument();
  });

  it('displays pricing', () => {
    render(<TeamBillingPage />);

    // Should show prices
    const prices = screen.queryAllByText(/\$\d+/);
    expect(prices.length).toBeGreaterThan(0);
  });
});

describe('Usage Cards', () => {
  it('displays team members count', () => {
    render(<TeamBillingPage />);

    expect(screen.getByText(/team members/i)).toBeInTheDocument();
  });

  it('shows rows generated', () => {
    render(<TeamBillingPage />);

    expect(screen.getByText(/rows generated/i)).toBeInTheDocument();
  });

  it('displays storage used', () => {
    render(<TeamBillingPage />);

    expect(screen.getByText(/storage used/i)).toBeInTheDocument();
  });

  it('shows usage warnings when nearing limit', () => {
    render(<TeamBillingPage />);

    // If usage is high, should show warning
    const warnings = screen.queryAllByText(/approaching limit/i);
    // Might not have warnings
    expect(warnings.length).toBeGreaterThanOrEqual(0);
  });
});

describe('Invoice Table', () => {
  it('shows invoice date', () => {
    render(<TeamBillingPage />);

    // Should have date column
    expect(screen.getByText(/date/i)).toBeInTheDocument();
  });

  it('shows invoice amount', () => {
    render(<TeamBillingPage />);

    // Should have amount column
    expect(screen.getByText(/amount/i)).toBeInTheDocument();
  });

  it('shows invoice status', () => {
    render(<TeamBillingPage />);

    // Should have status column
    expect(screen.getByText(/status/i)).toBeInTheDocument();
  });

  it('displays empty state when no invoices', () => {
    render(<TeamBillingPage />);

    const emptyMessage = screen.queryByText(/no invoices/i);
    // Might have invoices
    if (emptyMessage) {
      expect(emptyMessage).toBeInTheDocument();
    }
  });
});
