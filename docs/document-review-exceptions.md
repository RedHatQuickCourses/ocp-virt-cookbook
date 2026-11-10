# Documentation review rules and page types

Run `python3 scripts/review-docs.py --all` from the repository root. After the
warning cleanup for [issue #377](https://github.com/RedHatQuickCourses/ocp-virt-cookbook/issues/377),
the 103 pages and navigation files report **0 errors and 0 warnings**. No
intentional exceptions remain. The rules below recognize valid document formats
and YAML conventions. No checks are disabled.

## Empty YAML mappings are supported

The `yaml-flow-syntax` check accepts empty mappings such as `devices: {}`,
`resources: {}`, `pod: {}`, and `masquerade: {}`, including whitespace inside
the braces. These no longer produce warnings or need exceptions.

YAML block style cannot express an empty mapping. Keep `{}` when an example
needs an empty object: replacing it with a bare key produces `null`, and removing
the key can change the configuration. Nonempty flow mappings and inline flow
sequences still produce warnings.

## AsciiDoc attributes inside scalars are supported

The `yaml-flow-syntax` check recognizes attribute references embedded in scalar
values, such as `image: quay.io/openshift-release-dev/ocp-release:{ocp-min-version}.20-x86_64`.
These references no longer produce warnings or need exceptions. Actual flow
collections still produce warnings, including collections containing attributes.

Quote an attribute used as an entire YAML scalar, for example
`version: "{ocp-min-version}"`, to distinguish it from a single-key flow mapping.

## Page types

All 82 content pages now declare their types: 74 tutorials, 2 references, 5
troubleshooting guides, and 1 setup reference. Index and navigation files do not
require a type.

For compatibility, pages without a type default to `tutorial`. A non-index page
with no declared type, an explicit `tutorial` type, or an unrecognized type must
include `== Prerequisites` and either `== Summary` or `== Verification`.

Declare the page type in the document header, after the title and before the first
blank line:

```asciidoc
= API Component Overview
:navtitle: API Component Overview
:page-type: reference
```

The `tutorial-sections` check accepts `reference`, `troubleshooting`, and `setup`
as non-tutorial page types. These pages keep their own topic, requirements, or
diagnostic sections. General formatting, YAML, and link checks still apply.
Metadata shown in the document body or in a code example does not change the
page type used by the check.

The following non-tutorial pages declare their formats explicitly:

| File | `page-type` |
| --- | --- |
| [API component overview](../modules/api/pages/api-component-overview.adoc) | `reference` |
| [Glossary](../modules/appendix/pages/glossary.adoc) | `reference` |
| [Prerequisites and setup](../modules/getting-started/pages/prerequisites.adoc) | `setup` |
| [Cloud-init troubleshooting](../modules/networking/pages/cloud-init-troubleshooting.adoc) | `troubleshooting` |
| [OVS bridge troubleshooting](../modules/networking/pages/ovs-bridge-troubleshooting.adoc) | `troubleshooting` |
| [LVM troubleshooting](../modules/storage/pages/lvm-troubleshooting.adoc) | `troubleshooting` |
| [Linux remote access troubleshooting](../modules/vm-configuration/pages/remote-access-linux-troubleshooting.adoc) | `troubleshooting` |
| [Golden images troubleshooting](../modules/vm-lifecycle/pages/golden-images-troubleshooting.adoc) | `troubleshooting` |
