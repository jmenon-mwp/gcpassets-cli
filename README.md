# GCP Assets CLI

This Python CLI application helps you list and manage Google Cloud Platform (GCP) assets. It allows you to:
1.  Display the hierarchy of folders and projects under a given GCP organization or folder.
2.  List specific resource types within an organization, folder, or project.

## Setup

1.  **Prerequisites:**
    *   Python 3.9+
    *   Google Cloud SDK (`gcloud`) installed and configured.

2.  **Install Dependencies:**
    Create a `requirements.txt` file with the following content:
    ```
    google-cloud-asset
    google-api-python-client
    ```
    Then, install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Authentication:**
    *   Authenticate using Application Default Credentials:
        ```bash
        gcloud auth application-default login
        ```
    *   **Quota Project**: Ensure you have a project set for quota billing:
        ```bash
        gcloud auth application-default set-quota-project YOUR_QUOTA_PROJECT_ID
        ```
    *   **Permissions**: The credentials need:
        *   `cloudasset.assets.searchAllResources`
        *   `resourcemanager.projects.get`

## Usage

### 1. `hierarchy` - Display Asset Hierarchy

Displays folder/project hierarchy with four output formats:

**Syntax:**
```bash
gcpassets-cli.py hierarchy --scope SCOPE [--format FORMAT]
```

**Options:**
- `--scope`: GCP organization scope (e.g. `organizations/123456789`)
- `--format`: Output format (`tree`, `json`, `tabular`, `pretty`)

**Output Formats:**
- `tree` (default): Text-based tree showing org-level projects first
- `json`: Includes 'organization_projects' key for direct org projects
- `tabular`: Fixed-width table with columns: ID, Display Name, Type, Parent ID
- `pretty`: Visually enhanced tree with folder/project icons (as shown below)

**Example Output (pretty format):**
```
Scope: folders/987013313595
├── 📁 Folder1
│   └── 📄 ProjectA
├── 📁 Folder2
└── 📄 DirectProject
```

**Example:**
```bash
gcpassets-cli.py hierarchy --scope organizations/1234567890 --format tree
```

### 2. `list-resources` - List Specific Resources

Lists GCP resources within a scope with simplified output.

**Syntax:**
```bash
gcpassets-cli.py list-resources --scope SCOPE --type RESOURCE_TYPE [--format FORMAT] [--debug]
```

**Options:**
- `--scope`: GCP organization scope
- `--type`: Resource type (vm, storagebucket, etc.)
- `--format`: Output format (`tabular`, `json`, `csv`)
- `--debug`: Enable debug output

**Resource Types:**
`bqdatasets`, `buckets`, `ca`, `ca-pool`, `classicvpns`, `cloud-run`, `cloudsql`, `clusters`, `dataproc-cluster`, `disks`, `dnszones`, `filestore-instance`, `firewalls`, `gke-cluster`, `loadbalancers`, `logbucket`, `memcacheinstance`, `networkhub`, `networkspoke`, `pubsub-subscription`, `pubsub-topic`, `regiondisk`, `reservation`, `route`, `routers`, `secret`, `securitypolicy`, `serviceaccount`, `snapshot`, `spanner-instance`, `sslcert`, `sslpolicy`, `subnets`, `svcattachment`, `target-http-proxy`, `target-https-proxy`, `target-instance`, `target-pool`, `target-ssl-proxy`, `target-vpn-gateway`, `urlmap`, `vm`, `vpcs`, `vpc-connector`, `vpngateway`, `vpntunnels`

**Output:**
Simplified fixed-width table with columns: `Project_ID` and `Resource_Name`

**Examples:**
```bash
# Tabular output (default)
gcpassets-cli.py list-resources --scope folders/987013313595 --type vm

# JSON output
gcpassets-cli.py list-resources --scope folders/987013313595 --type vm --format json

# CSV output
gcpassets-cli.py list-resources --scope folders/987013313595 --type vm --format csv

# Debug mode
gcpassets-cli.py list-resources --scope folders/987013313595 --type vm --debug
```

## Notes
*   The script uses the Google Cloud Asset API to fetch asset data and the Cloud Resource Manager API to resolve project numbers to Project ID strings for more user-friendly output.
*   **Asset Type Aliases**: Uses embedded aliases for common resource types (no external files needed)

## Features

- **Hierarchy Visualization**: Display GCP resource hierarchy (organizations, folders, projects)
- **Resource Listing**: List resources of specific types within a scope
- **Output Formats**: Supports multiple output formats:
  - `tree`: Hierarchical tree view
  - `pretty`: Pretty-printed tree view
  - `json`: JSON output
  - `tabular`: Tabular output
  - `csv`: CSV output
