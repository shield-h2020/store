import resources.vnsf_element as vnsf_element
import resources.vnsfs as vnsfs
import endpoints_base

resources = [
    {
        'resource': '/' + endpoints_base.ENDPOINT_VNSFS,
        'handler': vnsfs.Vnsf
    },
    {
        'resource': '/' + endpoints_base.ENDPOINT_VNSFS + '/<string:vnsf_id>',
        'handler': vnsf_element.VnsfElement
    }
]
