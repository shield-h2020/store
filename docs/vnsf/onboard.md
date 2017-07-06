
> work in progress


# vNSF Packaging

## Contents

The vNSF package extends the OSM definition by adding the security details. The SHIELD vNSF package has the following elements, marked as *(M)*andatory or *(O)*ptional:


Element | Contents | Source
-|-|-
manifest.yaml | (M) package contents definition along with the security information | SHIELD
*&lt;vnf_name\>*_vnfd.yaml | (M) vNSF descriptor information. Follows the [OSM Information Model](https://osm.etsi.org/wikipub/images/0/0c/Osm-r1-information-model-descriptors.pdf) (page 47) | OSM
images | (O) VDU image files for the vNSF | OSM
scripts | (O) base configuration scripts once the vNSF is up and running | OSM
icons | (O) used on the OSM Composer | OSM
charms | (O) [juju charm](https://jujucharms.com/) configuration for the VNF | OSM
cloud_init | (O) instantiation configurations | OSM
checksums.txt | (M) image file(s) hash(es) | OSM
README | (O) vNSF related information | OSM


## Data Model

`manifest.yaml`

```yaml
manifest:vnsf:
    descriptor: xpto_vnfd/xpto_vnfd.yaml
    type: OSM
    security:
        vdu:
        -   id: xpto_vnfd-VM
            hash: 7fb693dfd95a14dd6ef6df837c872027
            attestation:
                key: <TBD - provided by TM>
```
