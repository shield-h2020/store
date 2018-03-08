# vNSF Packaging

## Contents


### Elements

To foster VNF reuse and remove SHIELD applicability barriers the SHIELD VNF package format extends existing VNF formats by introducing:

* a security manifest to ensure VNF tamper-proofing
* a digitally-signed security manifest to prove provenance and integrity
* support for including Orchestrator-specific VNF package format
* a .tar.gz package format to enclose everything

A SHIELD vNSF package (`.tar.gz` file) comprises:

| Element | Format | Purpose |
|-|-|-
| manifest.yaml | YAML | Security manifest which defines the tamper-proof metadata to ensure the vNSF in operation wasn't tampered with since when it was onboarded
| *&lt;vnf_package_file\>* | Orchestrator specific | The VNF package to onboard into the vNSF Orchestrator

### Structure

The structure of a SHIELD vNSF package is as follows:

```bash
.
├── manifest.yaml           # SHIELD security manifest
└── <vnf_package_file>      # Orchestrator-specific VNF package
```

This packaging is Orchestrator agnostic and allows for onboarding an existing VNF into SHIELD simply by providing a security manifest tailored to the VNF in question. Once this is done it is just a matter of producing a .tar.gz file with the contents mentioned and submit it to the Store.

### Datamodel

#### Security manifest (`manifest.yaml`)

**Elements**

| Field | Purpose |
|-|-
| manifest:vnsf | Defines a SHIELD vNSF package
| type | The type of VNF the manifest describes. Allowed values: `OSM`
| package | VNF file name within the SHIELD package. This file name, contents and format is Orchestrator specific. This manifest only identifies the file which holds the VNF package
| hash | The message digest for the VNF package mentioned in the package field
| descriptor | VNF Descriptor file within the VNF-specific package. Tipically a path to the actual file itself
| properties | vNSF characterization and purpose-related details
| security_info | The metadata used for attestation purposes to ensure the VNF wasn't tampred with

**Example**

```yaml
manifest:vnsf:
    type: OSM
    package: cirros_vnf.tar.gz
    hash: <image_hash_here>
    descriptor: cirros_vnf/cirros_vnfd.yaml
    properties:
        vendor: some vendor name
        capabilities: ['Virtual Cirr OS']
    security_info:
        vdu:
          - id: cirros_vnf-VM
            hash: <image_hash_here>
            attestation:
                some_key: <TBD - provided by TM>
                some_key: <TBD - provided by TM>
                some_key: <TBD - provided by TM>
                some_group: <TBD - provided by TM>
                  some_key: <TBD - provided by TM>
                  some_key: <TBD - provided by TM>
```

## Examples


### OSM VNF packaging

#### Elements

The SHIELD vNSF package extends the OSM VNF package definition by adding the security details. The SHIELD vNSF package is thus a wrapper that contains the following elements, marked as *(M)*andatory or *(O)*ptional:

Element | Contents | Source
-|-|-
manifest.yaml | (M) package contents definition along with the security information | SHIELD
*&lt;vnf_name\>*_vnfd.yaml | (M) vNSF descriptor information. Follows the [OSM Information Model](https://osm.etsi.org/wikipub/images/2/26/OSM_R2_Information_Model.pdf) (page 47) | OSM
charms | (O) [juju charm](https://jujucharms.com/) configuration for the VNF | OSM
checksums.txt | (M) image file(s) hash(es) | OSM
cloud_init | (O) instantiation configurations | OSM
icons | (O) used on the OSM Composer | OSM
images | (O) VDU image files for the vNSF | OSM
README | (O) vNSF related information | OSM
scripts | (O) base configuration scripts once the vNSF is up and running | OSM

#### Structure

The structure of a SHIELD vNSF package is as follows:

```bash
.
├── manifest.yaml           # SHIELD
└── <vnf_name>.tar.gz       # OSM VNF package
```

The structure of the OSM VNF package is:

```bash
.
├── <vnf_name>_vnf              # OSM
    ├── charms                  # OSM
    ├── checksums.txt           # OSM
    ├── cloud_init              # OSM
    ├── icons                   # OSM
    ├── images                  # OSM
    ├── README                  # OSM
    ├── scripts                 # OSM
    └── <vnf_name>_vnfd.yaml    # OSM
```

#### Example

**Security manifest** (`manifest.yaml`)

```yaml
manifest:vnsf:
    type: OSM
    package: cirros_vnf.tar.gz
    descriptor: cirros_vnf/cirros_vnfd.yaml
    properties:
        vendor: some vendor name
        capabilities: ['Virtual Cirr OS']
    security_info:
        vdu:
          - id: cirros_vnf-VM
            hash: <image_hash_here>
            attestation:
                some_key: <TBD - provided by TM>
                some_key: <TBD - provided by TM>
                some_key: <TBD - provided by TM>
                some_group: <TBD - provided by TM>
                  some_key: <TBD - provided by TM>
                  some_key: <TBD - provided by TM>
```

**OSM VNF Descriptor** (`cirros_vnfd.yaml`)

```yaml
vnfd:vnfd-catalog:
    vnfd:
    -   id: cirros_vnfd
        name: cirros_vnfd
        short-name: cirros_vnfd
        description: Simple VNF example with a cirros
        vendor: OSM
        version: '1.0'

        # Place the logo as png in icons directory and provide the name here
        logo: cirros-64.png

        # Management interface
        mgmt-interface:
            vdu-id: cirros_vnfd-VM

        # Atleast one VDU need to be specified
        vdu:
        -   id: cirros_vnfd-VM
            name: cirros_vnfd-VM
            description: cirros_vnfd-VM
            count: 1

            # Flavour of the VM to be instantiated for the VDU
            vm-flavor:
                vcpu-count: 1
                memory-mb: 512
                storage-gb: 1

            # Image/checksum or image including the full path
            image: cirros034
            #checksum:

            external-interface:
            # Specify the external interfaces
            # There can be multiple interfaces defined
            -   name: eth0
                virtual-interface:
                    type: OM-MGMT
                    bandwidth: '0'
                    vpci: 0000:00:0a.0
                vnfd-connection-point-ref: eth0

        connection-point:
            -   name: eth0
                type: VPORT
```

#### SHIELD Package Generation

A SHIELD vNSF package can be generated by leveraging on the [OSM VNF packet generation](https://osm.etsi.org/wikipub/index.php/Creating_your_own_VNF_package_%28Release_TWO%29), then adding the extra files introduced for the SHIELD vNSFs.

```bash
git clone https://osm.etsi.org/gerrit/osm/descriptor-packages
# Single-VM VNF package
./descriptor-packages/src/generate_descriptor_pkg.sh -t vnfd --image <IMAGE_PATH> -c <VNF_NAME>
# Edit YAML files to fit to the vNSF (adding VMs, VLDs, images, resources and so on)
# Define and customise the SHIELD vNSF manifest
touch manifest.yaml
# Provide the md5sum for each file in the SHIELD vNSF package
touch <VNF_NAME>_vnfd/checksums.txt
# Generate final .tar.gz
tar -zcvf <VNF_NAME>_vnfd.tar.gz <VNF_NAME>_vnfd manifest.yaml
```
