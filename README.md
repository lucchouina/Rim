Rim
===

Release Image Management - model driven appliance life cycle management for Linux


Rim is the culmination of over 10 years of work in the Linux appliance platform development with influences 
from domains like core 
telecomminications router, multi-tiered wireless RAN communication deployments, embedded high speed in-line or 
side-line network security appliances and multi-tiered physical security deployments.

Rim's focus is on the platform and its life-cycle. How it meets the need of the applications it supports, how to
make sure these applications have what they need to be efficiently developpped, tested, debuged, upgraded.

The platform needs to be an enabler and never stand in the way of service delivery.  Developpers should be able 
to integrate in a very clear way with the platform, every time a feature is judged common to multiple components of the 
service, specific APIs and configuration schemas must be inforced to deliver these features to these components.

Example basic features are - scratch installs, upgrades, downgrades, revert-to-factory, out-of-the-box
configuration, backups and restorations, high availability (ha), desaster recovery (dr). Rim supports all of these 
except for ha and dr at the moment.

For all other features that are omnipresent in todays products - scripting languages, logging APis 
and log rotation, databases, java engine, tomcat applet, a NtoM messaging layer, web server, firewall,
application corefile management, system crash dump management, watchdog management - application components must
me able to integrate with and make use of in a well defined and using drop-in mechanism. Rim currently
has supports for all of these (and the list will keep growing).

Basic behavior, must be defined to be the survival of the services the platofrm supports not of individual processes. 
There is an implcit agreement that there will always be bugs and the role of the platform is to mitigate the impact
of these bugs on the availability of the service the platform supplies. 

The implication of the above statement is far reaching. One of its implication is the need to move away from standard
distributions that target a certain personnality (desktop, enterprise) or certain scope (Embedded this or
Embedded that). The later often forgetting some of the more overarching needs of ongoing busineses, which include
very long life cycles for products, many different types of hardware for the same application, multiple tiers of 
product working together (tier 1 gathers input and data, tier 2 is in the proximity of tier 1 and implements
a higher level of intelligance, tier 3 integrates level 1 and 2 and implement a more geocentric maanagement 
interface the end user).

In the case of multi-tiered deployments, Rim has support for the control of software upgrade flows from a master to
it slaves (tier 3 to tier 2 to tier 1), the inforcement of a strict compatibility matrix, and martialling of the
associated upgrades and downgrades of the nodes involved. 

Rim software delivery is based on a set of discrete software components that are use in read-only mode and for which
a bill of meterial (BOM) provides a md5 digest. Each such component is targetted to a specific node personality, for example
tier1, tier2 or tier3, and a specific architecture, for example Arm, PPC, i686, x86_64. The list of components that
make up a node is defined by the model that says what service is made up of what component and what type of hardware
architecture can assume this type of personality in normal deployment. 

If the build process associated with a component can always generate the same software (given that RIM build
environments are all self contained in that the RIM itself, the software roots and the cross-compilers are also version
controlled, that should not be difficult) then the packaging itself will also generate the same md5 for the
assocociated read-only software components.  This produces a build flow that generate incremental changes in the 
md5 digests of affected components. Combined with the fact that these components are accessed read-only at
run-time, upgrades really become a process of comparing 2 BOMs and coying the components with 
new md5 digests. The new components will flow through to the nodes that are a valid consumer of these ocmponents and
will skip others. Common software components on a node are shared accross version through the magic of filesystem
hard links.

The wiki will explore more features of RIM and in more details.


