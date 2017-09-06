# vNSF Onboarding

Onboarding a vNSF comprises several steps to ensure the data provided complies with the SHIELD constraints and policies. To avoid potential vNSF misbehaviour or malfunction the onboarding process encompasses an approval stage. In this stage the vNSF is registered but kept on a sandboxed state which makes it only visible to the Service Provider. Once this Service Provider deems the vNSF approved, it will be available in the Store for all the other users. Whilst the vNSF is sandboxed the Service Provider can perform any kind of validations to ensure the vNSF delivers as expected. To perform such validations a special kind of tenant may be used to provide a self-contained environment where the vNSF runs and allows the Service Provider to perform the validation in any way, shape or form, be it only the vNSF lifecycle (start/stop/etc.), any additional traffic or behaviour analysis, or operating as integrated in a NS (instantiated for the approval stage).

![vNSF Onboarding](https://www.websequencediagrams.com/cgi-bin/cdraw?lz=cGFydGljaXBhbnQgRGV2ZWxvcGVyCgAKDFN0b3JlAAUNQ2F0YWxvZ3UACA5TZXJ2aWNlIFByb3ZpZGVyIGFzIFNQCgpub3RlIG92ZXIAVgo6AGEKIGF1dGhvcml6ZWQKAHcJLT4AcAU6IFN1Ym1pdCB2TlNGCgCBAwUAEQlWYWxpZGF0ZSBkZXNjcmlwdG9yABsHLT4AXQsAOwZ0aW5nIChyZXEuIGlkKQCBBwsAgVcFLFNQOiBPdXQtb2YtYmFuZCBvcGVyYXRpb24gZHVlIHRvIHRpbWUtY29uc3VtaW5nIGNoZWNrcwoKbG9vcACBFwUgQ29tcG9uZW50cwCBGA9DaGVjayBpbWFnZSBpbnRlZ3JpdHkKZW5kCgCBSAgAgkQJOiBSZWdpc3RlcgBOBihzYW5kYm94ZWQpCgCCaQktAIISCQBzBWlkCgBACStTUAAPB29uYm9hcmRlZCAoAB8HAIFtB3JpZ2h0IG9mIFNQAII3C3ZOU0ZcbihvAIFuFCkKU1AtPi0AgwgHQXBwcm92AEsNAIE0EgCCDAVyZWFkeQAVEgCDdwsAgRoQAIMLEwCFBwkAgx0FAE0LZm9yIGRlcGxveW1lbnQKCg&s=rose)