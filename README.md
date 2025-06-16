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
gcpassets-cli.py hierarchy -s SCOPE [-f FORMAT]
```

**Options:**
- `-s, --scope`: GCP organization scope (e.g. `organizations/123456789`)
- `-f, --format`: Output format (`tree`, `json`, `tabular`, `pretty`)

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
gcpassets-cli.py hierarchy -s organizations/1234567890 -f tree
```

### 2. `list-resources` - List Specific Resources

Lists GCP resources within a scope with simplified output.

**Syntax:**
```bash
gcpassets-cli.py list-resources -s SCOPE -t RESOURCE_TYPE [-f FORMAT] [-d]
```

**Options:**
- `-s, --scope`: GCP organization scope
- `-t, --type`: Resource type (vm, storagebucket, etc.)
- `-f, --format`: Output format (`tabular`, `json`, `csv`)
- `-d, --debug`: Enable debug output

**Resource Types:**
`accessapprovalsettings`, `accesslevel`, `accesspolicy`, `activedirectory`, `address`, `addressgroup`, `agent`, `aiplatformdataset`, `aiplatformendpoint`, `aiplatformmodel`, `alertpolicy`, `alloydbbackup`, `alloydbcluster`, `alloydbinstance`, `api`, `apiconfig`, `apigatewaygateway`, `apigeeinstance`, `apigeeorganization`, `apihubinstance`, `apikeyskey`, `appconnection`, `appconnector`, `appengineapplication`, `appengineservice`, `appgateway`, `apphubapplication`, `apphubservice`, `apphubworkload`, `appprofile`, `artifactregistryrepository`, `aspecttype`, `assuredworkloadsworkload`, `attachedcluster`, `attestor`, `authconfig`, `authorizationpolicy`, `authorizedorgsdesc`, `autokeyconfig`, `automation`, `automationrun`, `autonomousdatabase`, `autoscaler`, `autoscalingpolicy`, `awscluster`, `awsnodepool`, `azureclient`, `azurecluster`, `azurenodepool`, `backendbucket`, `backendservice`, `backtestresult`, `backupdrbackup`, `backupdrbackupplan`, `backupdrbackupvault`, `backupplanassociation`, `backuppolicy`, `backuprun`, `baremetaladmincluster`, `baremetalcluster`, `baremetalnodepool`, `batch`, `batchjob`, `batchpredictionjob`, `bigquerydataset`, `bigqueryexport`, `bigquerymodel`, `bigquerytable`, `bigtableadminbackup`, `bigtableadmincluster`, `bigtableadmininstance`, `bigtableadmintable`, `billingaccount`, `binaryauthorizationpolicy`, `bitbucketserverconfig`, `blockchainnode`, `bucket`, `build`, `buildtrigger`, `capool`, `catalog`, `cdnkey`, `certificateauthority`, `certificateissuanceconfig`, `certificatemanagercertificate`, `certificatemap`, `certificatemapentry`, `certificaterevocationlist`, `certificatetemplate`, `channelconnection`, `cienttlspolicy`, `clientconnectorservice`, `clientgateway`, `clonejob`, `cloudbuildconnection`, `cloudbuildrepository`, `cloudcontrolspartnerworkload`, `clouddeployrelease`, `cloudexadatainfrastructure`, `cloudfunction`, `cloudresourcemanagerorganization`, `cloudresourcemanagerproject`, `cloudvmcluster`, `coderepositoryindex`, `collection`, `commitment`, `compilationresult`, `composerenvironment`, `computefirewallpolicy`, `computeimage`, `computeinstance`, `computeproject`, `computesnapshot`, `computestoragepool`, `configdeployment`, `connectclusters`, `connectedcluster`, `connectivitytest`, `connector`, `connectorsconnection`, `connectorsmanagedzone`, `consentstore`, `contact`, `containercluster`, `containerregistryimage`, `containerthreatdetectionsettings`, `conversationprofile`, `conversionworkspace`, `cryptokey`, `cryptokeyversion`, `customclass`, `customconstraint`, `customer`, `customjob`, `customtargettype`, `cutoverjob`, `dashboard`, `datacenterconnector`, `dataflowjob`, `dataformrepository`, `datafusioninstance`, `datalabelingjob`, `datamigrationconnectionprofile`, `datamigrationprivateconnection`, `dataplexasset`, `dataplexenvironment`, `dataproccluster`, `dataprocjob`, `datascan`, `datasource`, `datastore`, `datastreamconnectionprofile`, `datastreamprivateconnection`, `defaultsupportedidpconfig`, `deidentifytemplate`, `deliverypipeline`, `deploypolicy`, `developerconnectconnection`, `dicomstore`, `discoveryconfig`, `disk`, `dlpjob`, `dnsauthorization`, `dnsmanagedzone`, `dnspeering`, `dnspolicy`, `dockerimage`, `domain`, `domainmapping`, `edgecachekeyset`, `edgecacheorigin`, `edgecacheservice`, `ekmconfig`, `ekmconnection`, `encryptionconfigs`, `endpointattachment`, `endpointpolicy`, `engine`, `engineconfig`, `enrollment`, `entrygroup`, `entrytype`, `eventarcchannel`, `eventsubscription`, `eventthreatdetectioncustommodule`, `eventthreatdetectionsettings`, `externalaccessrule`, `externaladdress`, `externalvpngateway`, `feature`, `featuregroup`, `featureonlinestore`, `featurestore`, `federation`, `feed`, `fhirstore`, `filebackup`, `fileinstance`, `filesnapshot`, `financialservicesdataset`, `financialservicesinstance`, `financialservicesmodel`, `firebaseappinfo`, `firebaseproject`, `firebaserulesrelease`, `firestorebackup`, `firestoredatabase`, `firewall`, `firewallendpoint`, `firewallendpointassociation`, `fleet`, `folder`, `forwardingrule`, `function`, `gatewaysecuritypolicy`, `gatewaysecuritypolicyrule`, `githubenterpriseconfig`, `gitrepositorylink`, `gkebackupbackup`, `gkebackupbackupplan`, `gkehubnamespace`, `globaladdress`, `globalforwardingrule`, `globaltriggersettings`, `glossary`, `googleapisource`, `googlechannelconfig`, `grant`, `group`, `grpcroute`, `healthcaredataset`, `healthcheck`, `hl7v2store`, `httphealthcheck`, `httproute`, `httpshealthcheck`, `hub`, `hubroute`, `humanreviewconfig`, `hyperparametertuningjob`, `iamrole`, `iamserviceaccount`, `identitytoolkitconfig`, `idsendpoint`, `imageimport`, `importjob`, `inboundsamlconfig`, `index`, `indexendpoint`, `input`, `inspecttemplate`, `instanceconfig`, `instancegroup`, `instancegroupmanager`, `instancesettings`, `instancetemplate`, `instantsnapshot`, `integration`, `integrationscertificate`, `integrationsexecution`, `integrationversion`, `interconnect`, `interconnectattachment`, `issuemodel`, `jobrun`, `jobtemplate`, `jobtrigger`, `keyhandle`, `keyring`, `kmsconfig`, `knowledgebase`, `krmapihost`, `labelerpool`, `lake`, `lbrouteextension`, `lbtrafficextension`, `license`, `lie`, `link`, `liveconfig`, `livestreamasset`, `livestreamchannel`, `locationsettings`, `logbucket`, `loggingsettings`, `logmetric`, `logsink`, `logview`, `lookerinstance`, `machineimage`, `managedkafkacluster`, `managedservice`, `managementserver`, `mavenartifact`, `membership`, `membershipbinding`, `membershipfeature`, `memcacheinstance`, `mesh`, `messagebus`, `metadataimport`, `metadatajob`, `metadatastore`, `metastorebackup`, `metastoreservice`, `migratingvm`, `migrationjob`, `migrationworkflow`, `modeldeploymentmonitoringjob`, `muteconfig`, `nasjob`, `netappbackup`, `netappbackupvault`, `netappsnapshot`, `netappstoragepool`, `network`, `networkattachment`, `networkedgesecurityservice`, `networkendpointgroup`, `networkpeering`, `networksecuritytlsinspectionpolicy`, `networkservicesgateway`, `nodegroup`, `nodepool`, `nodetemplate`, `notebook`, `notebookexecutionjob`, `notebookruntime`, `notebookruntimetemplate`, `notebooksinstance`, `notificationchannel`, `notificationconfig`, `npmpackage`, `oauthidpconfig`, `orgpolicypolicy`, `ospolicyassignment`, `ospolicyassignmentreport`, `packetmirroring`, `partner`, `patchdeployment`, `phrase`, `phrasematcher`, `phraseset`, `pipeline`, `pipelinejob`, `platformpolicy`, `policybasedroute`, `policyv2`, `pool`, `posture`, `posturedeployment`, `predictionresult`, `preview`, `privatecacertificate`, `privatecloud`, `process`, `processor`, `processorversion`, `projectbillinginfo`, `publicdelegatedprefix`, `pubsubsnapshot`, `pythonpackage`, `queue`, `quotapreference`, `rbacrolebinding`, `recaptchaenterprisefirewallpolicy`, `recaptchaenterprisekey`, `recentquery`, `recognizer`, `rediscluster`, `redisinstance`, `regionbackendservice`, `regiondisk`, `registration`, `releaseconfig`, `replication`, `reportconfig`, `reportdetail`, `repositorygroup`, `reservation`, `resourcepolicy`, `resourcerecordset`, `resourcevalueconfig`, `responsepolicy`, `responsepolicyrule`, `restore`, `restoreplan`, `revision`, `rollout`, `route`, `router`, `routetable`, `rule`, `ruleset`, `runexecution`, `runjob`, `runservice`, `savedquery`, `scanconfig`, `schema`, `scope`, `secretmanagersecret`, `secretversion`, `securesourcemanagerinstance`, `securitycenterservice`, `securityhealthanalyticscustommodule`, `securityhealthanalyticssettings`, `securitypolicy`, `securityprofile`, `securityprofilegroup`, `servertlspolicy`, `serviceaccountkey`, `serviceattachment`, `servicebinding`, `servicedirectoryendpoint`, `servicedirectorynamespace`, `servicedirectoryservice`, `servicelbpolicy`, `servicenetworkingconnection`, `serviceperimeter`, `serviceprojectattachment`, `serviceusageservice`, `session`, `sfdcchannel`, `sfdcinstance`, `slate`, `snooze`, `source`, `spannerbackup`, `spannerdatabase`, `spannerinstance`, `speaker`, `speakeridsettings`, `specialistpool`, `speechconfig`, `spoke`, `sqladminbackup`, `sqladmininstance`, `sslcertificate`, `sslpolicy`, `storedinfotype`, `stream`, `subnetwork`, `subscription`, `suspension`, `tagbinding`, `tagkey`, `tagvalue`, `target`, `targetgrpcproxy`, `targethttpproxy`, `targethttpsproxy`, `targetinstance`, `targetpool`, `targetproject`, `targetsslproxy`, `targettcpproxy`, `targetvpngateway`, `task`, `tcproute`, `tenant`, `tensorboard`, `tlsroute`, `topic`, `tpunode`, `trainingpipeline`, `transcoderjob`, `transferconfig`, `transferjob`, `trigger`, `trustconfig`, `tuningjob`, `tunneldestgroup`, `uptimecheckconfig`, `urllist`, `urlmap`, `utilizationreport`, `version`, `view`, `virtualmachinethreatdetectionsettings`, `vmwareadmincluster`, `vmwarecluster`, `vmwareenginecluster`, `vmwareenginenetwork`, `vmwareenginenetworkpolicy`, `vmwareengineprivateconnection`, `vmwarenodepool`, `vodconfig`, `volume`, `volumebackup`, `volumerestore`, `vpngateway`, `vpntunnel`, `vulnerabilityreport`, `wasmplugin`, `wasmpluginversion`, `websecurityscannersettings`, `workerpool`, `workflow`, `workflowconfig`, `workflowinvocation`, `workflowtemplate`, `workspace`, `workstation`, `workstationcluster`, `workstationconfig`, `zone`

**Output Fields:**
- `name`: Resource name
- `asset_type`: Full resource type
- `project`: Project ID
- `display_name`: Human-readable name (if available)
- `location`: Resource location
- `parent_full_resource_name`: Parent resource reference
- `additional_attributes`: Extended metadata (varies by resource type)

**Common Additional Attributes:**
- Compute Instances: `machineType`, `internalIPs`, `networkInterfaces`
- Disks: `sizeGb`, `type`, `users`
- Networks: `id`, `routingMode`
- GKE Clusters: `currentMasterVersion`, `nodePools`

**Output:**
Simplified fixed-width table with columns: `Project_ID` and `Resource_Name`

**Examples:**
```bash
# Tabular output (default)
gcpassets-cli.py list-resources -s folders/987013313595 -t computeinstance

# JSON output
gcpassets-cli.py list-resources -s folders/987013313595 -t computeinstance -f json

# CSV output
gcpassets-cli.py list-resources -s folders/987013313595 -t computeinstance -f csv
```

**Note:** Additional attributes availability varies by resource type. Some types may return an empty object `{}`.

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
