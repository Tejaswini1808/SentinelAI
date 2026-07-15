"""Seed security knowledge base: MITRE ATT&CK techniques, OWASP Top 10, NIST CSF
functions, sample CVEs, SOC runbooks/policies, and synthetic past incidents.

This is illustrative content for the RAG demo, not an authoritative export of any
framework. MITRE technique IDs/names and the listed CVEs reflect real public data;
descriptions here are short paraphrases, and the runbooks/policies/incidents are
synthetic examples for a fictional org.
"""

_MITRE_ATTACK = [
    ("T1566", "Phishing", "Adversaries send fraudulent messages (email, links, attachments) to trick users into revealing credentials or running malicious code.", "Initial Access"),
    ("T1078", "Valid Accounts", "Adversaries use legitimate compromised credentials to gain and maintain access, blending in with normal activity.", "Persistence"),
    ("T1059", "Command and Scripting Interpreter", "Adversaries abuse command-line and scripting interpreters (PowerShell, bash, Python) to execute commands and payloads.", "Execution"),
    ("T1055", "Process Injection", "Adversaries inject code into the address space of a running process to evade detection and gain its privileges.", "Defense Evasion"),
    ("T1053", "Scheduled Task/Job", "Adversaries abuse task scheduling utilities (cron, Task Scheduler) to execute code at a set time or on a recurring basis.", "Execution"),
    ("T1071", "Application Layer Protocol", "Adversaries use common application protocols (HTTP, DNS, HTTPS) for command-and-control to blend with normal traffic.", "Command and Control"),
    ("T1021", "Remote Services", "Adversaries use valid credentials to log into remote services (RDP, SSH, SMB) for lateral movement.", "Lateral Movement"),
    ("T1003", "OS Credential Dumping", "Adversaries dump credentials from OS memory or storage (e.g. LSASS) to obtain account hashes or plaintext passwords.", "Credential Access"),
    ("T1486", "Data Encrypted for Impact", "Adversaries encrypt files on target systems, typically for ransomware extortion, to disrupt availability.", "Impact"),
    ("T1105", "Ingress Tool Transfer", "Adversaries transfer tools or files from an external system into the compromised environment.", "Command and Control"),
    ("T1490", "Inhibit System Recovery", "Adversaries delete or disable backups and recovery features to prevent restoration after an attack (common in ransomware).", "Impact"),
    ("T1027", "Obfuscated Files or Information", "Adversaries encode, encrypt, or otherwise obfuscate payloads and files to evade signature-based detection.", "Defense Evasion"),
    ("T1110", "Brute Force", "Adversaries systematically guess passwords or use credential lists to gain account access.", "Credential Access"),
    ("T1547", "Boot or Logon Autostart Execution", "Adversaries configure system settings so malicious code runs automatically on boot or logon.", "Persistence"),
    ("T1082", "System Information Discovery", "Adversaries gather OS, hardware, and configuration details to plan further actions.", "Discovery"),
    ("T1041", "Exfiltration Over C2 Channel", "Adversaries steal data by sending it over the same channel used for command-and-control.", "Exfiltration"),
    ("T1204", "User Execution", "Adversaries rely on a user to execute malicious code, e.g. opening an attachment or clicking a link.", "Execution"),
    ("T1595", "Active Scanning", "Adversaries scan victim infrastructure (ports, vulnerabilities) to gather information for targeting.", "Reconnaissance"),
    ("T1587", "Develop Capabilities", "Adversaries build custom malware, exploits, or tooling to use in operations.", "Resource Development"),
    ("T1098", "Account Manipulation", "Adversaries modify account permissions, credentials, or settings to maintain access.", "Persistence"),
    ("T1036", "Masquerading", "Adversaries rename or disguise malicious files/processes to look legitimate and evade detection.", "Defense Evasion"),
    ("T1046", "Network Service Discovery", "Adversaries enumerate services running on remote hosts to identify potential targets.", "Discovery"),
    ("T1057", "Process Discovery", "Adversaries enumerate running processes on a system to understand the environment.", "Discovery"),
    ("T1070", "Indicator Removal", "Adversaries delete or alter logs and artifacts to hide evidence of their activity.", "Defense Evasion"),
    ("T1074", "Data Staged", "Adversaries collect and stage data in a central location prior to exfiltration.", "Collection"),
    ("T1083", "File and Directory Discovery", "Adversaries enumerate files and directories to locate information of interest.", "Discovery"),
    ("T1087", "Account Discovery", "Adversaries enumerate local, domain, or cloud accounts to plan credential or lateral movement operations.", "Discovery"),
    ("T1090", "Proxy", "Adversaries route traffic through intermediate proxies to obscure the true source/destination of C2 traffic.", "Command and Control"),
    ("T1112", "Modify Registry", "Adversaries modify Windows Registry keys to hide configuration, achieve persistence, or disable defenses.", "Defense Evasion"),
    ("T1133", "External Remote Services", "Adversaries abuse externally facing remote access services (VPN, Citrix, RDP gateways) to gain initial or persistent access.", "Initial Access"),
    ("T1135", "Network Share Discovery", "Adversaries enumerate network shares to identify accessible data or lateral movement paths.", "Discovery"),
    ("T1189", "Drive-by Compromise", "Adversaries compromise systems when a user visits a website hosting malicious content, without further user interaction.", "Initial Access"),
    ("T1190", "Exploit Public-Facing Application", "Adversaries exploit vulnerabilities in internet-facing applications (web apps, APIs) to gain initial access.", "Initial Access"),
    ("T1195", "Supply Chain Compromise", "Adversaries compromise software, hardware, or update mechanisms upstream to affect downstream targets.", "Initial Access"),
    ("T1199", "Trusted Relationship", "Adversaries leverage access through a trusted third party (vendor, MSP) to compromise the intended target.", "Initial Access"),
    ("T1203", "Exploitation for Client Execution", "Adversaries exploit software vulnerabilities in client applications to execute code.", "Execution"),
    ("T1218", "System Binary Proxy Execution", "Adversaries abuse trusted, signed system binaries to execute malicious code and evade allowlisting.", "Defense Evasion"),
    ("T1484", "Domain or Tenant Policy Modification", "Adversaries modify domain or cloud tenant policies (GPOs, trust relationships) to enable further access or evade defenses.", "Defense Evasion"),
    ("T1489", "Service Stop", "Adversaries stop or disable services (backups, security tooling) to impact availability or evade detection.", "Impact"),
    ("T1498", "Network Denial of Service", "Adversaries flood network resources to degrade or deny availability to legitimate users.", "Impact"),
    ("T1531", "Account Access Removal", "Adversaries delete or lock accounts to deny access to legitimate users, often to disrupt response efforts.", "Impact"),
    ("T1552", "Unsecured Credentials", "Adversaries search for credentials stored insecurely in files, scripts, config, or command history.", "Credential Access"),
    ("T1555", "Credentials from Password Stores", "Adversaries extract credentials saved in password managers, browsers, or keychains.", "Credential Access"),
    ("T1562", "Impair Defenses", "Adversaries disable or tamper with security tools (EDR, logging, firewall rules) to evade detection.", "Defense Evasion"),
    ("T1567", "Exfiltration Over Web Service", "Adversaries exfiltrate data using legitimate web services (cloud storage, code repos) to blend in with normal traffic.", "Exfiltration"),
]

_FRAMEWORK_OVERVIEWS = [
    (
        "MITRE-ATTACK-OVERVIEW",
        "mitre_attack",
        "What is MITRE ATT&CK?",
        "MITRE ATT&CK is a globally-accessible knowledge base of adversary tactics and "
        "techniques based on real-world observations, maintained by MITRE. It organizes "
        "attacker behavior into Tactics (the attacker's goal, e.g. Initial Access, "
        "Execution, Persistence, Exfiltration, Impact) and Techniques (the specific way "
        "that goal is achieved, e.g. T1566 Phishing, T1059 Command and Scripting "
        "Interpreter). Security teams use ATT&CK for threat modeling, mapping detections "
        "and incidents to known adversary behavior, red-team/blue-team exercises, and "
        "identifying coverage gaps in defenses.",
    ),
    (
        "OWASP-TOP10-OVERVIEW",
        "owasp",
        "What is the OWASP Top 10?",
        "The OWASP Top 10 is a standard awareness document published by the Open Worldwide "
        "Application Security Project (OWASP) listing the most critical security risks to "
        "web applications, based on large-scale data analysis and industry survey. It's "
        "updated periodically (e.g. the 2021 edition) and used by development and security "
        "teams as a baseline for secure coding, security testing, and procurement "
        "requirements. Each entry (A01-A10) names a risk category, such as A03 Injection "
        "or A01 Broken Access Control, rather than a single specific vulnerability.",
    ),
    (
        "NIST-CSF-OVERVIEW",
        "nist",
        "What is the NIST Cybersecurity Framework (CSF)?",
        "The NIST Cybersecurity Framework (CSF) is a voluntary framework published by the "
        "U.S. National Institute of Standards and Technology to help organizations manage "
        "and reduce cybersecurity risk. It organizes activities into core Functions — "
        "Govern, Identify, Protect, Detect, Respond, and Recover — each broken into "
        "categories and subcategories of outcomes. Organizations use it to assess current "
        "security posture, set target states, and communicate risk to leadership, "
        "independent of any specific technology or vendor.",
    ),
]

_OWASP_TOP_10_2021 = [
    ("A01", "Broken Access Control", "Restrictions on what authenticated users can do are not properly enforced, allowing access to unauthorized data or functions."),
    ("A02", "Cryptographic Failures", "Sensitive data is exposed due to weak, missing, or misconfigured cryptography (e.g. weak algorithms, cleartext transmission)."),
    ("A03", "Injection", "Untrusted input is interpreted as code or commands (SQL, OS command, LDAP), allowing attackers to alter query/command logic."),
    ("A04", "Insecure Design", "Missing or ineffective security controls at the design stage, not fixable purely by implementation-level patches."),
    ("A05", "Security Misconfiguration", "Insecure default configs, verbose errors, unnecessary features enabled, or missing security hardening."),
    ("A06", "Vulnerable and Outdated Components", "Use of libraries, frameworks, or software with known vulnerabilities or that are no longer supported."),
    ("A07", "Identification and Authentication Failures", "Weaknesses in authentication (weak passwords, missing MFA, session fixation) allow account compromise."),
    ("A08", "Software and Data Integrity Failures", "Code and infrastructure that doesn't verify integrity, e.g. unsigned updates or insecure CI/CD pipelines, allowing tampering."),
    ("A09", "Security Logging and Monitoring Failures", "Insufficient logging, monitoring, and alerting delays or prevents detection and response to breaches."),
    ("A10", "Server-Side Request Forgery (SSRF)", "An application fetches a remote resource using a user-supplied URL without validating the destination, letting attackers reach internal systems."),
]

_NIST_CSF = [
    ("NIST-GOVERN", "NIST CSF: Govern", "Establish and monitor the organization's cybersecurity risk management strategy, expectations, and policy."),
    ("NIST-IDENTIFY", "NIST CSF: Identify", "Understand organizational assets, systems, data, and risks to manage cybersecurity risk to systems, people, and assets."),
    ("NIST-PROTECT", "NIST CSF: Protect", "Implement safeguards (access control, awareness training, data security) to manage and reduce risk."),
    ("NIST-DETECT", "NIST CSF: Detect", "Implement activities to identify the occurrence of a cybersecurity event in a timely manner."),
    ("NIST-RESPOND", "NIST CSF: Respond", "Take action regarding a detected cybersecurity incident to contain impact."),
    ("NIST-RECOVER", "NIST CSF: Recover", "Maintain plans for resilience and restore capabilities or services impaired by a cybersecurity incident."),
]

_CVES = [
    ("CVE-2021-44228", "Log4Shell (Apache Log4j2 RCE)", "A remote code execution vulnerability in Apache Log4j2's JNDI lookup handling, allowing unauthenticated RCE via crafted log messages. Critical severity, widely exploited in 2021-2022."),
    ("CVE-2017-0144", "EternalBlue (Microsoft SMBv1 RCE)", "A remote code execution vulnerability in Microsoft's SMBv1 protocol implementation, exploited by WannaCry and NotPetya for wormable lateral spread."),
    ("CVE-2014-0160", "Heartbleed (OpenSSL Information Disclosure)", "A buffer over-read in OpenSSL's heartbeat extension allowing attackers to read sensitive memory contents, including private keys and session data."),
    ("CVE-2023-4966", "Citrix Bleed (NetScaler ADC/Gateway)", "An information disclosure vulnerability in Citrix NetScaler ADC and Gateway allowing session token theft and session hijacking, exploited in the wild in 2023."),
    ("CVE-2021-34527", "PrintNightmare (Windows Print Spooler RCE)", "A remote code execution / privilege escalation vulnerability in the Windows Print Spooler service."),
]

_RUNBOOKS = [
    ("RB-PHISH-01", "SOC Runbook: Phishing Response", "1) Isolate reported message and recipients. 2) Extract indicators (sender, URLs, attachments) for enrichment. 3) Check for further delivery/clicks across mailboxes. 4) Reset credentials if links were clicked. 5) Block indicators at email gateway and proxy. 6) Notify affected users."),
    ("RB-RANSOM-01", "SOC Runbook: Ransomware Containment", "1) Isolate affected hosts from network immediately. 2) Identify patient-zero and initial access vector. 3) Preserve volatile evidence before shutdown. 4) Disable compromised accounts. 5) Assess backup integrity before any restore. 6) Engage incident commander and legal/comms per policy."),
    ("RB-CREDCOMP-01", "SOC Runbook: Credential Compromise", "1) Force password reset and revoke active sessions/tokens. 2) Enforce MFA if not already required. 3) Review account activity for anomalous logins or privilege changes. 4) Check for lateral use of the credential on other systems. 5) Determine root cause (phishing, stuffing, leak)."),
    ("POL-REMOTE-ACCESS", "Company Policy: Remote Access", "All remote access to internal systems requires MFA and a managed device. VPN sessions are logged and reviewed. Split-tunneling is disabled by default. Access requests follow least-privilege and require manager approval."),
    ("POL-LOG-RETENTION", "Company Policy: Security Log Retention", "Security-relevant logs (auth, network, endpoint, cloud audit) are retained for a minimum of 12 months hot/searchable and 5 years in cold storage, per compliance requirements."),
]

_PAST_INCIDENTS = [
    ("INC-2025-014", "Past Incident: Phishing-led Credential Compromise", "A user clicked a phishing link mimicking the SSO portal and entered credentials. The attacker used the stolen credentials for a valid-accounts login from an unfamiliar ASN, then attempted RDP lateral movement to two internal hosts before being contained. Root cause: no MFA enforced on the account. Remediation: org-wide MFA enforcement and phishing-resistant auth rollout."),
    ("INC-2025-031", "Past Incident: Ransomware via Exposed VPN Appliance", "An unpatched VPN appliance with a known RCE vulnerability was exploited for initial access. The attacker dumped credentials via OS credential dumping, moved laterally over SMB, disabled backup jobs, then deployed ransomware encrypting file shares. Remediation: patch management SLA tightened, backup isolation implemented, EDR deployed fleet-wide."),
    ("INC-2025-047", "Past Incident: Cloud Storage Misconfiguration Data Exposure", "A cloud storage bucket was misconfigured with public read access during a migration, exposing internal documents for approximately 9 days before detection via a routine external attack-surface scan. Remediation: automated cloud posture scanning added to CI/CD and quarterly access reviews."),
]


def build_knowledge_base() -> list[dict]:
    docs = []
    for doc_id, source_type, title, text in _FRAMEWORK_OVERVIEWS:
        docs.append({
            "doc_id": doc_id,
            "source_type": source_type,
            "title": title,
            "text": text,
            "tags": [doc_id, "framework_overview", source_type],
        })
    for tid, name, desc, tactic in _MITRE_ATTACK:
        docs.append({
            "doc_id": tid,
            "source_type": "mitre_attack",
            "title": f"{tid}: {name}",
            "text": f"{tid} ({name}) — Tactic: {tactic}. {desc}",
            "tags": [tid, name, tactic, "mitre_attack"],
        })
    for cid, name, desc in _OWASP_TOP_10_2021:
        docs.append({
            "doc_id": cid,
            "source_type": "owasp",
            "title": f"OWASP {cid}: {name}",
            "text": f"OWASP Top 10 (2021) {cid} — {name}. {desc}",
            "tags": [cid, name, "owasp_top_10"],
        })
    for cid, name, desc in _NIST_CSF:
        docs.append({
            "doc_id": cid,
            "source_type": "nist",
            "title": name,
            "text": f"{name}. {desc}",
            "tags": [cid, "nist_csf"],
        })
    for cve_id, name, desc in _CVES:
        docs.append({
            "doc_id": cve_id,
            "source_type": "cve",
            "title": f"{cve_id}: {name}",
            "text": f"{cve_id} ({name}). {desc}",
            "tags": [cve_id, name, "cve"],
        })
    for rid, name, desc in _RUNBOOKS:
        docs.append({
            "doc_id": rid,
            "source_type": "runbook",
            "title": name,
            "text": f"{name}. {desc}",
            "tags": [rid, "runbook_or_policy"],
        })
    for iid, name, desc in _PAST_INCIDENTS:
        docs.append({
            "doc_id": iid,
            "source_type": "past_incident",
            "title": name,
            "text": f"{name}. {desc}",
            "tags": [iid, "past_incident"],
        })
    return docs
