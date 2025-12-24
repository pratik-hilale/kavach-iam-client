# iam-client

A lightweight, production-ready **IAM client SDK** for backend services.

This package allows backend services to securely communicate with the
Identity and Access Management (IAM) system using **service credentials**.

---

## ✨ Features

- Service-to-service authentication
- Automatic service token retrieval
- Token introspection
- Fetch user details by user ID
- Clean, minimal Python API
- Designed for FastAPI backends

---

## 📦 Installation

### Install directly from GitHub

```bash
pip install git+https://github.com/YOUR_ORG/iam-client.git
```


### Install directly from GitHub

```bash
pip install git+https://github.com/YOUR_ORG/iam-client.git@v0.1.0
```


## ✨ Configuration
Set the following environment variables in the consuming backend service:
```
IAM_BASE_URL=https://iam.xyz.com
TENANT_SLUG=xyz
IAM_CLIENT_ID=xyz-backend
IAM_CLIENT_SECRET=super-secret
```

## ✨ Usage
### Create IAM client (once per service)
```
from iam_client.client import IAMClient

iam = IAMClient(
    base_url="https://iam.xyz.com",
    tenant_slug="xyz",
    client_id="xyz-backend",
    client_secret="super-secret",
)
```