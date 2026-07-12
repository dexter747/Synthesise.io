# Admin Login Credentials

## Admin Portal Access

**URL**: http://localhost:3001 (development) or https://admin.synthesize.io (production)

**Credentials**:
- **Email**: admin@example.com
- **Password**: <set-a-strong-password>

**Note**: These are the default admin credentials. Change them immediately in production!

## How to Seed Admin User

If the admin user doesn't exist, run:

```bash
cd apps/api
source venv/bin/activate
python -m app.seed_admin
```

This will create/update the super admin user with the credentials above.

## Admin Capabilities

The admin user has access to:
- User management (view, edit, suspend users)
- Organization management
- Subscription management
- System analytics and metrics
- API key management
- Feature flags
- Audit logs
- System health monitoring
- Billing and invoices

## Security Note

⚠️ **Important**: Change the default admin password immediately after first login in production environments!
