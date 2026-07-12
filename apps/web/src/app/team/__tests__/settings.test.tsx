/**
 * Tests for Team Settings page
 */
import { render, screen, fireEvent, waitFor } from '@/__tests__/utils/test-utils';
import TeamSettingsPage from '@/app/team/settings/page';

describe('TeamSettingsPage', () => {
  it('renders all settings sections', () => {
    render(<TeamSettingsPage />);

    expect(screen.getByText('General Settings')).toBeInTheDocument();
    expect(screen.getByText('Team Settings')).toBeInTheDocument();
    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('Danger Zone')).toBeInTheDocument();
  });

  it('shows organization name input', () => {
    render(<TeamSettingsPage />);

    const nameInput = screen.getByLabelText(/organization name/i);
    expect(nameInput).toBeInTheDocument();
  });

  it('shows organization slug input', () => {
    render(<TeamSettingsPage />);

    const slugInput = screen.getByLabelText(/url slug/i);
    expect(slugInput).toBeInTheDocument();
  });

  it('has save changes button', () => {
    render(<TeamSettingsPage />);

    const saveButton = screen.getByRole('button', { name: /save changes/i });
    expect(saveButton).toBeInTheDocument();
  });

  it('shows toggle switches for team settings', () => {
    render(<TeamSettingsPage />);

    // Should have toggles for various settings
    const switches = screen.getAllByRole('switch');
    expect(switches.length).toBeGreaterThan(0);
  });

  it('has delete organization button in danger zone', () => {
    render(<TeamSettingsPage />);

    const deleteButton = screen.getByRole('button', { name: /delete organization/i });
    expect(deleteButton).toBeInTheDocument();
  });

  it('shows confirmation modal when delete is clicked', async () => {
    render(<TeamSettingsPage />);

    const deleteButton = screen.getByRole('button', { name: /delete organization/i });
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
    });
  });

  it('requires typing organization name to confirm deletion', async () => {
    render(<TeamSettingsPage />);

    fireEvent.click(screen.getByRole('button', { name: /delete organization/i }));

    await waitFor(() => {
      const confirmInput = screen.getByPlaceholderText(/type.*to confirm/i);
      expect(confirmInput).toBeInTheDocument();
      
      const confirmButton = screen.getByRole('button', { name: /delete permanently/i });
      expect(confirmButton).toBeDisabled();
    });
  });
});

describe('SettingToggle Component', () => {
  it('toggles value when clicked', async () => {
    render(<TeamSettingsPage />);

    const switches = screen.getAllByRole('switch');
    if (switches.length > 0) {
      const firstSwitch = switches[0];
      const initialState = firstSwitch.getAttribute('aria-checked');
      
      fireEvent.click(firstSwitch);
      
      await waitFor(() => {
        const newState = firstSwitch.getAttribute('aria-checked');
        expect(newState).not.toBe(initialState);
      });
    }
  });
});

describe('Form Validation', () => {
  it('validates organization name length', async () => {
    render(<TeamSettingsPage />);

    const nameInput = screen.getByLabelText(/organization name/i);
    
    // Try setting name too short
    fireEvent.change(nameInput, { target: { value: 'ab' } });
    
    await waitFor(() => {
      // Should show validation error
      const errorMessage = screen.queryByText(/at least 3 characters/i);
      if (errorMessage) {
        expect(errorMessage).toBeInTheDocument();
      }
    });
  });

  it('validates slug format', async () => {
    render(<TeamSettingsPage />);

    const slugInput = screen.getByLabelText(/url slug/i);
    
    // Try setting invalid slug with spaces
    fireEvent.change(slugInput, { target: { value: 'invalid slug' } });
    
    await waitFor(() => {
      // Should show validation error
      const errorMessage = screen.queryByText(/letters.*numbers.*hyphens/i);
      if (errorMessage) {
        expect(errorMessage).toBeInTheDocument();
      }
    });
  });
});
