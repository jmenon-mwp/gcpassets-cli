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
'accessapprovalsettings'               : 'accessapproval.googleapis.com/AccessApprovalSettings',
'authorizedorgsdesc'                   : 'accesscontextmanager.googleapis.com/AuthorizedOrgsDesc',
'batchpredictionjob'                   : 'aiplatform.googleapis.com/BatchPredictionJob',
'customjob'                            : 'aiplatform.googleapis.com/CustomJob',
'datalabelingjob'                      : 'aiplatform.googleapis.com/DataLabelingJob',
'aiplatformdataset'                    : 'aiplatform.googleapis.com/Dataset',
'aiplatformendpoint'                   : 'aiplatform.googleapis.com/Endpoint',
'featuregroup'                         : 'aiplatform.googleapis.com/FeatureGroup',
'featureonlinestore'                   : 'aiplatform.googleapis.com/FeatureOnlineStore',
'featurestore'                         : 'aiplatform.googleapis.com/Featurestore',
'hyperparametertuningjob'              : 'aiplatform.googleapis.com/HyperparameterTuningJob',
'index'                                : 'aiplatform.googleapis.com/Index',
'indexendpoint'                        : 'aiplatform.googleapis.com/IndexEndpoint',
'metadatastore'                        : 'aiplatform.googleapis.com/MetadataStore',
'aiplatformmodel'                      : 'aiplatform.googleapis.com/Model',
'modeldeploymentmonitoringjob'         : 'aiplatform.googleapis.com/ModelDeploymentMonitoringJob',
'nasjob'                               : 'aiplatform.googleapis.com/NasJob',
'notebookexecutionjob'                 : 'aiplatform.googleapis.com/NotebookExecutionJob',
'notebookruntime'                      : 'aiplatform.googleapis.com/NotebookRuntime',
'notebookruntimetemplate'              : 'aiplatform.googleapis.com/NotebookRuntimeTemplate',
'pipelinejob'                          : 'aiplatform.googleapis.com/PipelineJob',
'specialistpool'                       : 'aiplatform.googleapis.com/SpecialistPool',
'tensorboard'                          : 'aiplatform.googleapis.com/Tensorboard',
'trainingpipeline'                     : 'aiplatform.googleapis.com/TrainingPipeline',
'tuningjob'                            : 'aiplatform.googleapis.com/TuningJob',
'alloydbbackup'                        : 'alloydb.googleapis.com/Backup',
'alloydbcluster'                       : 'alloydb.googleapis.com/Cluster',
'alloydbinstance'                      : 'alloydb.googleapis.com/Instance',
'connectedcluster'                     : 'anthos.googleapis.com/ConnectedCluster',
'api'                                  : 'apigateway.googleapis.com/Api',
'apiconfig'                            : 'apigateway.googleapis.com/ApiConfig',
'apigatewaygateway'                    : 'apigateway.googleapis.com/Gateway',
'apigeeinstance'                       : 'apigee.googleapis.com/Instance',
'apigeeorganization'                   : 'apigee.googleapis.com/Organization',
'apihubinstance'                       : 'apihub.googleapis.com/ApiHubInstance',
'apikeyskey'                           : 'apikeys.googleapis.com/Key',
'appengineapplication'                 : 'appengine.googleapis.com/Application',
'appengineservice'                     : 'appengine.googleapis.com/Service',
'version'                              : 'appengine.googleapis.com/Version',
'apphubapplication'                    : 'apphub.googleapis.com/Application',
'apphubservice'                        : 'apphub.googleapis.com/Service',
'serviceprojectattachment'             : 'apphub.googleapis.com/ServiceProjectAttachment',
'apphubworkload'                       : 'apphub.googleapis.com/Workload',
'dockerimage'                          : 'artifactregistry.googleapis.com/DockerImage',
'mavenartifact'                        : 'artifactregistry.googleapis.com/MavenArtifact',
'npmpackage'                           : 'artifactregistry.googleapis.com/NpmPackage',
'pythonpackage'                        : 'artifactregistry.googleapis.com/PythonPackage',
'artifactregistryrepository'           : 'artifactregistry.googleapis.com/Repository',
'rule'                                 : 'artifactregistry.googleapis.com/Rule',
'assuredworkloadsworkload'             : 'assuredworkloads.googleapis.com/Workload',
'backupdrbackup'                       : 'backupdr.googleapis.com/Backup',
'backupdrbackupplan'                   : 'backupdr.googleapis.com/BackupPlan',
'backupplanassociation'                : 'backupdr.googleapis.com/BackupPlanAssociation',
'backupdrbackupvault'                  : 'backupdr.googleapis.com/BackupVault',
'datasource'                           : 'backupdr.googleapis.com/DataSource',
'managementserver'                     : 'backupdr.googleapis.com/ManagementServer',
'batchjob'                             : 'batch.googleapis.com/Job',
'appconnection'                        : 'beyondcorp.googleapis.com/AppConnection',
'appconnector'                         : 'beyondcorp.googleapis.com/AppConnector',
'appgateway'                           : 'beyondcorp.googleapis.com/AppGateway',
'clientconnectorservice'               : 'beyondcorp.googleapis.com/ClientConnectorService',
'clientgateway'                        : 'beyondcorp.googleapis.com/ClientGateway',
'transferconfig'                       : 'bigquerydatatransfer.googleapis.com/TransferConfig',
'bigquerydataset'                      : 'bigquery.googleapis.com/Dataset',
'bigquerymodel'                        : 'bigquery.googleapis.com/Model',
'bigquerytable'                        : 'bigquery.googleapis.com/Table',
'migrationworkflow'                    : 'bigquerymigration.googleapis.com/MigrationWorkflow',
'appprofile'                           : 'bigtableadmin.googleapis.com/AppProfile',
'bigtableadminbackup'                  : 'bigtableadmin.googleapis.com/Backup',
'bigtableadmincluster'                 : 'bigtableadmin.googleapis.com/Cluster',
'bigtableadmininstance'                : 'bigtableadmin.googleapis.com/Instance',
'bigtableadmintable'                   : 'bigtableadmin.googleapis.com/Table',
'attestor'                             : 'binaryauthorization.googleapis.com/Attestor',
'platformpolicy'                       : 'binaryauthorization.googleapis.com/PlatformPolicy',
'binaryauthorizationpolicy'            : 'binaryauthorization.googleapis.com/Policy',
'blockchainnode'                       : 'blockchainnodeengine.googleapis.com/BlockchainNode',
'certificatemanagercertificate'        : 'certificatemanager.googleapis.com/Certificate',
'certificateissuanceconfig'            : 'certificatemanager.googleapis.com/CertificateIssuanceConfig',
'certificatemap'                       : 'certificatemanager.googleapis.com/CertificateMap',
'certificatemapentry'                  : 'certificatemanager.googleapis.com/CertificateMapEntry',
'dnsauthorization'                     : 'certificatemanager.googleapis.com/DnsAuthorization',
'trustconfig'                          : 'certificatemanager.googleapis.com/TrustConfig',
'coderepositoryindex'                  : 'cloudaicompanion.googleapis.com/CodeRepositoryIndex',
'repositorygroup'                      : 'cloudaicompanion.googleapis.com/RepositoryGroup',
'feed'                                 : 'cloudasset.googleapis.com/Feed',
'billingaccount'                       : 'cloudbilling.googleapis.com/BillingAccount',
'projectbillinginfo'                   : 'cloudbilling.googleapis.com/ProjectBillingInfo',
'bitbucketserverconfig'                : 'cloudbuild.googleapis.com/BitbucketServerConfig',
'build'                                : 'cloudbuild.googleapis.com/Build',
'buildtrigger'                         : 'cloudbuild.googleapis.com/BuildTrigger',
'cloudbuildconnection'                 : 'cloudbuild.googleapis.com/Connection',
'githubenterpriseconfig'               : 'cloudbuild.googleapis.com/GithubEnterpriseConfig',
'globaltriggersettings'                : 'cloudbuild.googleapis.com/GlobalTriggerSettings',
'cloudbuildrepository'                 : 'cloudbuild.googleapis.com/Repository',
'workerpool'                           : 'cloudbuild.googleapis.com/WorkerPool',
'customer'                             : 'cloudcontrolspartner.googleapis.com/Customer',
'partner'                              : 'cloudcontrolspartner.googleapis.com/Partner',
'cloudcontrolspartnerworkload'         : 'cloudcontrolspartner.googleapis.com/Workload',
'automation'                           : 'clouddeploy.googleapis.com/Automation',
'automationrun'                        : 'clouddeploy.googleapis.com/AutomationRun',
'customtargettype'                     : 'clouddeploy.googleapis.com/CustomTargetType',
'deliverypipeline'                     : 'clouddeploy.googleapis.com/DeliveryPipeline',
'deploypolicy'                         : 'clouddeploy.googleapis.com/DeployPolicy',
'jobrun'                               : 'clouddeploy.googleapis.com/JobRun',
'clouddeployrelease'                   : 'clouddeploy.googleapis.com/Release',
'rollout'                              : 'clouddeploy.googleapis.com/Rollout',
'target'                               : 'clouddeploy.googleapis.com/Target',
'cloudfunction'                        : 'cloudfunctions.googleapis.com/CloudFunction',
'function'                             : 'cloudfunctions.googleapis.com/Function',
'autokeyconfig'                        : 'cloudkms.googleapis.com/AutokeyConfig',
'cryptokey'                            : 'cloudkms.googleapis.com/CryptoKey',
'cryptokeyversion'                     : 'cloudkms.googleapis.com/CryptoKeyVersion',
'ekmconfig'                            : 'cloudkms.googleapis.com/EkmConfig',
'ekmconnection'                        : 'cloudkms.googleapis.com/EkmConnection',
'importjob'                            : 'cloudkms.googleapis.com/ImportJob',
'keyhandle'                            : 'cloudkms.googleapis.com/KeyHandle',
'keyring'                              : 'cloudkms.googleapis.com/KeyRing',
'quotapreference'                      : 'cloudquotas.googleapis.com/QuotaPreference',
'folder'                               : 'cloudresourcemanager.googleapis.com/Folder',
'lien'                                 : 'cloudresourcemanager.googleapis.com/Lien',
'cloudresourcemanagerorganization'     : 'cloudresourcemanager.googleapis.com/Organization',
'cloudresourcemanagerproject'          : 'cloudresourcemanager.googleapis.com/Project',
'tagbinding'                           : 'cloudresourcemanager.googleapis.com/TagBinding',
'tagkey'                               : 'cloudresourcemanager.googleapis.com/TagKey',
'tagvalue'                             : 'cloudresourcemanager.googleapis.com/TagValue',
'queue'                                : 'cloudtasks.googleapis.com/Queue',
'composerenvironment'                  : 'composer.googleapis.com/Environment',
'address'                              : 'compute.googleapis.com/Address',
'autoscaler'                           : 'compute.googleapis.com/Autoscaler',
'backendbucket'                        : 'compute.googleapis.com/BackendBucket',
'backendservice'                       : 'compute.googleapis.com/BackendService',
'commitment'                           : 'compute.googleapis.com/Commitment',
'disk'                                 : 'compute.googleapis.com/Disk',
'externalvpngateway'                   : 'compute.googleapis.com/ExternalVpnGateway',
'firewall'                             : 'compute.googleapis.com/Firewall',
'computefirewallpolicy'                : 'compute.googleapis.com/FirewallPolicy',
'forwardingrule'                       : 'compute.googleapis.com/ForwardingRule',
'globaladdress'                        : 'compute.googleapis.com/GlobalAddress',
'globalforwardingrule'                 : 'compute.googleapis.com/GlobalForwardingRule',
'healthcheck'                          : 'compute.googleapis.com/HealthCheck',
'httphealthcheck'                      : 'compute.googleapis.com/HttpHealthCheck',
'httpshealthcheck'                     : 'compute.googleapis.com/HttpsHealthCheck',
'computeimage'                         : 'compute.googleapis.com/Image',
'computeinstance'                      : 'compute.googleapis.com/Instance',
'instancegroup'                        : 'compute.googleapis.com/InstanceGroup',
'instancegroupmanager'                 : 'compute.googleapis.com/InstanceGroupManager',
'instancesettings'                     : 'compute.googleapis.com/InstanceSettings',
'instancetemplate'                     : 'compute.googleapis.com/InstanceTemplate',
'instantsnapshot'                      : 'compute.googleapis.com/InstantSnapshot',
'interconnect'                         : 'compute.googleapis.com/Interconnect',
'interconnectattachment'               : 'compute.googleapis.com/InterconnectAttachment',
'license'                              : 'compute.googleapis.com/License',
'machineimage'                         : 'compute.googleapis.com/MachineImage',
'network'                              : 'compute.googleapis.com/Network',
'networkattachment'                    : 'compute.googleapis.com/NetworkAttachment',
'networkedgesecurityservice'           : 'compute.googleapis.com/NetworkEdgeSecurityService',
'networkendpointgroup'                 : 'compute.googleapis.com/NetworkEndpointGroup',
'nodegroup'                            : 'compute.googleapis.com/NodeGroup',
'nodetemplate'                         : 'compute.googleapis.com/NodeTemplate',
'packetmirroring'                      : 'compute.googleapis.com/PacketMirroring',
'computeproject'                       : 'compute.googleapis.com/Project',
'publicdelegatedprefix'                : 'compute.googleapis.com/PublicDelegatedPrefix',
'regionbackendservice'                 : 'compute.googleapis.com/RegionBackendService',
'regiondisk'                           : 'compute.googleapis.com/RegionDisk',
'reservation'                          : 'compute.googleapis.com/Reservation',
'resourcepolicy'                       : 'compute.googleapis.com/ResourcePolicy',
'route'                                : 'compute.googleapis.com/Route',
'router'                               : 'compute.googleapis.com/Router',
'securitypolicy'                       : 'compute.googleapis.com/SecurityPolicy',
'serviceattachment'                    : 'compute.googleapis.com/ServiceAttachment',
'computesnapshot'                      : 'compute.googleapis.com/Snapshot',
'sslcertificate'                       : 'compute.googleapis.com/SslCertificate',
'sslpolicy'                            : 'compute.googleapis.com/SslPolicy',
'computestoragepool'                   : 'compute.googleapis.com/StoragePool',
'subnetwork'                           : 'compute.googleapis.com/Subnetwork',
'targetgrpcproxy'                      : 'compute.googleapis.com/TargetGrpcProxy',
'targethttpproxy'                      : 'compute.googleapis.com/TargetHttpProxy',
'targethttpsproxy'                     : 'compute.googleapis.com/TargetHttpsProxy',
'targetinstance'                       : 'compute.googleapis.com/TargetInstance',
'targetpool'                           : 'compute.googleapis.com/TargetPool',
'targetsslproxy'                       : 'compute.googleapis.com/TargetSslProxy',
'targettcpproxy'                       : 'compute.googleapis.com/TargetTcpProxy',
'targetvpngateway'                     : 'compute.googleapis.com/TargetVpnGateway',
'urlmap'                               : 'compute.googleapis.com/UrlMap',
'vpngateway'                           : 'compute.googleapis.com/VpnGateway',
'vpntunnel'                            : 'compute.googleapis.com/VpnTunnel',
'configdeployment'                     : 'config.googleapis.com/Deployment',
'preview'                              : 'config.googleapis.com/Preview',
'connectorsconnection'                 : 'connectors.googleapis.com/Connection',
'endpointattachment'                   : 'connectors.googleapis.com/EndpointAttachment',
'eventsubscription'                    : 'connectors.googleapis.com/EventSubscription',
'connectorsmanagedzone'                : 'connectors.googleapis.com/ManagedZone',
'issuemodel'                           : 'contactcenterinsights.googleapis.com/IssueModel',
'phrasematcher'                        : 'contactcenterinsights.googleapis.com/PhraseMatcher',
'view'                                 : 'contactcenterinsights.googleapis.com/View',
'containercluster'                     : 'container.googleapis.com/Cluster',
'nodepool'                             : 'container.googleapis.com/NodePool',
'containerregistryimage'               : 'containerregistry.googleapis.com/Image',
'dataflowjob'                          : 'dataflow.googleapis.com/Job',
'compilationresult'                    : 'dataform.googleapis.com/CompilationResult',
'releaseconfig'                        : 'dataform.googleapis.com/ReleaseConfig',
'dataformrepository'                   : 'dataform.googleapis.com/Repository',
'workflowconfig'                       : 'dataform.googleapis.com/WorkflowConfig',
'workflowinvocation'                   : 'dataform.googleapis.com/WorkflowInvocation',
'workspace'                            : 'dataform.googleapis.com/Workspace',
'dnspeering'                           : 'datafusion.googleapis.com/DnsPeering',
'datafusioninstance'                   : 'datafusion.googleapis.com/Instance',
'process'                              : 'datalineage.googleapis.com/Process',
'datamigrationconnectionprofile'       : 'datamigration.googleapis.com/ConnectionProfile',
'conversionworkspace'                  : 'datamigration.googleapis.com/ConversionWorkspace',
'migrationjob'                         : 'datamigration.googleapis.com/MigrationJob',
'datamigrationprivateconnection'       : 'datamigration.googleapis.com/PrivateConnection',
'aspecttype'                           : 'dataplex.googleapis.com/AspectType',
'dataplexasset'                        : 'dataplex.googleapis.com/Asset',
'datascan'                             : 'dataplex.googleapis.com/DataScan',
'encryptionconfigs'                    : 'dataplex.googleapis.com/EncryptionConfigs',
'entrygroup'                           : 'dataplex.googleapis.com/EntryGroup',
'entrytype'                            : 'dataplex.googleapis.com/EntryType',
'dataplexenvironment'                  : 'dataplex.googleapis.com/Environment',
'glossary'                             : 'dataplex.googleapis.com/Glossary',
'lake'                                 : 'dataplex.googleapis.com/Lake',
'metadatajob'                          : 'dataplex.googleapis.com/MetadataJob',
'task'                                 : 'dataplex.googleapis.com/Task',
'zone'                                 : 'dataplex.googleapis.com/Zone',
'autoscalingpolicy'                    : 'dataproc.googleapis.com/AutoscalingPolicy',
'batch'                                : 'dataproc.googleapis.com/Batch',
'dataproccluster'                      : 'dataproc.googleapis.com/Cluster',
'dataprocjob'                          : 'dataproc.googleapis.com/Job',
'session'                              : 'dataproc.googleapis.com/Session',
'workflowtemplate'                     : 'dataproc.googleapis.com/WorkflowTemplate',
'datastreamconnectionprofile'          : 'datastream.googleapis.com/ConnectionProfile',
'datastreamprivateconnection'          : 'datastream.googleapis.com/PrivateConnection',
'stream'                               : 'datastream.googleapis.com/Stream',
'developerconnectconnection'           : 'developerconnect.googleapis.com/Connection',
'gitrepositorylink'                    : 'developerconnect.googleapis.com/GitRepositoryLink',
'agent'                                : 'dialogflow.googleapis.com/Agent',
'conversationprofile'                  : 'dialogflow.googleapis.com/ConversationProfile',
'knowledgebase'                        : 'dialogflow.googleapis.com/KnowledgeBase',
'locationsettings'                     : 'dialogflow.googleapis.com/LocationSettings',
'collection'                           : 'discoveryengine.googleapis.com/Collection',
'datastore'                            : 'discoveryengine.googleapis.com/DataStore',
'engine'                               : 'discoveryengine.googleapis.com/Engine',
'notebook'                             : 'discoveryengine.googleapis.com/Notebook',
'deidentifytemplate'                   : 'dlp.googleapis.com/DeidentifyTemplate',
'discoveryconfig'                      : 'dlp.googleapis.com/DiscoveryConfig',
'dlpjob'                               : 'dlp.googleapis.com/DlpJob',
'inspecttemplate'                      : 'dlp.googleapis.com/InspectTemplate',
'jobtrigger'                           : 'dlp.googleapis.com/JobTrigger',
'storedinfotype'                       : 'dlp.googleapis.com/StoredInfoType',
'dnsmanagedzone'                       : 'dns.googleapis.com/ManagedZone',
'dnspolicy'                            : 'dns.googleapis.com/Policy',
'resourcerecordset'                    : 'dns.googleapis.com/ResourceRecordSet',
'responsepolicy'                       : 'dns.googleapis.com/ResponsePolicy',
'responsepolicyrule'                   : 'dns.googleapis.com/ResponsePolicyRule',
'humanreviewconfig'                    : 'documentai.googleapis.com/HumanReviewConfig',
'labelerpool'                          : 'documentai.googleapis.com/LabelerPool',
'processor'                            : 'documentai.googleapis.com/Processor',
'processorversion'                     : 'documentai.googleapis.com/ProcessorVersion',
'registration'                         : 'domains.googleapis.com/Registration',
'contact'                              : 'essentialcontacts.googleapis.com/Contact',
'eventarcchannel'                      : 'eventarc.googleapis.com/Channel',
'channelconnection'                    : 'eventarc.googleapis.com/ChannelConnection',
'enrollment'                           : 'eventarc.googleapis.com/Enrollment',
'googleapisource'                      : 'eventarc.googleapis.com/GoogleApiSource',
'googlechannelconfig'                  : 'eventarc.googleapis.com/GoogleChannelConfig',
'messagebus'                           : 'eventarc.googleapis.com/MessageBus',
'pipeline'                             : 'eventarc.googleapis.com/Pipeline',
'trigger'                              : 'eventarc.googleapis.com/Trigger',
'filebackup'                           : 'file.googleapis.com/Backup',
'fileinstance'                         : 'file.googleapis.com/Instance',
'filesnapshot'                         : 'file.googleapis.com/Snapshot',
'backtestresult'                       : 'financialservices.googleapis.com/BacktestResult',
'financialservicesdataset'             : 'financialservices.googleapis.com/Dataset',
'engineconfig'                         : 'financialservices.googleapis.com/EngineConfig',
'financialservicesinstance'            : 'financialservices.googleapis.com/Instance',
'financialservicesmodel'               : 'financialservices.googleapis.com/Model',
'predictionresult'                     : 'financialservices.googleapis.com/PredictionResult',
'firebaseappinfo'                      : 'firebase.googleapis.com/FirebaseAppInfo',
'firebaseproject'                      : 'firebase.googleapis.com/FirebaseProject',
'firebaserulesrelease'                 : 'firebaserules.googleapis.com/Release',
'ruleset'                              : 'firebaserules.googleapis.com/Ruleset',
'firestorebackup'                      : 'firestore.googleapis.com/Backup',
'firestoredatabase'                    : 'firestore.googleapis.com/Database',
'gkebackupbackup'                      : 'gkebackup.googleapis.com/Backup',
'gkebackupbackupplan'                  : 'gkebackup.googleapis.com/BackupPlan',
'restore'                              : 'gkebackup.googleapis.com/Restore',
'restoreplan'                          : 'gkebackup.googleapis.com/RestorePlan',
'volumebackup'                         : 'gkebackup.googleapis.com/VolumeBackup',
'volumerestore'                        : 'gkebackup.googleapis.com/VolumeRestore',
'feature'                              : 'gkehub.googleapis.com/Feature',
'fleet'                                : 'gkehub.googleapis.com/Fleet',
'membership'                           : 'gkehub.googleapis.com/Membership',
'membershipbinding'                    : 'gkehub.googleapis.com/MembershipBinding',
'membershipfeature'                    : 'gkehub.googleapis.com/MembershipFeature',
'gkehubnamespace'                      : 'gkehub.googleapis.com/Namespace',
'rbacrolebinding'                      : 'gkehub.googleapis.com/RBACRoleBinding',
'scope'                                : 'gkehub.googleapis.com/Scope',
'attachedcluster'                      : 'gkemulticloud.googleapis.com/AttachedCluster',
'awscluster'                           : 'gkemulticloud.googleapis.com/AwsCluster',
'awsnodepool'                          : 'gkemulticloud.googleapis.com/AwsNodePool',
'azureclient'                          : 'gkemulticloud.googleapis.com/AzureClient',
'azurecluster'                         : 'gkemulticloud.googleapis.com/AzureCluster',
'azurenodepool'                        : 'gkemulticloud.googleapis.com/AzureNodePool',
'baremetaladmincluster'                : 'gkeonprem.googleapis.com/BareMetalAdminCluster',
'baremetalcluster'                     : 'gkeonprem.googleapis.com/BareMetalCluster',
'baremetalnodepool'                    : 'gkeonprem.googleapis.com/BareMetalNodePool',
'vmwareadmincluster'                   : 'gkeonprem.googleapis.com/VmwareAdminCluster',
'vmwarecluster'                        : 'gkeonprem.googleapis.com/VmwareCluster',
'vmwarenodepool'                       : 'gkeonprem.googleapis.com/VmwareNodePool',
'consentstore'                         : 'healthcare.googleapis.com/ConsentStore',
'healthcaredataset'                    : 'healthcare.googleapis.com/Dataset',
'dicomstore'                           : 'healthcare.googleapis.com/DicomStore',
'fhirstore'                            : 'healthcare.googleapis.com/FhirStore',
'hl7v2store'                           : 'healthcare.googleapis.com/Hl7V2Store',
'policyv2'                             : 'iam.googleapis.com/PolicyV2',
'iamrole'                              : 'iam.googleapis.com/Role',
'iamserviceaccount'                    : 'iam.googleapis.com/ServiceAccount',
'serviceaccountkey'                    : 'iam.googleapis.com/ServiceAccountKey',
'tunneldestgroup'                      : 'iap.googleapis.com/TunnelDestGroup',
'accesslevel'                          : 'identity.accesscontextmanager.googleapis.com/AccessLevel',
'accesspolicy'                         : 'identity.accesscontextmanager.googleapis.com/AccessPolicy',
'serviceperimeter'                     : 'identity.accesscontextmanager.googleapis.com/ServicePerimeter',
'identitytoolkitconfig'                : 'identitytoolkit.googleapis.com/Config',
'defaultsupportedidpconfig'            : 'identitytoolkit.googleapis.com/DefaultSupportedIdpConfig',
'inboundsamlconfig'                    : 'identitytoolkit.googleapis.com/InboundSamlConfig',
'oauthidpconfig'                       : 'identitytoolkit.googleapis.com/OauthIdpConfig',
'tenant'                               : 'identitytoolkit.googleapis.com/Tenant',
'idsendpoint'                          : 'ids.googleapis.com/Endpoint',
'authconfig'                           : 'integrations.googleapis.com/AuthConfig',
'integrationscertificate'              : 'integrations.googleapis.com/Certificate',
'integrationsexecution'                : 'integrations.googleapis.com/Execution',
'integration'                          : 'integrations.googleapis.com/Integration',
'integrationversion'                   : 'integrations.googleapis.com/IntegrationVersion',
'sfdcchannel'                          : 'integrations.googleapis.com/SfdcChannel',
'sfdcinstance'                         : 'integrations.googleapis.com/SfdcInstance',
'suspension'                           : 'integrations.googleapis.com/Suspension',
'krmapihost'                           : 'krmapihosting.googleapis.com/KrmApiHost',
'livestreamasset'                      : 'livestream.googleapis.com/Asset',
'livestreamchannel'                    : 'livestream.googleapis.com/Channel',
'input'                                : 'livestream.googleapis.com/Input',
'pool'                                 : 'livestream.googleapis.com/Pool',
'link'                                 : 'logging.googleapis.com/Link',
'logbucket'                            : 'logging.googleapis.com/LogBucket',
'logmetric'                            : 'logging.googleapis.com/LogMetric',
'logsink'                              : 'logging.googleapis.com/LogSink',
'logview'                              : 'logging.googleapis.com/LogView',
'recentquery'                          : 'logging.googleapis.com/RecentQuery',
'savedquery'                           : 'logging.googleapis.com/SavedQuery',
'loggingsettings'                      : 'logging.googleapis.com/Settings',
'lookerinstance'                       : 'looker.googleapis.com/Instance',
'domain'                               : 'managedidentities.googleapis.com/Domain',
'managedkafkacluster'                  : 'managedkafka.googleapis.com/Cluster',
'connectclusters'                      : 'managedkafka.googleapis.com/connectClusters',
'memcacheinstance'                     : 'memcache.googleapis.com/Instance',
'metastorebackup'                      : 'metastore.googleapis.com/Backup',
'federation'                           : 'metastore.googleapis.com/Federation',
'metadataimport'                       : 'metastore.googleapis.com/MetadataImport',
'metastoreservice'                     : 'metastore.googleapis.com/Service',
'alertpolicy'                          : 'monitoring.googleapis.com/AlertPolicy',
'dashboard'                            : 'monitoring.googleapis.com/Dashboard',
'notificationchannel'                  : 'monitoring.googleapis.com/NotificationChannel',
'snooze'                               : 'monitoring.googleapis.com/Snooze',
'uptimecheckconfig'                    : 'monitoring.googleapis.com/UptimeCheckConfig',
'activedirectory'                      : 'netapp.googleapis.com/ActiveDirectory',
'netappbackup'                         : 'netapp.googleapis.com/Backup',
'backuppolicy'                         : 'netapp.googleapis.com/BackupPolicy',
'netappbackupvault'                    : 'netapp.googleapis.com/BackupVault',
'kmsconfig'                            : 'netapp.googleapis.com/KmsConfig',
'replication'                          : 'netapp.googleapis.com/Replication',
'netappsnapshot'                       : 'netapp.googleapis.com/Snapshot',
'netappstoragepool'                    : 'netapp.googleapis.com/StoragePool',
'volume'                               : 'netapp.googleapis.com/Volume',
'hub'                                  : 'networkconnectivity.googleapis.com/Hub',
'hubroute'                             : 'networkconnectivity.googleapis.com/HubRoute',
'policybasedroute'                     : 'networkconnectivity.googleapis.com/PolicyBasedRoute',
'routetable'                           : 'networkconnectivity.googleapis.com/RouteTable',
'spoke'                                : 'networkconnectivity.googleapis.com/Spoke',
'connectivitytest'                     : 'networkmanagement.googleapis.com/ConnectivityTest',
'addressgroup'                         : 'networksecurity.googleapis.com/AddressGroup',
'authorizationpolicy'                  : 'networksecurity.googleapis.com/AuthorizationPolicy',
'cienttlspolicy'                       : 'networksecurity.googleapis.com/CientTlsPolicy',
'firewallendpoint'                     : 'networksecurity.googleapis.com/FirewallEndpoint',
'firewallendpointassociation'          : 'networksecurity.googleapis.com/FirewallEndpointAssociation',
'gatewaysecuritypolicy'                : 'networksecurity.googleapis.com/GatewaySecurityPolicy',
'gatewaysecuritypolicyrule'            : 'networksecurity.googleapis.com/GatewaySecurityPolicyRule',
'securityprofile'                      : 'networksecurity.googleapis.com/SecurityProfile',
'securityprofilegroup'                 : 'networksecurity.googleapis.com/SecurityProfileGroup',
'servertlspolicy'                      : 'networksecurity.googleapis.com/ServerTlsPolicy',
'networksecuritytlsinspectionpolicy'   : 'networksecurity.googleapis.com/TlsInspectionPolicy',
'urllist'                              : 'networksecurity.googleapis.com/UrlList',
'edgecachekeyset'                      : 'networkservices.googleapis.com/EdgeCacheKeyset',
'edgecacheorigin'                      : 'networkservices.googleapis.com/EdgeCacheOrigin',
'edgecacheservice'                     : 'networkservices.googleapis.com/EdgeCacheService',
'endpointpolicy'                       : 'networkservices.googleapis.com/EndpointPolicy',
'networkservicesgateway'               : 'networkservices.googleapis.com/Gateway',
'grpcroute'                            : 'networkservices.googleapis.com/GrpcRoute',
'httproute'                            : 'networkservices.googleapis.com/HttpRoute',
'lbrouteextension'                     : 'networkservices.googleapis.com/LbRouteExtension',
'lbtrafficextension'                   : 'networkservices.googleapis.com/LbTrafficExtension',
'mesh'                                 : 'networkservices.googleapis.com/Mesh',
'servicebinding'                       : 'networkservices.googleapis.com/ServiceBinding',
'servicelbpolicy'                      : 'networkservices.googleapis.com/ServiceLbPolicy',
'tcproute'                             : 'networkservices.googleapis.com/TcpRoute',
'tlsroute'                             : 'networkservices.googleapis.com/TlsRoute',
'wasmplugin'                           : 'networkservices.googleapis.com/WasmPlugin',
'wasmpluginversion'                    : 'networkservices.googleapis.com/WasmPluginVersion',
'notebooksinstance'                    : 'notebooks.googleapis.com/Instance',
'autonomousdatabase'                   : 'oracledatabase.googleapis.com/AutonomousDatabase',
'cloudexadatainfrastructure'           : 'oracledatabase.googleapis.com/CloudExadataInfrastructure',
'cloudvmcluster'                       : 'oracledatabase.googleapis.com/CloudVmCluster',
'customconstraint'                     : 'orgpolicy.googleapis.com/CustomConstraint',
'orgpolicypolicy'                      : 'orgpolicy.googleapis.com/Policy',
'ospolicyassignment'                   : 'osconfig.googleapis.com/OSPolicyAssignment',
'ospolicyassignmentreport'             : 'osconfig.googleapis.com/OSPolicyAssignmentReport',
'patchdeployment'                      : 'osconfig.googleapis.com/PatchDeployment',
'vulnerabilityreport'                  : 'osconfig.googleapis.com/VulnerabilityReport',
'capool'                               : 'privateca.googleapis.com/CaPool',
'privatecacertificate'                 : 'privateca.googleapis.com/Certificate',
'certificateauthority'                 : 'privateca.googleapis.com/CertificateAuthority',
'certificaterevocationlist'            : 'privateca.googleapis.com/CertificateRevocationList',
'certificatetemplate'                  : 'privateca.googleapis.com/CertificateTemplate',
'grant'                                : 'privilegedaccessmanager.googleapis.com/Grant',
'schema'                               : 'pubsub.googleapis.com/Schema',
'pubsubsnapshot'                       : 'pubsub.googleapis.com/Snapshot',
'subscription'                         : 'pubsub.googleapis.com/Subscription',
'topic'                                : 'pubsub.googleapis.com/Topic',
'recaptchaenterprisefirewallpolicy'    : 'recaptchaenterprise.googleapis.com/FirewallPolicy',
'recaptchaenterprisekey'               : 'recaptchaenterprise.googleapis.com/Key',
'rediscluster'                         : 'redis.googleapis.com/Cluster',
'redisinstance'                        : 'redis.googleapis.com/Instance',
'catalog'                              : 'retail.googleapis.com/Catalog',
'domainmapping'                        : 'run.googleapis.com/DomainMapping',
'runexecution'                         : 'run.googleapis.com/Execution',
'runjob'                               : 'run.googleapis.com/Job',
'revision'                             : 'run.googleapis.com/Revision',
'runservice'                           : 'run.googleapis.com/Service',
'secretmanagersecret'                  : 'secretmanager.googleapis.com/Secret',
'secretversion'                        : 'secretmanager.googleapis.com/SecretVersion',
'securesourcemanagerinstance'          : 'securesourcemanager.googleapis.com/Instance',
'bigqueryexport'                       : 'securitycenter.googleapis.com/BigQueryExport',
'containerthreatdetectionsettings'     : 'securitycenter.googleapis.com/ContainerThreatDetectionSettings',
'eventthreatdetectionsettings'         : 'securitycenter.googleapis.com/EventThreatDetectionSettings',
'muteconfig'                           : 'securitycenter.googleapis.com/MuteConfig',
'notificationconfig'                   : 'securitycenter.googleapis.com/NotificationConfig',
'resourcevalueconfig'                  : 'securitycenter.googleapis.com/ResourceValueConfig',
'securityhealthanalyticssettings'      : 'securitycenter.googleapis.com/SecurityHealthAnalyticsSettings',
'virtualmachinethreatdetectionsettings': 'securitycenter.googleapis.com/VirtualMachineThreatDetectionSettings',
'websecurityscannersettings'           : 'securitycenter.googleapis.com/WebSecurityScannerSettings',
'eventthreatdetectioncustommodule'     : 'securitycentermanagement.googleapis.com/EventThreatDetectionCustomModule',
'securitycenterservice'                : 'securitycentermanagement.googleapis.com/SecurityCenterService',
'securityhealthanalyticscustommodule'  : 'securitycentermanagement.googleapis.com/SecurityHealthAnalyticsCustomModule',
'posture'                              : 'securityposture.googleapis.com/Posture',
'posturedeployment'                    : 'securityposture.googleapis.com/PostureDeployment',
'servicedirectoryendpoint'             : 'servicedirectory.googleapis.com/Endpoint',
'servicedirectorynamespace'            : 'servicedirectory.googleapis.com/Namespace',
'servicedirectoryservice'              : 'servicedirectory.googleapis.com/Service',
'managedservice'                       : 'servicemanagement.googleapis.com/ManagedService',
'servicenetworkingconnection'          : 'servicenetworking.googleapis.com/Connection',
'serviceusageservice'                  : 'serviceusage.googleapis.com/Service',
'spannerbackup'                        : 'spanner.googleapis.com/Backup',
'spannerdatabase'                      : 'spanner.googleapis.com/Database',
'spannerinstance'                      : 'spanner.googleapis.com/Instance',
'instanceconfig'                       : 'spanner.googleapis.com/InstanceConfig',
'phrase'                               : 'speakerid.googleapis.com/Phrase',
'speakeridsettings'                    : 'speakerid.googleapis.com/Settings',
'speaker'                              : 'speakerid.googleapis.com/Speaker',
'speechconfig'                         : 'speech.googleapis.com/Config',
'customclass'                          : 'speech.googleapis.com/CustomClass',
'phraseset'                            : 'speech.googleapis.com/PhraseSet',
'recognizer'                           : 'speech.googleapis.com/Recognizer',
'sqladminbackup'                       : 'sqladmin.googleapis.com/Backup',
'backuprun'                            : 'sqladmin.googleapis.com/BackupRun',
'sqladmininstance'                     : 'sqladmin.googleapis.com/Instance',
'bucket'                               : 'storage.googleapis.com/Bucket',
'reportconfig'                         : 'storageinsights.googleapis.com/ReportConfig',
'reportdetail'                         : 'storageinsights.googleapis.com/ReportDetail',
'transferjob'                          : 'storagetransfer.googleapis.com/TransferJob',
'tpunode'                              : 'tpu.googleapis.com/Node',
'transcoderjob'                        : 'transcoder.googleapis.com/Job',
'jobtemplate'                          : 'transcoder.googleapis.com/JobTemplate',
'cdnkey'                               : 'videostitcher.googleapis.com/CdnKey',
'liveconfig'                           : 'videostitcher.googleapis.com/LiveConfig',
'slate'                                : 'videostitcher.googleapis.com/Slate',
'vodconfig'                            : 'videostitcher.googleapis.com/VodConfig',
'clonejob'                             : 'vmmigration.googleapis.com/CloneJob',
'cutoverjob'                           : 'vmmigration.googleapis.com/CutoverJob',
'datacenterconnector'                  : 'vmmigration.googleapis.com/DatacenterConnector',
'group'                                : 'vmmigration.googleapis.com/Group',
'imageimport'                          : 'vmmigration.googleapis.com/ImageImport',
'migratingvm'                          : 'vmmigration.googleapis.com/MigratingVm',
'source'                               : 'vmmigration.googleapis.com/Source',
'targetproject'                        : 'vmmigration.googleapis.com/TargetProject',
'utilizationreport'                    : 'vmmigration.googleapis.com/UtilizationReport',
'vmwareenginecluster'                  : 'vmwareengine.googleapis.com/Cluster',
'externalaccessrule'                   : 'vmwareengine.googleapis.com/ExternalAccessRule',
'externaladdress'                      : 'vmwareengine.googleapis.com/ExternalAddress',
'networkpeering'                       : 'vmwareengine.googleapis.com/NetworkPeering',
'vmwareenginenetworkpolicy'            : 'vmwareengine.googleapis.com/NetworkPolicy',
'privatecloud'                         : 'vmwareengine.googleapis.com/PrivateCloud',
'vmwareengineprivateconnection'        : 'vmwareengine.googleapis.com/PrivateConnection',
'vmwareenginenetwork'                  : 'vmwareengine.googleapis.com/VmwareEngineNetwork',
'connector'                            : 'vpcaccess.googleapis.com/Connector',
'scanconfig'                           : 'websecurityscanner.googleapis.com/ScanConfig',
'workflow'                             : 'workflows.googleapis.com/Workflow',
'workstation'                          : 'workstations.googleapis.com/Workstation',
'workstationcluster'                   : 'workstations.googleapis.com/WorkstationCluster',
'workstationconfig'                    : 'workstations.googleapis.com/WorkstationConfig',
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

def fetch_flat_resources(scope, asset_type, folders_dict, debug=False):
    """
    Fetches GCP resources of a specific type for the given scope.

    Args:
        scope: The GCP scope to search within (e.g., organizations/123456789)
        asset_type: The type of resource to fetch (e.g., compute.googleapis.com/Instance)
        folders_dict: Dictionary mapping folder IDs to display names
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

            # Build path from folders hierarchy
            path_parts = []
            if hasattr(resource, 'folders') and resource.folders:
                for folder_id in reversed(resource.folders):
                    # Extract folder ID without 'folders/' prefix
                    folder_id_clean = folder_id.split('/')[-1] if '/' in folder_id else folder_id
                    if folder_id_clean in folders_dict:
                        path_parts.append(folders_dict[folder_id_clean])
                    else:
                        path_parts.append(folder_id_clean)  # Fallback to ID if name not found

            # Extract project ID from parentFullResourceName
            project_id = resource.parent_full_resource_name.split('/')[-1] if resource.parent_full_resource_name else 'Unknown'
            path_parts.append(project_id)
            resource_dict['path'] = '/'.join(path_parts)

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
        print(f"Error fetching resources: {e}")
        return []

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
    Prints resources in a tabular format.

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

    headers = ["Name", "Project ID", "Location", "Full Path"]
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
        path = resource.get('path', '')

        # Escape double quotes and handle commas
        short_name = short_name.replace('"', '""')
        project_id = project_id.replace('"', '""')
        location = location.replace('"', '""')
        path = path.replace('"', '""')

        row_data = [
            short_name,
            project_id,
            location,
            path
        ]
        rows.append(row_data)

    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, field in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(field)))

    # Create format strings
    header_format_string = "  ".join(["{:<" + str(w) + "}" for w in col_widths])
    row_format_string = "  ".join(["{:<" + str(w) + "}" for w in col_widths])

    # Print table
    print()
    print(header_format_string.format(*headers))
    print("-" * (sum(col_widths) + len(col_widths) * 2))

    for row_data in rows:
        print(row_format_string.format(*row_data))

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

def get_folders_dict(scope):
    """
    Fetches all folders in the given scope and returns a dictionary
    mapping folder ID to display name.

    Args:
        scope: GCP scope (e.g., organizations/123456789)

    Returns:
        Dict[str, str]: {folder_id: display_name}
    """
    client = asset_v1.AssetServiceClient()
    response = client.search_all_resources(
        request={
            "scope": scope,
            "asset_types": ["cloudresourcemanager.googleapis.com/Folder"],
            "read_mask": "name,displayName"
        }
    )

    folders_dict = {}
    for resource in response:
        # Extract folder ID from resource name
        folder_id = resource.name.split('/')[-1]
        folders_dict[folder_id] = resource.display_name

    return folders_dict

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
    print("Name,Project ID,Location,Scope,Full Path")

    # Print each resource
    for resource in resources:
        name_parts = resource['name'].split('/')
        short_name = name_parts[-1] if name_parts else resource['name']
        project_id = resource['project']
        location = resource.get('location', '')
        path = resource.get('path', '')

        # Escape double quotes and handle commas
        short_name = short_name.replace('"', '""')
        project_id = project_id.replace('"', '""')
        location = location.replace('"', '""')
        scope_str = scope.replace('"', '""')
        path = path.replace('"', '""')

        print(f'"{short_name}","{project_id}","{location}","{scope_str}","{path}"')

def main():
    parser = argparse.ArgumentParser(description="GCP Asset Lister CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    hierarchy_parser = subparsers.add_parser('hierarchy', help='Display asset hierarchy (folders, projects).')
    hierarchy_parser.add_argument('-s', '--scope', required=True, help='GCP organization scope (e.g. organizations/123456789)')
    hierarchy_parser.add_argument('-f', '--format', choices=['tree', 'json', 'tabular', 'pretty'], default='tree', help='Output format')

    list_resources_parser = subparsers.add_parser('list-resources', help='List resources of a specific type.')
    list_resources_parser.add_argument('-s', '--scope', required=True, help='GCP organization scope (e.g. organizations/123456789)')
    list_resources_parser.add_argument('-t', '--type', required=True, help='Resource type to list (e.g., compute.googleapis.com/Instance)')
    list_resources_parser.add_argument('-f', '--format', choices=['json', 'tabular', 'csv'], default='tabular', help='Output format')
    list_resources_parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')

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
        # Convert user input to lowercase for case-insensitive lookup
        asset_type_key = args.type.lower()
        asset_type = asset_type_mapping.get(asset_type_key, args.type)

        folders_dict = get_folders_dict(scope)

        if not args.debug:
            spinner = Spinner(f"Fetching {args.type} resources... ")
            spinner.start()

        try:
            resources = fetch_flat_resources(scope, asset_type, folders_dict, args.debug)
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
