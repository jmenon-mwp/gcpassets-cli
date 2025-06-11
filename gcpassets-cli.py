#!/usr/bin/env python3
import argparse
import csv
import itertools
import json
import os
import re
import sys
import threading
import time
from datetime import datetime, timedelta
from google.cloud import asset_v1
from google.protobuf.json_format import MessageToDict

# Embedded API type aliases
ASSET_TYPE_MAPPING = {
    'bucket': 'storage.googleapis.com/Bucket',
    'ca': 'privateca.googleapis.com/CertificateAuthority',
    'ca-pool': 'privateca.googleapis.com/CaPool',
    'cloud-run': 'run.googleapis.com/Service',
    'dataproc-cluster': 'dataproc.googleapis.com/Cluster',
    'disks': 'compute.googleapis.com/Disk',
    'dnszone': 'dns.googleapis.com/ManagedZone',
    'filestore-instance': 'file.googleapis.com/Instance',
    'gke-cluster': 'container.googleapis.com/Cluster',
    'logbucket': 'logging.googleapis.com/LogBucket',
    'memcacheinstance': 'memcache.googleapis.com/Instance',
    'networkhub': 'networkconnectivity.googleapis.com/Hub',
    'networkspoke': 'networkconnectivity.googleapis.com/Spoke',
    'project': 'compute.googleapis.com/Project',
    'pubsub-subscription': 'pubsub.googleapis.com/Subscription',
    'pubsub-topic': 'pubsub.googleapis.com/Topic',
    'regiondisk': 'compute.googleapis.com/RegionDisk',
    'reservation': 'compute.googleapis.com/Reservation',
    'route': 'compute.googleapis.com/Route',
    'router': 'compute.googleapis.com/Router',
    'secret': 'secretmanager.googleapis.com/Secret',
    'securitypolicy': 'compute.googleapis.com/SecurityPolicy',
    'serviceaccount': 'iam.googleapis.com/ServiceAccount',
    'snapshot': 'compute.googleapis.com/Snapshot',
    'spanner-instance': 'spanner.googleapis.com/Instance',
    'sql-instance': 'sqladmin.googleapis.com/Instance',
    'sslcert': 'compute.googleapis.com/SslCertificate',
    'sslpolicy': 'compute.googleapis.com/SslPolicy',
    'subnet': 'compute.googleapis.com/Subnetwork',
    'svcattachment': 'compute.googleapis.com/ServiceAttachment',
    'target-http-proxy': 'compute.googleapis.com/TargetHttpProxy',
    'target-https-proxy': 'compute.googleapis.com/TargetHttpsProxy',
    'target-instance': 'compute.googleapis.com/TargetInstance',
    'target-pool': 'compute.googleapis.com/TargetPool',
    'target-ssl-proxy': 'compute.googleapis.com/TargetSslProxy',
    'target-vpn-gateway': 'compute.googleapis.com/TargetVpnGateway',
    'urlmap': 'compute.googleapis.com/UrlMap',
    'vm': 'compute.googleapis.com/Instance',
    'vpc': 'compute.googleapis.com/Network',
    'vpc-connector': 'vpcaccess.googleapis.com/Connector',
    'vpngateway': 'compute.googleapis.com/VpnGateway',
    'vpntunnel': 'compute.googleapis.com/VpnTunnel'
}

class Spinner:
    """
    A simple spinner class for command-line interfaces
    """
    def __init__(self, message):
        self.message = message
        self.running = False
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.thread = threading.Thread(target=self._spin)

    def start(self):
        self.running = True
        self.thread.start()

    def _spin(self):
        while self.running:
            sys.stdout.write(f"\r{self.message} {next(self.spinner)}")
            sys.stdout.flush()
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.thread.join()
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
        sys.stdout.flush()

def fetch_assets(scope, debug=False):
    """
    Fetches GCP assets (organizations, folders, projects) for the given scope.

    Args:
        scope: The GCP scope to search within (e.g., organizations/1234567890)
        debug: If True, prints debug information

    Returns:
        List of asset dictionaries with their hierarchy information
    """
    client = asset_v1.AssetServiceClient()
    asset_types_to_fetch = [
        "cloudresourcemanager.googleapis.com/Organization",
        "cloudresourcemanager.googleapis.com/Folder",
        "cloudresourcemanager.googleapis.com/Project"
    ]
    assets_from_api = []
    try:
        first_resource = None
        for i, asset in enumerate(client.search_all_resources(scope=scope, asset_types=asset_types_to_fetch)):
            if i == 0:
                first_resource = asset

            assets_from_api.append({
                'name': asset.name,
                'asset_type': asset.asset_type,
                'display_name': getattr(asset, 'display_name', ''),
                'parent': asset.parent_full_resource_name.replace("//cloudresourcemanager.googleapis.com/", "")
            })
        if debug and first_resource:
            print("Debug: First resource raw data:")
            print(json.dumps(MessageToDict(first_resource._pb), indent=2))
    except Exception as e:
        print(f"Error fetching assets from GCP: {e}")
    return assets_from_api

def fetch_flat_resources(scope, asset_type, debug=False):
    """
    Fetches GCP resources of a specific type for the given scope.

    Args:
        scope: The GCP scope to search within (e.g., organizations/1234567890)
        asset_type: The type of resource to fetch (e.g., compute.googleapis.com/Instance)
        debug: If True, prints the first resource in raw format and exits

    Returns:
        List of resource dictionaries with their details
    """
    client = asset_v1.AssetServiceClient()
    resources_data = []
    seen_resources = set()
    try:
        first_resource = None
        for i, resource in enumerate(client.search_all_resources(scope=scope, asset_types=[asset_type])):
            if i == 0:
                first_resource = resource
                if debug:
                    # In debug mode, print the raw first resource and exit
                    print(json.dumps(MessageToDict(first_resource._pb), indent=2))
                    return []

            resource_dict = {
                'name': resource.name,
                'asset_type': resource.asset_type,
                'project': resource.project,
                'display_name': getattr(resource, 'display_name', ''),
                'location': getattr(resource, 'location', ''),
                'parent_full_resource_name': resource.parent_full_resource_name
            }

            # Handle BigQuery dataset duplicates
            if resource.asset_type == "bigquery.googleapis.com/Dataset":
                key = (resource_dict['project'], resource_dict['name'])
                if key in seen_resources:
                    continue
                seen_resources.add(key)
                resources_data.append(resource_dict)
            else:
                resources_data.append(resource_dict)

    except Exception as e:
        print(f"Error fetching resources from GCP: {e}")
    return resources_data

def fetch_folder_hierarchy(scope, debug=False):
    """
    Fetches folder hierarchy from GCP

    Args:
        scope: GCP scope
        debug: Whether to enable debug output

    Returns:
        List of folders and projects
    """
    client = asset_v1.AssetServiceClient()
    folders = []
    projects = []

    # Fetch folders
    response = client.search_all_resources(
        scope=scope,
        asset_types=["cloudresourcemanager.googleapis.com/Folder"],
        page_size=500
    )

    for i, folder in enumerate(response):
        if debug and i == 0:
            print(json.dumps(MessageToDict(folder._pb), indent=2))
            return []  # Exit after printing first resource in debug mode

        folder_dict = MessageToDict(folder._pb)
        folders.append(folder_dict)

    # Fetch projects
    response = client.search_all_resources(
        scope=scope,
        asset_types=["cloudresourcemanager.googleapis.com/Project"],
        page_size=500
    )

    for i, project in enumerate(response):
        if debug and i == 0:
            print(json.dumps(MessageToDict(project._pb), indent=2))
            return []  # Exit after printing first resource in debug mode

        project_dict = MessageToDict(project._pb)
        projects.append(project_dict)

    return folders + projects

def load_asset_type_mapping():
    """
    Returns the embedded asset type mapping.

    Returns:
        Dictionary of asset type aliases
    """
    return dict(sorted(ASSET_TYPE_MAPPING.items()))

def build_folder_tree(assets, queried_parent_type, queried_parent_id):
    """
    Builds a hierarchical tree of folders and projects from the given assets.

    Args:
        assets: List of asset dictionaries
        queried_parent_type: Type of the parent asset (e.g., organizations, folders)
        queried_parent_id: ID of the parent asset

    Returns:
        Dictionary representing the hierarchical tree
    """
    folders = []
    root_level_projects = []
    projects = []

    for a in assets:
        asset_type = a.get('asset_type', '')
        name_parts = a.get('name', '').split('/')
        bare_name = name_parts[-1] if name_parts and name_parts[-1] else ''
        display_name = a.get('display_name', '')
        id_part = bare_name

        parent_full_resource_name = a.get('parent', '')
        parent_id_type, parent_id_value = '', ''
        if parent_full_resource_name:
            standardized_parent_str = parent_full_resource_name.replace("//cloudresourcemanager.googleapis.com/", "")
            if '/' in standardized_parent_str:
                parent_id_type, parent_id_value = standardized_parent_str.split('/', 1)

        entry = {
            'id': id_part,
            'name': a.get('name',''),
            'display_name': display_name,
            'parent_id_type': parent_id_type,
            'parent_id_value': parent_id_value,
            'asset_type': asset_type
        }

        if asset_type.endswith('/Folder'):
            folders.append(entry)
        elif asset_type.endswith('/Project'):
            projects.append(entry)
            if parent_id_type == queried_parent_type and parent_id_value == queried_parent_id:
                root_level_projects.append(entry)

    folder_tree = {}
    # Start with folders directly under the queried parent
    for folder in folders:
        if folder['parent_id_type'] == queried_parent_type and folder['parent_id_value'] == queried_parent_id:
            folder_id = folder['id']
            folder_tree[folder_id] = {
                'folder': folder,
                'projects': [],
                'subfolders': {}
            }

    # Function to recursively add subfolders
    def add_subfolders(folder_id, current_level):
        for folder in folders:
            if folder['parent_id_type'] == 'folders' and folder['parent_id_value'] == folder_id:
                subfolder_id = folder['id']
                current_level['subfolders'][subfolder_id] = {
                    'folder': folder,
                    'projects': [],
                    'subfolders': {}
                }
                add_subfolders(subfolder_id, current_level['subfolders'][subfolder_id])

    # Build the tree recursively starting from root folders
    for folder_id, folder_data in folder_tree.items():
        add_subfolders(folder_id, folder_data)

    # Assign projects to folders
    for project in projects:
        if project['parent_id_type'] == 'folders':
            folder_id = project['parent_id_value']
            # Find the folder in the tree
            def find_folder(tree, target_id):
                for folder_id, folder_data in tree.items():
                    if folder_id == target_id:
                        return folder_data
                    found = find_folder(folder_data['subfolders'], target_id)
                    if found:
                        return found
                return None

            folder_node = find_folder(folder_tree, folder_id)
            if folder_node:
                folder_node['projects'].append(project)

    return {
        'root_projects': root_level_projects,
        'folder_tree': folder_tree
    }

def generate_tree_output(hierarchy_data):
    """
    Generates a string representation of the hierarchical tree.

    Args:
        hierarchy_data: Dictionary representing the hierarchical tree

    Returns:
        String representation of the tree
    """
    output_lines = []

    # Root level projects
    for project in sorted(hierarchy_data['root_projects'], key=lambda p: p['display_name']):
        output_lines.append(f"- {project['display_name']} ({project['id']})")

    # Recursive function for folders
    def print_folder(folder_data, level=0):
        indent = '  ' * level
        folder = folder_data['folder']
        output_lines.append(f"{indent}[{folder['display_name']}] ({folder['id']})")

        # Projects in this folder
        for project in sorted(folder_data['projects'], key=lambda p: p['display_name']):
            output_lines.append(f"{indent}  - {project['display_name']} ({project['id']})")

        # Subfolders
        for subfolder_id, subfolder_data in sorted(folder_data['subfolders'].items(), key=lambda x: x[1]['folder']['display_name']):
            print_folder(subfolder_data, level+1)

    # Root level folders
    for folder_id, folder_data in sorted(hierarchy_data['folder_tree'].items(), key=lambda x: x[1]['folder']['display_name']):
        print_folder(folder_data)

    return "\n".join(output_lines)

def generate_json_output(hierarchy_data):
    """
    Generates a JSON representation of the hierarchical tree.

    Args:
        hierarchy_data: Dictionary representing the hierarchical tree

    Returns:
        JSON string representation of the tree
    """
    # Convert hierarchy to JSON-serializable format
    def folder_to_dict(folder_data):
        return {
            'folder': folder_data['folder'],
            'projects': folder_data['projects'],
            'subfolders': {fid: folder_to_dict(fd) for fid, fd in folder_data['subfolders'].items()}
        }

    return json.dumps({
        'organization_projects': hierarchy_data['root_projects'],
        'folders': {fid: folder_to_dict(fd) for fid, fd in hierarchy_data['folder_tree'].items()}
    }, indent=2)

def generate_tabular_output(hierarchy_data):
    """
    Generates a tabular representation of the hierarchical tree.

    Args:
        hierarchy_data: Dictionary representing the hierarchical tree

    Returns:
        List of rows for the table
    """
    rows = []

    # Root level projects
    for project in hierarchy_data['root_projects']:
        rows.append([
            project['id'],
            project['display_name'],
            'Project',
            ''  # No parent
        ])

    # Recursive function for folders and their projects
    def process_folder(folder_data, parent_display_name):
        folder = folder_data['folder']
        # Add the folder itself
        rows.append([
            folder['id'],
            folder['display_name'],
            'Folder',
            parent_display_name
        ])

        # Projects in this folder
        for project in folder_data['projects']:
            rows.append([
                project['id'],
                project['display_name'],
                'Project',
                folder['display_name']
            ])

        # Subfolders
        for subfolder_data in folder_data['subfolders'].values():
            process_folder(subfolder_data, folder['display_name'])

    # Root level folders
    for folder_data in hierarchy_data['folder_tree'].values():
        process_folder(folder_data, '')

    return rows

def print_resource_table(resources, scope):
    """
    Prints a table of resources.

    Args:
        resources: List of resource dictionaries
        scope: The scope of the resources
    """
    if not resources:
        print("No resources found.")
        return

    # Sort resources by project and then by name
    sorted_resources = sorted(resources, key=lambda r: (r.get('project', ''), r['name']))

    # Print scope header
    print(f"Scope: {scope}")

    headers = ["Name", "Project ID", "Location"]
    rows = []

    for resource in sorted_resources:
        name_parts = resource['name'].split('/')
        short_name = name_parts[-1] if name_parts else resource['name']

        # Extract project ID from parentFullResourceName
        project_id = ""
        if 'parent_full_resource_name' in resource:
            parent_full = resource.get('parent_full_resource_name', '')
            if parent_full.startswith("//cloudresourcemanager.googleapis.com/projects/"):
                project_id = parent_full.split("/")[-1]

        location = resource.get('location', '')

        # Escape double quotes and handle commas
        short_name = short_name.replace('"', '""')
        project_id = project_id.replace('"', '""')
        location = location.replace('"', '""')

        row_data = [
            short_name,
            project_id,
            location
        ]
        rows.append(row_data)

    # Calculate max widths for each column
    max_widths = [max(len(str(row[i])) for row in rows + [headers]) for i in range(len(headers))]

    # Print table
    header_line = "  ".join(headers[i].ljust(max_widths[i]) for i in range(len(headers)))
    print(header_line)
    print("-" * len(header_line))
    for row in sorted(rows, key=lambda x: (x[1], x[0])):
        print("  ".join(str(row[i]).ljust(max_widths[i]) for i in range(len(row))))

def print_tree_output(hierarchy_data):
    """
    Prints the hierarchical tree.

    Args:
        hierarchy_data: Dictionary representing the hierarchical tree
    """
    print(generate_tree_output(hierarchy_data))

def print_json_output(hierarchy_data):
    """
    Prints the JSON representation of the hierarchical tree.

    Args:
        hierarchy_data: Dictionary representing the hierarchical tree
    """
    print(generate_json_output(hierarchy_data))

def print_tabular_output(hierarchy_data):
    """
    Prints the tabular representation of the hierarchical tree.

    Args:
        hierarchy_data: Dictionary representing the hierarchical tree
    """
    tabular_rows = generate_tabular_output(hierarchy_data)
    # Define column widths for fixed-length feel
    col_widths = [30, 40, 10, 30] # Adjust as needed: ID, DisplayName, Type, ParentID
    header_format_string = "{:<%d} {:<%d} {:<%d} {:<%d}" % tuple(col_widths)
    row_format_string = "{:<%d} {:<%d} {:<%d} {:<%d}" % tuple(col_widths)

    headers = ["ID", "Display_Name", "Type", "Parent_ID"]
    print(header_format_string.format(*headers))
    print("-" * (sum(col_widths) + len(col_widths) * 2))

    if tabular_rows:
        for row_data in sorted(tabular_rows, key=lambda x: (x[0], x[1])):
            # Ensure all row elements are strings for formatting
            formatted_row = [str(field) for field in row_data]
            print(row_format_string.format(*formatted_row))
    else:
        print("No data to display in tabular format.")

def generate_pretty_tree_output(folder_data, prefix='', is_last=False):
    """
    Generates a pretty string representation of the hierarchical tree.

    Args:
        folder_data: Dictionary representing a folder in the tree
        prefix: Prefix for indentation
        is_last: If True, this is the last child

    Returns:
        List of lines for the pretty tree
    """
    output = []

    # Print projects in this folder
    projects = folder_data.get('projects', [])
    # Sort projects by display name
    projects = sorted(projects, key=lambda x: x['display_name'].lower())

    for i, project in enumerate(projects):
        is_last_project = i == len(projects) - 1 and not folder_data.get('subfolders')
        connector = '└── ' if is_last_project else '├── '
        output.append(f"{prefix}{connector}📄 {project['display_name']}")

    # Print subfolders
    if 'subfolders' in folder_data:
        folders = folder_data['subfolders']
        # Sort folders by display name
        folder_ids = sorted(folders.keys(), key=lambda k: folders[k]['folder']['display_name'].lower())

        for i, folder_id in enumerate(folder_ids):
            is_last_folder = i == len(folder_ids) - 1
            connector = '└── ' if is_last_folder else '├── '
            output.append(f"{prefix}{connector}📁 {folders[folder_id]['folder']['display_name']}")

            # Create new prefix for children
            child_prefix = prefix + ("    " if is_last_folder else "│   ")

            # Recursively generate output for subfolder
            sub_output = generate_pretty_tree_output(
                folders[folder_id],
                child_prefix,
                is_last_folder
            )
            output.extend(sub_output)

    return output

def print_pretty_tree_output(hierarchy_data, scope):
    """
    Prints the pretty string representation of the hierarchical tree.

    Args:
        hierarchy_data: Dictionary representing the hierarchical tree
        scope: The scope of the tree
    """
    output = [f"Scope: {scope}"]

    # Print root projects
    projects = hierarchy_data.get('root_projects', [])
    # Sort root projects by display name
    projects = sorted(projects, key=lambda x: x['display_name'].lower())

    for i, project in enumerate(projects):
        is_last_project = i == len(projects) - 1 and not hierarchy_data.get('folder_tree')
        connector = '└── ' if is_last_project else '├── '
        output.append(f"{connector}📄 {project['display_name']}")

    # Print folder tree
    folder_tree = hierarchy_data.get('folder_tree', {})
    # Sort top-level folders by display name
    folder_ids = sorted(folder_tree.keys(), key=lambda k: folder_tree[k]['folder']['display_name'].lower())

    for i, folder_id in enumerate(folder_ids):
        folder_data = folder_tree[folder_id]
        is_last_folder = i == len(folder_ids) - 1
        connector = '└── ' if is_last_folder else '├── '
        output.append(f"{connector}📁 {folder_data['folder']['display_name']}")

        # Create prefix for children
        child_prefix = "    " if is_last_folder else "│   "

        # Generate output for folder
        folder_output = generate_pretty_tree_output(folder_data, child_prefix, is_last_folder)
        output.extend(folder_output)

    for line in output:
        print(line)

def print_csv_output(resources, scope):
    """
    Prints resources in CSV format.

    Args:
        resources: List of resource dictionaries
        scope: The scope of the resources
    """
    if not resources:
        print("No resources found.")
        return

    # Print header
    print("Name,Project ID,Location,Scope")

    # Print each resource
    for resource in resources:
        name_parts = resource['name'].split('/')
        short_name = name_parts[-1] if name_parts else resource['name']
        project_id = resource['project']
        location = resource.get('location', '')

        # Escape double quotes and handle commas
        short_name = short_name.replace('"', '""')
        project_id = project_id.replace('"', '""')
        location = location.replace('"', '""')
        scope_str = scope.replace('"', '""')

        print(f'"{short_name}","{project_id}","{location}","{scope_str}"')

def main():
    parser = argparse.ArgumentParser(description="GCP Asset Lister CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    hierarchy_parser = subparsers.add_parser("hierarchy", help="Display asset hierarchy (folders, projects).")
    hierarchy_parser.add_argument("--scope", required=True, help="GCP organization scope (e.g. organizations/123456789)")
    hierarchy_parser.add_argument("--format", choices=["tree", "json", "tabular", "pretty"], default="tree", help="Output format")

    list_parser = subparsers.add_parser("list-resources", help="List resources of a specific type.")
    list_parser.add_argument("--scope", required=True, help="GCP organization scope (e.g. organizations/123456789)")
    list_parser.add_argument("--type", required=True, help="Resource type to list (e.g., compute.googleapis.com/Instance)")
    list_parser.add_argument("--format", choices=["json", "tabular", "csv"], default="tabular", help="Output format")
    list_parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()
    scope = args.scope

    if args.command == "hierarchy":
        # Validate scope
        try:
            parent_type, parent_id = scope.split('/', 1)
            if parent_type not in ["organizations", "folders"] or not parent_id.strip():
                raise ValueError("Scope must be 'organizations/<id>' or 'folders/<id>'. Received: '{scope}'. Details: {e}")
            parent_id = parent_id.strip()
        except ValueError as e:
            print(f"Error: Invalid --scope format. Must be 'organizations/<id>' or 'folders/<id>'. Received: '{scope}'. Details: {e}")
            return

        try:
            assets = fetch_assets(scope)
        except Exception as e:
            print(f"Error fetching assets from GCP: {e}")
            return

        if not assets:
            print("No assets found under the specified parent or an error occurred during fetching.")
            return

        hierarchy_data = build_folder_tree(assets, parent_type, parent_id)

        if args.format == "tree":
            print_tree_output(hierarchy_data)
        elif args.format == "json":
            print_json_output(hierarchy_data)
        elif args.format == "tabular":
            print_tabular_output(hierarchy_data)
        elif args.format == "pretty":
            print_pretty_tree_output(hierarchy_data, scope)

    elif args.command == "list-resources":
        # Load resource type mapping
        asset_type_mapping = load_asset_type_mapping()
        asset_type = asset_type_mapping.get(args.type, args.type)

        if not args.debug:
            spinner = Spinner(f"Fetching {args.type} resources... ")
            spinner.start()

        try:
            resources = fetch_flat_resources(scope, asset_type, args.debug)
        finally:
            if not args.debug:
                spinner.stop()

        if not resources and not args.debug:
            print("No resources found.")
            return

        if args.debug:
            # In debug mode, output already printed in fetch_flat_resources
            pass
        elif args.format == "json":
            # Add scope to each resource
            for r in resources:
                r['scope'] = scope
            print(json.dumps(resources, indent=2))
        elif args.format == "csv":
            print_csv_output(resources, scope)
        else:  # tabular
            print_resource_table(resources, scope)

if __name__ == "__main__":
    main()
