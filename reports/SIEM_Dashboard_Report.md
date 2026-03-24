**CUSTOM SIEM DASHBOARD**

**DESIGN & IMPLEMENTATION**

ELK Stack Security Operations Center Lab Report

Prepared by:

**Pranmoy Patar**

March 2025

  ----------------------------------- -----------------------------------
  **Platform**                        ELK Stack 8.11.0 + Filebeat

  **Environment**                     Kali Linux + Docker Compose

  **Visualizations**                  7 panels across 3 attack types

  **Export**                          PDF via Kibana Reporting
  ----------------------------------- -----------------------------------

# 1. Objective & Overview

This report documents the design and implementation of a custom Security
Information and Event Management (SIEM) dashboard built on top of an ELK
Stack (Elasticsearch, Logstash, Kibana) deployment. The dashboard was
designed to visualize critical security events --- specifically
brute-force credential attacks, DNS-based data exfiltration, and
PowerShell-based exploitation --- in real time using data ingested from
Python-driven attack simulations.

This lab builds directly on a prior ELK Stack deployment lab in which
the stack was set up via Docker Compose on a Kali Linux VM, Filebeat was
configured to ship logs from three attack simulation scripts, and the
foundational data pipeline was validated. This report focuses
specifically on the dashboard layer --- the design decisions,
visualization implementations, technical challenges encountered, and
outcomes achieved.

The primary objectives of this phase were:

-   Design a multi-panel Kibana dashboard that provides a SOC analyst
    view of security events across three distinct attack categories

-   Implement runtime fields to extract structured attributes from raw
    log messages for richer querying and visualization

-   Build seven visualizations covering event volume, attacker
    identification, anomaly detection, and technique classification

-   Add contextual Markdown documentation panels to the dashboard for
    stakeholder readability

-   Export the completed dashboard as a PDF for portfolio documentation

-   Resolve infrastructure issues encountered during implementation
    including encryption key configuration and Docker data persistence

# 2. Environment & Infrastructure

## 2.1 System Configuration

  ------------------------ ----------------------------------------------
  **Component**            **Details**

  **Operating System**     Kali Linux (single VM)

  **Containerization**     Docker + Docker Compose

  **ELK Stack Version**    8.11.0 (Elasticsearch, Logstash, Kibana)

  **Log Shipper**          Filebeat (installed on VM host, not in Docker)

  **Elasticsearch Port**   9200

  **Kibana Port**          5601

  **Logstash Beats Port**  5044

  **docker-compose.yml     /home/elk-lab/docker-compose.yml
  path**                   
  ------------------------ ----------------------------------------------

## 2.2 Docker Compose Configuration

The final docker-compose.yml used in this lab includes persistent named
volumes for both Elasticsearch and Kibana, and Kibana encryption keys
required for the alerting and reporting subsystems. These additions were
made during the lab to resolve data loss and functionality issues
(detailed in Section 5).

version: \'3\'

services:

elasticsearch:

image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0

container_name: elasticsearch

environment:

\- discovery.type=single-node

\- xpack.security.enabled=false

ports:

\- \"9200:9200\"

mem_limit: 2g

volumes:

\- esdata:/usr/share/elasticsearch/data

logstash:

image: docker.elastic.co/logstash/logstash:8.11.0

container_name: logstash

ports:

\- \"5044:5044\"

kibana:

image: docker.elastic.co/kibana/kibana:8.11.0

container_name: kibana

environment:

\- ELASTICSEARCH_HOSTS=http://elasticsearch:9200

\-
xpack.encryptedSavedObjects.encryptionKey=a3f21b8c9e4d7a2f1c3b9e4d8c2a1f3b

\- xpack.alerting.encryptionKey=a3f21b8c9e4d7a2f1c3b9e4d8c2a1f3b

\- xpack.reporting.encryptionKey=a3f21b8c9e4d7a2f1c3b9e4d8c2a1f3b

ports:

\- \"5601:5601\"

depends_on:

\- elasticsearch

volumes:

\- kibanaData:/usr/share/kibana/data

volumes:

esdata:

driver: local

kibanaData:

driver: local

## 2.3 Data Pipeline

The full data flow from log generation to dashboard visualization
followed this pipeline:

**Python Scripts → /var/log/attack-simulation/ → Filebeat → Logstash
:5044 → Elasticsearch :9200 → Kibana :5601**

-   Three Python simulation scripts wrote attack logs to
    /var/log/attack-simulation/ in syslog, BIND DNS, and Sysmon-style
    formats respectively

-   Filebeat monitored these paths with dedicated inputs, enriching each
    event with log_type and tags fields before shipping to Logstash on
    localhost:5044

-   Logstash forwarded parsed events to Elasticsearch where they were
    indexed under filebeat-8.11.0-\*

-   Kibana queried Elasticsearch via the filebeat-\* Data View,
    providing the visualization and dashboard layer

# 3. Dashboard Design

## 3.1 Design Philosophy

The dashboard was designed to replicate a real-world SOC analyst
monitoring view. The guiding design principles were:

-   Separation by attack type --- each threat category occupies its own
    clearly labelled section so an analyst can immediately isolate an
    investigation area

-   Progressive detail --- the top row provides high-level event counts
    (KPI metrics), with deeper analytical charts below

-   Signal vs noise --- each visualization was built to include both
    malicious and legitimate traffic so the detection value of each
    chart is evident in context

-   Self-documenting --- Markdown panels were added throughout to
    describe each section, its detection logic, and the attack
    indicators being visualized, making the dashboard readable by
    non-technical stakeholders

## 3.2 Dashboard Layout

  ----------------------- ----------- ------------ -----------------------
  **Dashboard Header ---                           
  Markdown Panel (full                             
  width)**                                         

  Metric: Auth Events     Metric: DNS              Metric: PS Events
                          Events                   

  Brute Force --- Failed                           
  Login Timeline (full                             
  width)                                           

  Top Attacker IPs                    DNS Query    
                                      Volume       

  DNS Query Length                    PowerShell   
  Distribution                        Severity     
                                      Donut        

  PowerShell Attack                                
  Technique Tags (full                             
  width)                                           
  ----------------------- ----------- ------------ -----------------------

# 4. Visualizations --- Implementation Detail

## 4.1 Metric KPI Cards (3 panels)

Three Metric-type visualizations were placed at the top of the dashboard
as a high-level event count summary. Each metric card used a simple
Count aggregation filtered by log_type to give an at-a-glance view of
total events ingested per attack category.

  ----------------------- ----------------------- -----------------------
  **Panel**               **KQL Filter**          **Count**

  Auth Events             log_type:               1208
                          \"authentication\"      

  DNS Events              log_type: \"dns\"       1770

  PowerShell Events       log_type:               730
                          \"powershell\"          
  ----------------------- ----------------------- -----------------------

## 4.2 Brute Force --- Failed Login Timeline

Chart type: Bar vertical (stacked). This visualization plots the volume
of failed SSH authentication events over time, making the burst pattern
of a credential stuffing attack clearly visible as a spike against the
flat baseline of legitimate traffic.

-   **\@timestamp with Auto interval:** Horizontal axis

-   **Count of records:** Vertical axis

-   **log_type: \"authentication\" AND message: \"Failed password\":**
    KQL filter

-   **A sharp spike of \~50 failed login events clustered within the
    simulation window, visually distinct from the sparse legitimate
    failure rate:** Visual outcome

  -----------------------------------------------------------------------
  *Detection insight: A real SOC rule would trigger on \>10 failed logins
  from a single IP within 60 seconds. The timeline makes this threshold
  intuitive --- the attacker\'s burst is unmistakable.*

  -----------------------------------------------------------------------

## 4.3 Top Attacker IPs

Chart type: Bar horizontal. This visualization required creating a
runtime field to extract the source IP address from the raw
syslog-format message string, since Filebeat was not configured with a
Grok parser to do this at ingest time.

**Runtime Field --- source_ip**

// Stack Management → Data Views → filebeat-\* → Add field

// Name: source_ip \| Type: Keyword

if (doc\[\'message.keyword\'\].size() \> 0) {

def m =
/(\\d+\\.\\d+\\.\\d+\\.\\d+)/.matcher(doc\[\'message.keyword\'\].value);

if (m.find()) emit(m.group(1));

}

-   **Count of records:** Horizontal axis

-   **Top 10 values of source_ip:** Vertical axis

-   **log_type: \"authentication\" AND message: \"Failed password\":**
    KQL filter

-   **The three attacker IPs (203.0.113.100, 198.51.100.50, 192.0.2.200)
    dominated the chart, each with significantly higher counts than any
    legitimate source IP:** Visual outcome

## 4.4 DNS Tunneling --- Query Volume Over Time

Chart type: Line (dual layer). This visualization contrasts malicious
DNS tunnel queries against legitimate DNS traffic on the same timeline.
Rather than using the Filebeat tags field (which only carries metadata,
not content labels), two separate Lens layers were used with KQL
filters:

-   **log_type: \"dns\" AND message: \"malicious-c2.example.com\" ---
    labelled Malicious C2 Traffic:** Layer 1 (Malicious)

-   **log_type: \"dns\" AND NOT message: \"malicious-c2.example.com\"
    --- labelled Legitimate DNS:** Layer 2 (Legitimate)

-   **The malicious layer showed a consistently high and steady query
    rate (automated beaconing pattern) while legitimate traffic appeared
    sporadic and low-volume --- a clear visual contrast:** Visual
    outcome

  -----------------------------------------------------------------------
  *Note: An earlier approach attempted to break down by the Filebeat tags
  field. This was corrected --- tags only contains static metadata labels
  set in filebeat.yml (e.g. \'dns\', \'kali-client\') and cannot
  distinguish malicious from legitimate events within the same log
  stream. The dual-layer KQL approach is the correct method.*

  -----------------------------------------------------------------------

## 4.5 DNS Query Length Distribution

Chart type: Bar vertical. DNS tunneling encodes data into subdomain
labels, producing abnormally long query names. This visualization
exposes that anomaly by plotting query name length as a distribution. A
runtime field was created to extract and measure the query name from the
BIND-format log message:

**Runtime Field --- dns_query_length**

// Name: dns_query_length \| Type: Long

if (doc\[\'message.keyword\'\].size() \> 0) {

def m = /\\((\[\^)\]+)\\):
query:/.matcher(doc\[\'message.keyword\'\].value);

if (m.find()) emit(m.group(1).length());

}

-   **dns_query_length with interval of 10:** Horizontal axis

-   **Count of records:** Vertical axis

-   **log_type: \"dns\":** KQL filter

-   **A clear bimodal distribution --- legitimate queries clustering at
    10--25 characters, tunneling queries at 60--90 characters. The two
    populations are visually non-overlapping, making this a
    high-confidence detection signal:** Visual outcome

## 4.6 PowerShell Exploitation --- Severity Donut

Chart type: Donut. This visualization breaks down PowerShell events by
severity classification (critical, high, medium, info) to help an
analyst immediately understand the risk distribution of observed events.
A runtime field extracts the severity label from the Sysmon-style log
format:

**Runtime Field --- ps_severity**

// Name: ps_severity \| Type: Keyword

if (doc\[\'message.keyword\'\].size() \> 0) {

def m = /Severity:(\\w+)/.matcher(doc\[\'message.keyword\'\].value);

if (m.find()) emit(m.group(1));

}

-   **Top values of ps_severity:** Slice by

-   **Count of records:** Size by

-   **log_type: \"powershell\":** KQL filter

-   **Critical and high severity events dominated the donut (reflecting
    the simulation\'s 8 malicious command patterns), with a smaller info
    slice from the 10 legitimate baseline events:** Visual outcome

## 4.7 PowerShell --- Attack Technique Tags

Chart type: Treemap. This visualization categorizes PowerShell events by
their attack technique tags (e.g. encoded_command, credential_theft,
amsi_bypass, defense_evasion, lateral_movement) giving an analyst an
immediate picture of which techniques were employed. A runtime field
extracts the Tags value from each log entry:

**Runtime Field --- ps_tags**

// Name: ps_tags \| Type: Keyword

if (doc\[\'message.keyword\'\].size() \> 0) {

def m = /Tags:(\[\\w,\_\]+)/.matcher(doc\[\'message.keyword\'\].value);

if (m.find()) emit(m.group(1));

}

-   **Top 10 values of ps_tags:** Group by

-   **Count of records:** Metric

-   **log_type: \"powershell\":** KQL filter

-   **The treemap rendered technique blocks proportional to their
    frequency, with encoded_command and execution_policy_bypass
    appearing as the largest tiles, consistent with the simulation\'s
    command distribution:** Visual outcome

## 4.8 Markdown Documentation Panels

Six Markdown text panels were added to the dashboard to provide section
headers, attack descriptions, detection logic summaries, and a footer
note. These panels serve two purposes: they make the dashboard
self-explanatory for non-technical stakeholders, and they demonstrate
documentation discipline valued in professional SOC environments.

Panels added:

-   Dashboard Header --- title, author, environment summary,
    auto-refresh note

-   KPI Row Label --- describes the three metric cards

-   Brute Force Section --- attack description and detection threshold

-   DNS Tunneling Section --- attack description and C2 domain reference

-   PowerShell Section --- attack description and key indicator list

-   Footer --- lab disclaimer and RFC 5737 TEST-NET IP range note

# 5. Challenges & Troubleshooting

## 5.1 Encryption Key Not Configured (Alerting Blocked)

  -----------------------------------------------------------------------
  *Error: \"You must configure an encryption key to use Alerting\" ---
  Stack Management → Rules*

  -----------------------------------------------------------------------

When navigating to Stack Management → Rules to set up detection alerts,
Kibana displayed a blocking error requiring an encryption key. This is
because Kibana\'s alerting, saved objects, and reporting subsystems all
require an xpack.encryptedSavedObjects.encryptionKey to be set --- a
requirement that is not obvious in minimal Docker setups.

Root cause: The original docker-compose.yml had no Kibana environment
variables configured beyond ELASTICSEARCH_HOSTS. Kibana defaults to no
encryption key, which disables alerting functionality entirely.

**Resolution**

-   Added three xpack encryption key environment variables to the Kibana
    service in docker-compose.yml (encryptedSavedObjects, alerting, and
    reporting keys)

-   Used a 32-character hex string as the key value

-   Restarted the stack with docker-compose down && docker-compose up -d

-   Note: A curl-based trial license activation attempt
    (/\_license/start_trial) also failed as this endpoint is not
    available on the Basic license tier --- the fix was the encryption
    key, not the license

## 5.2 Dashboard Data Loss After Restart

After bringing the stack down to add the encryption key, all Kibana
dashboards, saved visualizations, Data Views, and settings (including
dark mode) were lost. The Elasticsearch index data was also gone,
meaning the simulations had to be re-run.

Root cause: The original docker-compose.yml had no volume mounts. Docker
containers store data inside the container filesystem by default ---
when a container is removed (docker-compose down), all data is
permanently deleted. This is a fundamental Docker persistence gotcha.

**Resolution**

-   Added named volume mounts for both Elasticsearch
    (esdata:/usr/share/elasticsearch/data) and Kibana
    (kibanaData:/usr/share/kibana/data) to docker-compose.yml

-   Used camelCase volume names (esdata, kibanaData) ---
    underscore-based names caused a validation error in this environment

-   Declared the volumes block at the bottom of docker-compose.yml so
    Docker creates and manages them as named volumes that persist across
    container restarts

-   Restored to a previously taken VM snapshot to recover the working
    dashboard state, then applied the volume configuration going forward

  -----------------------------------------------------------------------
  *Key lesson: Always configure Docker named volumes before running any
  stateful service. For ELK in particular, both Elasticsearch data and
  Kibana saved objects must be persisted separately.*

  -----------------------------------------------------------------------

## 5.3 DNS Visualization --- Incorrect Field Used for Breakdown

An initial attempt to break down the DNS Query Volume chart by attack
type used the Filebeat tags field. This produced incorrect results ---
the tags field contains static metadata labels set in filebeat.yml (e.g.
\[\"dns\", \"kali-client\"\]) and is identical for every DNS log entry
regardless of whether it is malicious or legitimate.

**Resolution**

-   Replaced the tags field breakdown with a dual-layer Lens approach

-   Layer 1 filtered on message: \"malicious-c2.example.com\" to isolate
    tunnel queries

-   Layer 2 used NOT message: \"malicious-c2.example.com\" to show
    legitimate traffic

-   This approach correctly contrasts the two traffic types based on
    actual log content rather than metadata

## 5.4 Alerting --- Skipped

Detection rule creation via Stack Management → Rules was identified as a
stretch goal. After resolving the encryption key issue (which unblocked
the Rules UI), the decision was made to focus on completing the full set
of dashboard visualizations and the PDF export within the available lab
time. Alerting rule configuration is documented as a future extension of
this lab.

# 6. Results & Findings

## 6.1 Dashboard Summary

  ---------------------- ------------------ ------------------ ------------
  **Visualization**      **Type**           **Attack           **Status**
                                            Category**         

  Metric KPI Cards (×3)  Metric             All                ✓ Complete

  Failed Login Timeline  Bar (vertical)     Credential         ✓ Complete
                                            Stuffing           

  Top Attacker IPs       Bar (horizontal)   Credential         ✓ Complete
                                            Stuffing           

  DNS Query Volume       Line (dual layer)  DNS Tunneling      ✓ Complete

  DNS Query Length Dist. Bar (vertical)     DNS Tunneling      ✓ Complete

  PS Severity Donut      Donut              PowerShell         ✓ Complete
                                            Exploitation       

  PS Attack Technique    Treemap            PowerShell         ✓ Complete
  Tags                                      Exploitation       

  Markdown Panels (×6)   Text/Markdown      All                ✓ Complete

  Detection Alert Rules  Threshold Rule     All                --- Skipped
  ---------------------- ------------------ ------------------ ------------

## 6.2 Key Detection Findings

Each visualization demonstrated clear, visually distinct detection
signals for its respective attack type:

**Credential Stuffing**

The failed login timeline showed an unmistakable burst pattern ---
approximately 50 failed events clustered within a 5-minute window from a
single IP, followed by silence, then sparse legitimate traffic. The Top
Attacker IPs chart confirmed all failures originated from TEST-NET
attacker IPs with zero legitimate failures from those sources. The
attack was trivially distinguishable from baseline traffic.

**DNS Tunneling**

The dual-layer DNS query volume chart showed a sustained, automated
querying pattern to malicious-c2.example.com at a consistent rate ---
characteristic of C2 beaconing --- against irregular, low-volume
legitimate DNS traffic. The query length distribution was the most
visually striking chart: two completely non-overlapping populations
(legitimate at 10--25 characters, tunneling at 60--90 characters) making
this a near-zero false-positive detection signal.

**PowerShell Exploitation**

The severity donut immediately communicated the risk landscape ---
critical and high events dominated, with info events from legitimate
PowerShell usage forming a small slice. The attack technique treemap
provided MITRE ATT&CK-style technique visibility, showing
encoded_command and execution_policy_bypass as the most frequent
techniques, which aligns with real-world PowerShell attack patterns.

## 6.3 PDF Export

The completed dashboard was successfully exported as a PDF using
Kibana\'s built-in Reporting feature (Stack Management → Reporting). The
export used Preserve Layout mode with the browser zoom set to 75% to
maximize panel visibility per page. The PDF produced a professional
multi-page document suitable for direct inclusion in a portfolio or
stakeholder report.


  -----------------------------------------------------------------------
  *The PDF export feature required the xpack.reporting.encryptionKey to
  be set --- this was resolved as part of the encryption key fix in
  Section 5.1. Without that key, the Reporting menu is available but
  export jobs fail silently.*

  -----------------------------------------------------------------------

# 7. Conclusion & Future Work

## 7.1 Conclusion

This lab successfully delivered a functional, multi-panel SIEM dashboard
on an ELK Stack 8.11.0 deployment that visualizes three distinct
cyberattack categories in near real-time. All seven planned
visualizations were implemented, runtime fields were used to enrich raw
log data without requiring Logstash Grok pipelines, and the dashboard
was documented with Markdown panels and exported as a professional PDF.

The lab demonstrated several important real-world skills beyond the
dashboard itself --- troubleshooting Docker data persistence,
configuring Kibana security subsystems, correcting field selection
errors in Kibana Lens, and using VM snapshots as a recovery mechanism.
These problem-solving experiences are as valuable as the technical
outcomes.

The completed dashboard serves as a practical demonstration of core blue
team and SOC analyst competencies: SIEM operation, log management,
threat detection visualization, and security event documentation.

## 7.2 Future Extensions

-   Implement detection alert rules for all three attack types using the
    now-functional Kibana Alerting engine (threshold rules for brute
    force, DNS query frequency, and PowerShell severity)

-   Add a Logstash Grok pipeline to parse structured fields (source_ip,
    dns_query_name, ps_severity) at ingest time --- eliminating the need
    for runtime fields and improving query performance at scale

-   Extend the dashboard with a GeoIP map visualization to plot attacker
    source IPs geographically using Elasticsearch\'s GeoIP enrichment
    processor

-   Add a MITRE ATT&CK technique mapping panel linking PowerShell
    technique tags to their corresponding ATT&CK technique IDs (e.g.
    T1059.001 for PowerShell, T1071.004 for DNS tunneling)

-   Integrate Elastic Security (formerly SIEM app) for a dedicated
    security workflow with case management and timeline investigation
    features

-   Configure email or Slack connector-based alert notifications once a
    connector is set up in Stack Management → Connectors

*Pranmoy Patar \| Custom SIEM Dashboard --- ELK Stack Lab \| Personal
Portfolio \| March 2025*
