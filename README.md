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
python3 gcpassets-cli.py hierarchy --parent <PARENT_RESOURCE> [--output_format <FORMAT>]
```

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
python3 gcpassets-cli.py hierarchy --parent organizations/1234567890 --output_format tree
```

### 2. `list-resources` - List Specific Resources

Lists GCP resources within a scope with simplified output.

**Syntax:**
```bash
python3 gcpassets-cli.py list-resources --type <RESOURCE_TYPE> --scope <SCOPE> [--format <FORMAT>] [--debug]
```

**Options:**
- `--type`: Resource type to list (vm, storagebucket, clusters, cloudsql, vpcs, loadbalancers, classicvpns, bqdatasets, disks, routers, etc.)
- `--scope`: Search scope (organizations/ID, folders/ID, projects/ID)
- `--format`: Output format (`tabular` (default), `json`)
- `--debug`: Show debug information including API responses

**Resource Types:**
`vm`, `storagebucket`, `clusters`, `cloudsql`, `vpcs`, `loadbalancers`, `classicvpns`, `bqdatasets`, `disks`, `routers`, `dnszones`, `vpntunnels`, `firewalls`, `subnets`

**Output:**
Simplified fixed-width table with columns: `Project_ID` and `Resource_Name`

**Examples:**
```bash
# Tabular output (default)
python3 gcpassets-cli.py list-resources --type vm --scope folders/987013313595

# JSON output
python3 gcpassets-cli.py list-resources --type vm --scope folders/987013313595 --format json

# Debug mode
python3 gcpassets-cli.py list-resources --type vm --scope folders/987013313595 --debug
```

## Notes
*   The script uses the Google Cloud Asset API to fetch asset data and the Cloud Resource Manager API to resolve project numbers to Project ID strings for more user-friendly output.
