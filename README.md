[comment]: # "Auto-generated SOAR connector documentation"
# IntSights

Publisher: IntSights  
Connector Version: 4\.2\.0  
Product Vendor: IntSights  
Product Name: IntSights Cyber Intelligence  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.4\.0  

This app integrates with IntSights Cyber Intelligence

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2019-2023 IntSights Cyber Intelligence Ltd."
[comment]: # ""
[comment]: # "  This unpublished material is proprietary to IntSights."
[comment]: # "  All rights reserved. The methods and"
[comment]: # "  techniques described herein are considered trade secrets"
[comment]: # "  and/or confidential. Reproduction or distribution, in whole"
[comment]: # "  or in part, is forbidden except by express written permission"
[comment]: # "  of IntSights."
[comment]: # ""
[comment]: # "  Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "  you may not use this file except in compliance with the License."
[comment]: # "  You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "      http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # "  Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "  the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "  either express or implied. See the License for the specific language governing permissions"
[comment]: # "  and limitations under the License."
[comment]: # ""
## Port Information

The app uses HTTP/ HTTPS protocol for communicating with the IntSights server. Below are the default
ports used by the Splunk SOAR Connector.

| SERVICE NAME | TRANSPORT PROTOCOL | PORT |
|--------------|--------------------|------|
| http         | tcp                | 80   |
| https        | tcp                | 443  |


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a IntSights Cyber Intelligence asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**account\_id** |  required  | string | User's Account ID
**api\_key** |  required  | password | User's API Key

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity  
[hunt ioc](#action-hunt-ioc) - Look for information about an ioc in the Intsights database  
[enrich ioc](#action-enrich-ioc) - Get enrichment information on IOC using the \(paid\) enrich API endpoint  
[hunt file](#action-hunt-file) - Look for information about a file hash in the Intsights database  
[hunt domain](#action-hunt-domain) - Look for information about a domain in the Intsights database  
[hunt ip](#action-hunt-ip) - Look for information about an IP in the Intsights database  
[hunt url](#action-hunt-url) - Look for information about a URL in the Intsights database  
[on poll](#action-on-poll) - Callback action for the on\_poll ingest functionality  
[close alert](#action-close-alert) - Close an alert in the IntSights dashboard  
[takedown request](#action-takedown-request) - Initiate a takedown request of an alert from the IntSights dashboard  

## action: 'test connectivity'
Validate the asset configuration for connectivity

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'hunt ioc'
Look for information about an ioc in the Intsights database

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**hunting** |  required  | Look for information about an ioc in the Intsights database | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.hunting | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
action\_result\.status | string | 
action\_result\.data | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'enrich ioc'
Get enrichment information on IOC using the \(paid\) enrich API endpoint

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ioc** |  required  | The IOC to enrich | string | 
**max\_poll\_cycles** |  required  | The maximum amount of poll cycles to wait before erroring out | numeric | 
**sleep\_seconds** |  required  | The amount of seconds to sleep before trying to poll the endpoint again for results | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.ioc | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
action\_result\.status | string | 
action\_result\.data | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'hunt file'
Look for information about a file hash in the Intsights database

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**hash** |  required  | Hash of the binary to hunt | string |  `hash`  `sha256`  `sha1`  `md5` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.hash | string |  `hash`  `sha256`  `sha1`  `md5` 
action\_result\.data\.\*\.Value | string |  `hash`  `sha256`  `sha1`  `md5` 
action\_result\.data\.\*\.SourceName | string | 
action\_result\.data\.\*\.FirstSeen | string | 
action\_result\.data\.\*\.LastSeen | string | 
action\_result\.data\.\*\.Severity\.Value | string | 
action\_result\.data\.\*\.InvestigationLink | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'hunt domain'
Look for information about a domain in the Intsights database

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**domain** |  required  | Domain to hunt | string |  `domain` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.domain | string |  `domain` 
action\_result\.data\.\*\.Value | string |  `domain` 
action\_result\.data\.\*\.SourceName | string | 
action\_result\.data\.\*\.FirstSeen | string | 
action\_result\.data\.\*\.LastSeen | string | 
action\_result\.data\.\*\.Severity\.Value | string | 
action\_result\.data\.\*\.InvestigationLink | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'hunt ip'
Look for information about an IP in the Intsights database

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** |  required  | IP to hunt | string |  `ip` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.ip | string |  `ip` 
action\_result\.data\.\*\.Value | string |  `ip` 
action\_result\.data\.\*\.SourceName | string | 
action\_result\.data\.\*\.FirstSeen | string | 
action\_result\.data\.\*\.LastSeen | string | 
action\_result\.data\.\*\.Severity\.Value | string | 
action\_result\.data\.\*\.InvestigationLink | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'hunt url'
Look for information about a URL in the Intsights database

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**url** |  required  | URL to hunt | string |  `url` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.url | string |  `url` 
action\_result\.data\.\*\.Value | string |  `url` 
action\_result\.data\.\*\.SourceName | string | 
action\_result\.data\.\*\.FirstSeen | string | 
action\_result\.data\.\*\.LastSeen | string | 
action\_result\.data\.\*\.Severity\.Value | string | 
action\_result\.data\.\*\.InvestigationLink | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'on poll'
Callback action for the on\_poll ingest functionality

Type: **ingest**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**container\_id** |  optional  | Parameter ignored in this app | string | 
**start\_time** |  optional  | Start of time range, in epoch time \(milliseconds\)\. Default\: 10 days | numeric | 
**end\_time** |  optional  | End of time range, in epoch time \(milliseconds\)\. Default\: Now | numeric | 
**container\_count** |  optional  | Maximum number of containers to ingest | numeric | 
**artifact\_count** |  optional  | Parameter ignored in this app | numeric | 

#### Action Output
No Output  

## action: 'close alert'
Close an alert in the IntSights dashboard

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alert\_id** |  required  | IntSights alert ID to close | string |  `intsights alert id` 
**reason** |  required  | IntSights alert's closure reason | string | 
**free\_text** |  optional  | IntSights alert's comments | string | 
**rate** |  optional  | IntSights Alert's rate \(0\-5\) | numeric | 
**is\_hidden** |  optional  | Alert's hidden status \(Delete alert from the account instance \- only when reason is FalsePositive\) | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.rate | numeric | 
action\_result\.parameter\.free\_text | string | 
action\_result\.parameter\.reason | string | 
action\_result\.parameter\.is\_hidden | boolean | 
action\_result\.parameter\.alert\_id | string |  `intsights alert id` 
action\_result\.data | string | 
action\_result\.message | string | 
action\_result\.status | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'takedown request'
Initiate a takedown request of an alert from the IntSights dashboard

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alert\_id** |  required  | IntSights alert ID to takedown | string |  `intsights alert id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.alert\_id | string |  `intsights alert id` 
action\_result\.data | string | 
action\_result\.message | string | 
action\_result\.status | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 