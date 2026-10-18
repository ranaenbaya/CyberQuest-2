from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import bcrypt
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import wraps
from datetime import datetime, timezone

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY'),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

if not app.config['SECRET_KEY']:
    raise RuntimeError('Set the SECRET_KEY environment variable before starting CyberQuest.')

# ─── Database ────────────────────────────────────────────────────────────────

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('Set the DATABASE_URL environment variable before starting CyberQuest.')

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    """Create tables if they don't exist — runs automatically on startup."""
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            stage_id TEXT NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            score INTEGER DEFAULT 0,
            completed_at TIMESTAMPTZ,
            UNIQUE(user_id, stage_id)
        );
            """)
        db.commit()
    finally:
        db.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

# ─── Stage Content ───────────────────────────────────────────────────────────

STAGES = [
    # ── HACKING STAGES ──────────────────────────────────────────────────────
    {
        "id": "hack_1",
        "type": "hacking",
        "title": "Reconnaissance",
        "subtitle": "Think Like an Attacker",
        "description": "Master the art of information gathering",
        "order": 1,
        "slides": [
            {
                "title": "What is Reconnaissance?",
                "content": "Reconnaissance is the very first phase of a cyber attack — and arguably the most important. Before any hacker touches a system, they spend time gathering as much information as possible about the target.\n\nThink of it like a burglar casing a house before breaking in. They study the layout, note the entry points, and identify weaknesses. In cyber security, this phase is called 'recon'.\n\nThe more information an attacker has, the more targeted and effective their attack will be. This is why understanding recon is critical — both for attackers and defenders.",
                "icon": "🔍"
            },
            {
                "title": "Passive vs Active Recon",
                "content": "There are two types of reconnaissance:\n\n🔵 PASSIVE RECON — Gathering information without directly interacting with the target. This includes searching public records, social media, company websites, and news articles. The target has no idea you're looking.\n\n🔴 ACTIVE RECON — Directly interacting with the target's systems, such as pinging their servers or scanning their ports. This leaves traces and can trigger security alerts.\n\nPassive recon is always safer for the attacker and harder for defenders to detect. Most professional attackers spend the majority of their time here.",
                "icon": "👁️"
            },
            {
                "title": "OSINT: Open Source Intelligence",
                "content": "OSINT stands for Open Source Intelligence — using publicly available information to build a profile of a target.\n\nCommon OSINT sources include:\n• Company websites — job listings reveal tech stacks\n• LinkedIn — employee names, roles, software used\n• GitHub — leaked code, API keys, internal structure\n• WHOIS — domain registration details\n• Shodan — internet-connected device search engine\n• Google — the most powerful OSINT tool of all\n\nA skilled attacker can build a detailed picture of an organisation purely from public information — no hacking required at this stage.",
                "icon": "🌐"
            },
            {
                "title": "Google Dorking",
                "content": "Google Dorking uses advanced search operators to find sensitive information indexed by Google.\n\nExamples:\n• site:example.com filetype:pdf — finds PDF files\n• intitle:'index of' passwords — finds exposed directories\n• inurl:admin — finds admin login pages\n\nThis technique can uncover:\n• Exposed login portals\n• Sensitive documents accidentally made public\n• Misconfigured servers\n• Email addresses and usernames\n\nGoogle Dorking is entirely passive — you're only using Google's index. However, using this information to gain unauthorised access is illegal.",
                "icon": "🔎"
            },
            {
                "title": "Tools Used in Recon",
                "content": "Professionals use specialised tools to speed up reconnaissance:\n\n🛠️ Maltego — Visual link analysis and data mining\n🛠️ theHarvester — Email and subdomain harvesting\n🛠️ Shodan — Scanning internet-exposed devices\n🛠️ Recon-ng — Full-featured recon framework\n🛠️ Nmap — Network discovery (active recon)\n🛠️ WHOIS — Domain and IP registration lookup\n\nThese tools are used by both ethical hackers (pen testers) and malicious attackers. The difference lies entirely in whether you have permission to test the target.",
                "icon": "🛠️"
            },
            {
                "title": "Ethics & Legal Boundaries",
                "content": "⚖️ IMPORTANT — This is where ethics begin.\n\nReconnaissance against a target you do NOT have permission to attack is illegal under the Computer Misuse Act 1990 (UK) and equivalent laws worldwide.\n\nEven passive recon can cross ethical lines if the intent is to cause harm. Ethical hackers (penetration testers) always work under a signed contract defining what they can and cannot do.\n\nThe skills you're learning here are for:\n✅ Authorised penetration testing\n✅ CTF (Capture the Flag) competitions\n✅ Defending your own systems\n✅ Understanding threats to better protect against them\n\nNEVER use these techniques against systems you don't own or have explicit permission to test.",
                "icon": "⚖️"
            }
        ],
        "quiz": [
            {
                "question": "What is the PRIMARY goal of the reconnaissance phase?",
                "options": {"A": "Immediately exploit vulnerabilities", "B": "Gather information about the target", "C": "Install malware on the target", "D": "Crash the target's servers"},
                "correct": "B",
                "explanation": "Reconnaissance is about gathering intelligence before any attack. The more you know about a target, the more effective a later attack can be."
            },
            {
                "question": "Which type of reconnaissance does NOT directly interact with the target system?",
                "options": {"A": "Active reconnaissance", "B": "Port scanning", "C": "Passive reconnaissance", "D": "Network probing"},
                "correct": "C",
                "explanation": "Passive recon gathers information without touching the target — using public sources, social media, and search engines only."
            },
            {
                "question": "What does OSINT stand for?",
                "options": {"A": "Online System Intelligence Network Tool", "B": "Open Source Intelligence", "C": "Offensive Security Intelligence Test", "D": "Operational System Intrusion Technique"},
                "correct": "B",
                "explanation": "OSINT = Open Source Intelligence. It refers to gathering information from publicly available sources."
            },
            {
                "question": "A penetration tester finds a company's admin login portal using Google search operators. What is this technique called?",
                "options": {"A": "SQL Injection", "B": "Phishing", "C": "Google Dorking", "D": "Brute Force"},
                "correct": "C",
                "explanation": "Google Dorking uses advanced search operators to find sensitive information indexed by Google, such as exposed admin portals."
            },
            {
                "question": "Under UK law, performing reconnaissance against a system WITHOUT permission is:",
                "options": {"A": "Legal if you don't cause damage", "B": "Only illegal if you access the system", "C": "Illegal under the Computer Misuse Act 1990", "D": "Legal as long as it's passive"},
                "correct": "C",
                "explanation": "The Computer Misuse Act 1990 covers unauthorised access to systems. Even reconnaissance with intent to attack can be prosecuted."
            }
        ]
    },
    {
        "id": "hack_2",
        "type": "hacking",
        "title": "Phishing Attacks",
        "subtitle": "The Human Vulnerability",
        "description": "Understand how attackers exploit human psychology",
        "order": 2,
        "slides": [
            {
                "title": "What is Phishing?",
                "content": "Phishing is a social engineering attack where an attacker impersonates a trusted entity to trick victims into revealing sensitive information — passwords, credit card numbers, or personal data.\n\nThe term comes from 'fishing' — casting a wide net and waiting for someone to take the bait.\n\nPhishing is the NUMBER ONE cause of data breaches worldwide. No matter how strong your technical security is, a single employee clicking a malicious link can compromise an entire organisation.\n\nThis is why understanding phishing — both how it works and how to spot it — is one of the most important cyber security skills you can learn.",
                "icon": "🎣"
            },
            {
                "title": "Types of Phishing",
                "content": "Phishing comes in many forms:\n\n📧 EMAIL PHISHING — Mass emails pretending to be banks, services, or IT departments. The most common type.\n\n🎯 SPEAR PHISHING — Targeted attacks against a specific person or organisation, using personal details to appear legitimate.\n\n🐋 WHALING — Spear phishing targeting senior executives (CEOs, CFOs) — 'big fish'.\n\n📱 SMISHING — Phishing via SMS text messages.\n\n📞 VISHING — Voice phishing via phone calls, often impersonating banks or government agencies.\n\n🌐 PHARMING — Redirecting users to fake websites without them clicking any link.",
                "icon": "📧"
            },
            {
                "title": "Anatomy of a Phishing Email",
                "content": "A typical phishing email contains several deceptive elements:\n\n🔴 Spoofed sender — 'security@paypa1.com' instead of 'paypal.com'\n🔴 Urgency — 'Your account will be suspended in 24 hours!'\n🔴 Fear — 'Suspicious login detected on your account'\n🔴 Malicious links — URLs that look legitimate but redirect to fake sites\n🔴 Malicious attachments — PDFs or Word docs containing malware\n🔴 Poor grammar — Though modern AI has made phishing emails far more convincing\n\nAttackers use email spoofing tools and domain typosquatting (registering similar domains) to make their messages appear genuine.",
                "icon": "✉️"
            },
            {
                "title": "How Spear Phishing Works",
                "content": "Unlike mass phishing, spear phishing is highly targeted and researched.\n\nAn attacker targeting a company employee might:\n1. Find their name and role on LinkedIn\n2. Identify their manager's name\n3. Find colleagues' email formats\n4. Send an email appearing to be from their manager asking for urgent bank details\n\nThis is why OSINT (Stage 1) directly feeds into phishing attacks. The information gathered during reconnaissance enables highly convincing phishing.\n\n95% of successful cyber attacks begin with a spear phishing email. Real-world breaches of major companies have started exactly this way.",
                "icon": "🎯"
            },
            {
                "title": "Creating a Phishing Simulation (Ethically)",
                "content": "Ethical hackers test organisations by running authorised phishing simulations.\n\nTools used include:\n🛠️ GoPhish — Open source phishing simulation framework\n🛠️ SET (Social Engineering Toolkit) — Comprehensive phishing toolkit\n🛠️ King Phisher — Campaign management and reporting\n\nAn authorised phishing test involves:\n• Written permission from the organisation\n• Defined scope (which employees can be targeted)\n• Clear reporting of results\n• Follow-up training for employees who clicked\n\nWithout authorisation, sending phishing emails is a criminal offence under the Fraud Act 2006 and Computer Misuse Act 1990.",
                "icon": "🛠️"
            },
            {
                "title": "Ethics & Legal Warning",
                "content": "⚖️ Phishing is one of the most harmful cyber attacks because it targets PEOPLE, not just systems.\n\nVictims of phishing can lose:\n• Their life savings\n• Their job (if corporate credentials are stolen)\n• Their personal identity\n• Years of emotional distress\n\nUsing these techniques without authorisation is:\n❌ Illegal under the Fraud Act 2006\n❌ Illegal under the Computer Misuse Act 1990\n❌ Potentially a breach of GDPR\n❌ Punishable by up to 10 years imprisonment\n\nEthical use means: authorised testing, security awareness training, and educating others to recognise and report phishing attempts.",
                "icon": "⚖️"
            }
        ],
        "quiz": [
            {
                "question": "What makes SPEAR phishing different from regular phishing?",
                "options": {"A": "It uses phone calls instead of emails", "B": "It targets a specific individual using personal information", "C": "It only targets financial institutions", "D": "It uses malware attachments exclusively"},
                "correct": "B",
                "explanation": "Spear phishing is targeted and researched — attackers gather personal details about the victim to make the attack more convincing."
            },
            {
                "question": "An attacker sends a text message pretending to be your bank, asking you to verify your account. What type of attack is this?",
                "options": {"A": "Vishing", "B": "Whaling", "C": "Smishing", "D": "Pharming"},
                "correct": "C",
                "explanation": "Smishing = SMS phishing. Phishing attacks delivered via text message are called smishing."
            },
            {
                "question": "Which of these is a RED FLAG in a phishing email?",
                "options": {"A": "Comes from a known colleague", "B": "Contains no attachments", "C": "Uses urgency: 'Act within 24 hours or your account is deleted'", "D": "Has a professional company logo"},
                "correct": "C",
                "explanation": "Urgency is a key manipulation tactic in phishing. Attackers create pressure so victims act before thinking critically."
            },
            {
                "question": "What is 'whaling'?",
                "options": {"A": "Phishing attacks on maritime companies", "B": "Targeted phishing against senior executives", "C": "Mass phishing targeting millions of people", "D": "Phishing using fake websites"},
                "correct": "B",
                "explanation": "Whaling targets 'big fish' — senior executives like CEOs and CFOs who have access to highly sensitive data and systems."
            },
            {
                "question": "Under which UK law is sending unauthorised phishing emails primarily prosecuted?",
                "options": {"A": "The Data Protection Act 2018", "B": "The Copyright Act 1988", "C": "The Fraud Act 2006", "D": "The Terrorism Act 2000"},
                "correct": "C",
                "explanation": "Phishing (obtaining information by deception) is primarily prosecuted under the Fraud Act 2006, with Computer Misuse Act also applicable."
            }
        ]
    },
    {
        "id": "hack_3",
        "type": "hacking",
        "title": "Password Attacks",
        "subtitle": "Cracking the First Line of Defence",
        "description": "Explore how passwords are compromised and why",
        "order": 3,
        "slides": [
            {
                "title": "Why Passwords Are Targeted",
                "content": "Passwords are the most common form of authentication — and the most commonly compromised.\n\nDespite decades of advice, the most common passwords worldwide are still '123456', 'password', and 'qwerty'. This makes password attacks incredibly effective.\n\nAttackers target passwords because:\n• One stolen password can give access to multiple accounts (password reuse)\n• Many services have weak rate-limiting\n• Stolen password databases are sold on the dark web\n• People choose predictable patterns\n\nUnderstanding how passwords are attacked helps you choose better passwords and build more secure systems.",
                "icon": "🔐"
            },
            {
                "title": "Brute Force Attacks",
                "content": "A brute force attack tries EVERY possible combination of characters until the correct password is found.\n\nFor a 6-character password using lowercase letters:\n• 26^6 = 308 million combinations\n• Modern hardware cracks this in seconds\n\nFor an 8-character password with uppercase, lowercase, numbers & symbols:\n• 95^8 = 6.6 quadrillion combinations\n• Takes years with typical hardware\n\nThis is why length and complexity matter enormously. Each extra character exponentially increases the time to crack.\n\n🛠️ Tools: Hydra, Medusa, Burp Suite (online brute force)\nHashcat, John the Ripper (offline hash cracking)",
                "icon": "💪"
            },
            {
                "title": "Dictionary Attacks",
                "content": "A dictionary attack uses a pre-compiled wordlist of common passwords instead of trying every combination.\n\nWhy it works:\n• Most people use real words, names, or simple substitutions (p@ssw0rd)\n• Password databases like RockYou (14 million real passwords) are freely available\n• Common patterns are well known: word + number + symbol\n\nA dictionary attack is MUCH faster than brute force because it only tries likely candidates.\n\nWordlists like rockyou.txt, SecLists, and CeWL (website-generated wordlists) give attackers millions of likely passwords to try in seconds.\n\nThis is why 'P@ssw0rd1!' is NOT a strong password despite meeting most complexity requirements.",
                "icon": "📖"
            },
            {
                "title": "Rainbow Tables & Password Hashing",
                "content": "Websites store passwords as HASHES — a one-way mathematical transformation. The same input always produces the same hash, but you can't reverse it.\n\nExample (MD5): 'password' → '5f4dcc3b5aa765d61d8327deb882cf99'\n\nRainbow tables are pre-computed databases of password-to-hash mappings. An attacker who steals a password database can look up hashes instantly.\n\nDefence: SALTING adds a random string to each password before hashing. This means even identical passwords have different hashes, making rainbow tables useless.\n\nModern secure hashing: bcrypt, Argon2, scrypt — these are deliberately slow and include salting automatically.",
                "icon": "🌈"
            },
            {
                "title": "Credential Stuffing",
                "content": "Credential stuffing uses KNOWN username/password pairs (from previous data breaches) to try to log into other services.\n\nBecause most people reuse passwords, if your LinkedIn password was in a breach, attackers will try it on your bank, email, and other accounts.\n\nThe scale is massive:\n• Collections like 'Collection #1' contained 773 million credentials\n• Automated bots can test thousands of combinations per second\n• Services like Have I Been Pwned (haveibeenpwned.com) let you check if your email was in a breach\n\nThis attack requires NO hacking skill — just a list of leaked credentials and automation.",
                "icon": "🗄️"
            },
            {
                "title": "Ethics & Legal Position",
                "content": "⚖️ Password attacks against systems you don't own or have permission to test are criminal offences.\n\nLegal uses of password cracking:\n✅ Penetration testing with written authorisation\n✅ Password recovery of your OWN systems\n✅ CTF (Capture the Flag) competitions\n✅ Security research in controlled environments\n\nIllegal uses:\n❌ Attempting to access any account that isn't yours\n❌ Running brute force against live services\n❌ Using stolen credential lists\n\nThe Computer Misuse Act 1990 Section 1 covers unauthorised access to computer systems, with penalties of up to 2 years imprisonment for basic offences and up to 10 years for more serious cases.",
                "icon": "⚖️"
            }
        ],
        "quiz": [
            {
                "question": "What is the key difference between a brute force attack and a dictionary attack?",
                "options": {"A": "Brute force is faster than dictionary attacks", "B": "Dictionary attacks only work on encrypted systems", "C": "Brute force tries all combinations; dictionary attacks use likely password wordlists", "D": "They are the same thing"},
                "correct": "C",
                "explanation": "Brute force tries every possible combination; dictionary attacks use pre-built wordlists of common passwords, making them much faster in practice."
            },
            {
                "question": "Why is adding a SALT to a password hash important?",
                "options": {"A": "It makes the hash shorter", "B": "It prevents rainbow table attacks by making identical passwords produce different hashes", "C": "It makes brute force attacks impossible", "D": "It encrypts the hash for extra security"},
                "correct": "B",
                "explanation": "Salting adds a random value before hashing, ensuring identical passwords produce unique hashes. This defeats pre-computed rainbow tables."
            },
            {
                "question": "An attacker uses email and password pairs leaked from a social media breach to try to log into online banking. This is called:",
                "options": {"A": "SQL Injection", "B": "Credential Stuffing", "C": "Phishing", "D": "Keylogging"},
                "correct": "B",
                "explanation": "Credential stuffing uses known leaked credentials to try to access other services, exploiting password reuse."
            },
            {
                "question": "Which password is STRONGEST against a dictionary attack?",
                "options": {"A": "P@ssw0rd1!", "B": "fluffy2019", "C": "xK9#mP2$qL7!nR4", "D": "MyDogBob2024!"},
                "correct": "C",
                "explanation": "Random characters with no recognisable patterns or words are strongest. Dictionary attacks exploit predictable patterns and real words."
            },
            {
                "question": "Which hashing algorithm is most suitable for storing user passwords?",
                "options": {"A": "MD5", "B": "SHA-1", "C": "Base64", "D": "bcrypt"},
                "correct": "D",
                "explanation": "bcrypt is designed for password hashing — it's deliberately slow, includes built-in salting, and resists brute force attacks. MD5 and SHA-1 are too fast for password storage."
            }
        ]
    },
    {
        "id": "hack_4",
        "type": "hacking",
        "title": "Network Scanning",
        "subtitle": "Mapping the Attack Surface",
        "description": "Learn how attackers map and probe networks",
        "order": 4,
        "slides": [
            {
                "title": "What is Network Scanning?",
                "content": "Network scanning is an active reconnaissance technique used to map out a target's network infrastructure.\n\nAttackers use it to discover:\n• Which devices are online (host discovery)\n• Which ports are open on those devices\n• What services are running on those ports\n• What operating systems are in use\n• Potential vulnerabilities in those services\n\nThis is typically where recon transitions from passive to active — the attacker begins probing the target directly.\n\nThink of it as a locksmith walking down a street, testing every door and window to see which ones are unlocked.",
                "icon": "📡"
            },
            {
                "title": "Understanding Ports",
                "content": "Every networked device communicates through PORTS — logical channels for specific types of traffic.\n\nThere are 65,535 ports. Well-known ones:\n• Port 22 — SSH (remote login)\n• Port 80 — HTTP (web)\n• Port 443 — HTTPS (secure web)\n• Port 21 — FTP (file transfer)\n• Port 3389 — RDP (Windows remote desktop)\n• Port 3306 — MySQL database\n\nAn open port = a potential entry point. If an outdated or misconfigured service is running on an open port, it may contain exploitable vulnerabilities.\n\nPort scanning identifies which doors are open — the next step is finding which ones are unlocked.",
                "icon": "🚪"
            },
            {
                "title": "Nmap: The Network Scanner",
                "content": "Nmap (Network Mapper) is the most widely used network scanning tool in the world — used by both attackers and defenders.\n\nCommon Nmap commands:\n• nmap 192.168.1.1 — Basic scan\n• nmap -sS 192.168.1.0/24 — Stealth SYN scan of a network range\n• nmap -sV 192.168.1.1 — Service version detection\n• nmap -O 192.168.1.1 — OS detection\n• nmap -A 192.168.1.1 — Aggressive scan (all of the above)\n• nmap --script vuln 192.168.1.1 — Vulnerability scan\n\nNmap can reveal an enormous amount of information about a target's network — which is why it's a standard tool in every penetration tester's toolkit.",
                "icon": "🗺️"
            },
            {
                "title": "Vulnerability Scanning",
                "content": "Vulnerability scanning goes beyond port scanning to identify known weaknesses in discovered services.\n\n🛠️ Nessus — Industry-standard commercial vulnerability scanner\n🛠️ OpenVAS — Free, open source alternative\n🛠️ Nikto — Web server vulnerability scanner\n🛠️ Metasploit — Exploitation framework with built-in scanner\n\nVulnerability scanners compare found services against databases of known vulnerabilities (CVEs — Common Vulnerabilities and Exposures).\n\nA CVE is a public record of a known security flaw with a severity score. Example: CVE-2021-44228 is the critical 'Log4Shell' vulnerability that affected millions of systems.",
                "icon": "🔬"
            },
            {
                "title": "Responsible Disclosure",
                "content": "If you discover a vulnerability in a system you're AUTHORISED to test, or even accidentally, you have ethical and sometimes legal obligations.\n\nResponsible Disclosure (Coordinated Vulnerability Disclosure):\n1. Document the vulnerability thoroughly\n2. Contact the organisation's security team privately\n3. Give them reasonable time to patch (typically 90 days)\n4. Only publish details after a patch is available\n\nMany companies run Bug Bounty programmes (HackerOne, Bugcrowd) that PAY researchers for responsibly disclosed vulnerabilities.\n\nResponsible disclosure protects users, supports the security community, and often rewards the researcher — it's the ethical foundation of offensive security.",
                "icon": "📋"
            },
            {
                "title": "Ethics & Legal Framework",
                "content": "⚖️ Network scanning without permission is illegal.\n\nEven though Nmap and similar tools are freely available, using them against systems you don't own or have explicit written permission to test is a criminal offence.\n\nLegal frameworks:\n• Computer Misuse Act 1990 (UK)\n• CFAA — Computer Fraud and Abuse Act (USA)\n• Similar laws exist in virtually every country\n\nAuthorised contexts:\n✅ Your own home network\n✅ Lab environments and virtual machines\n✅ CTF competitions\n✅ With signed penetration testing contract\n\nProfessional penetration testers always operate with a written 'Rules of Engagement' document specifying exactly what they can and cannot scan.",
                "icon": "⚖️"
            }
        ],
        "quiz": [
            {
                "question": "What is the primary purpose of network scanning?",
                "options": {"A": "To steal data from the target", "B": "To discover open ports, services, and potential vulnerabilities on a network", "C": "To send phishing emails automatically", "D": "To crash the target's servers"},
                "correct": "B",
                "explanation": "Network scanning maps the attack surface — discovering what devices, ports, and services are exposed before any exploitation."
            },
            {
                "question": "Port 443 is typically associated with which service?",
                "options": {"A": "FTP (File Transfer)", "B": "SSH (Secure Shell)", "C": "HTTPS (Secure Web)", "D": "MySQL Database"},
                "correct": "C",
                "explanation": "Port 443 is the standard port for HTTPS — encrypted web traffic. Port 80 is HTTP (unencrypted)."
            },
            {
                "question": "What does CVE stand for in the context of vulnerability scanning?",
                "options": {"A": "Common Vulnerability Exposure", "B": "Cyber Vulnerability Exploit", "C": "Common Vulnerabilities and Exposures", "D": "Critical Vector Event"},
                "correct": "C",
                "explanation": "CVE = Common Vulnerabilities and Exposures. It's a public database of known security flaws, each given a unique identifier and severity score."
            },
            {
                "question": "Which tool is MOST associated with port scanning and network discovery?",
                "options": {"A": "Wireshark", "B": "Nmap", "C": "Metasploit", "D": "Burp Suite"},
                "correct": "B",
                "explanation": "Nmap (Network Mapper) is the industry-standard tool for port scanning, host discovery, and service version detection."
            },
            {
                "question": "What is 'responsible disclosure'?",
                "options": {"A": "Immediately publishing vulnerabilities to warn the public", "B": "Selling vulnerabilities to the highest bidder", "C": "Privately notifying an organisation about a vulnerability before making it public", "D": "Exploiting a vulnerability to prove it exists"},
                "correct": "C",
                "explanation": "Responsible disclosure means privately notifying the affected organisation, giving them time to patch, then publishing details — protecting users while advancing security research."
            }
        ]
    },

    # ── DEFENCE STAGES ───────────────────────────────────────────────────────
    {
        "id": "def_1",
        "type": "defence",
        "title": "Password Security",
        "subtitle": "Build Your First Line of Defence",
        "description": "Master passwords, MFA, and account security",
        "order": 1,
        "slides": [
            {
                "title": "Why Password Security Matters",
                "content": "81% of confirmed data breaches involve weak, reused, or stolen passwords. Despite being the most fundamental security control, passwords remain the most exploited vulnerability.\n\nA compromised password can lead to:\n• Financial theft\n• Identity fraud\n• Corporate espionage\n• Complete account takeover\n\nThe good news: strong password hygiene is one of the easiest security improvements anyone can make. You don't need technical expertise — just good habits.\n\nIn this stage, you'll learn not just WHAT makes a strong password, but WHY the rules exist.",
                "icon": "🔑"
            },
            {
                "title": "Anatomy of a Strong Password",
                "content": "What actually makes a password strong?\n\n✅ LENGTH — The single most important factor. Each extra character exponentially increases crack time.\n• 8 characters = crackable in hours\n• 12 characters = years\n• 16+ characters = centuries\n\n✅ UNPREDICTABILITY — Avoid patterns, words, names, dates, keyboard walks (qwerty, 123456)\n\n✅ COMPLEXITY — Mix uppercase, lowercase, numbers, and symbols\n\n✅ UNIQUENESS — Never reuse passwords across accounts\n\nBest approach: Use a PASSPHRASE — 4+ random words strung together. 'correct-horse-battery-staple' is both memorable and extremely strong.",
                "icon": "💪"
            },
            {
                "title": "Password Managers",
                "content": "The only realistic way to use unique, strong passwords for every account is a PASSWORD MANAGER.\n\nA password manager:\n• Generates and stores unique strong passwords for every site\n• Auto-fills credentials securely\n• Alerts you to breached or reused passwords\n• Encrypts everything with a single master password\n\n🛠️ Reputable options: Bitwarden (free, open source), 1Password, Dashlane, KeePass\n\nYou only need to remember ONE strong master password.\n\nThe master password should be a long passphrase (20+ characters) that you've memorised and never written down digitally.",
                "icon": "🗝️"
            },
            {
                "title": "Two-Factor Authentication (2FA)",
                "content": "Two-Factor Authentication (2FA) adds a second layer of security beyond your password.\n\nThe three factors of authentication:\n• Something you KNOW — password\n• Something you HAVE — phone, hardware key\n• Something you ARE — fingerprint, face\n\n2FA combines any two of these. Even if an attacker steals your password, they still can't log in without your second factor.\n\nTypes of 2FA (strongest to weakest):\n1. Hardware key (YubiKey) — Most secure\n2. Authenticator app (Google Authenticator, Authy) — Very secure\n3. SMS code — Better than nothing, but vulnerable to SIM swapping\n\nEnable 2FA on every account that supports it — especially email, banking, and work accounts.",
                "icon": "📱"
            },
            {
                "title": "Recognising Credential Threats",
                "content": "Knowing your credentials are at risk:\n\n🔴 Have I Been Pwned — haveibeenpwned.com lets you check if your email appears in known breaches. Check regularly.\n\n🔴 Suspicious login alerts — Many services will email you when a new device logs in. Take these seriously.\n\n🔴 Unexpected password reset emails — You didn't request one? Someone is trying to access your account.\n\n🔴 Account lockouts — Multiple failed login attempts trigger lockouts. Someone is brute-forcing your account.\n\nIf you suspect a compromise:\n1. Change the password immediately from a safe device\n2. Check active sessions and log out all others\n3. Review recent account activity\n4. Enable 2FA if not already active",
                "icon": "⚠️"
            },
            {
                "title": "Organisational Password Policies",
                "content": "In an organisational context, password policies are formally defined rules. Modern NCSC (National Cyber Security Centre) guidance recommends:\n\n✅ Minimum 12 characters (not 8)\n✅ No mandatory complexity rules (they lead to predictable patterns)\n✅ No forced regular rotation unless breach is suspected\n✅ Mandatory 2FA for all accounts\n✅ Block known breached passwords\n✅ Use of approved password managers\n\nNote: Forcing users to change passwords every 30 days DECREASES security — users choose weaker passwords and follow predictable patterns (Password1, Password2...).\n\nThe NCSC's approach prioritises practicality and real-world security over checkbox compliance.",
                "icon": "🏛️"
            }
        ],
        "quiz": [
            {
                "question": "Which of these is the STRONGEST password?",
                "options": {"A": "P@ssw0rd123!", "B": "fluffy2019", "C": "correct-horse-battery-staple-voyage", "D": "Tr0ub4dor&3"},
                "correct": "C",
                "explanation": "Length beats complexity. A long passphrase of random words (28+ chars) is both memorable and vastly stronger than short complex strings."
            },
            {
                "question": "What is the MOST secure form of two-factor authentication?",
                "options": {"A": "SMS text message code", "B": "Email verification code", "C": "Hardware security key (e.g., YubiKey)", "D": "Security question"},
                "correct": "C",
                "explanation": "Hardware keys are the gold standard — they can't be phished, can't be SIM-swapped, and require physical possession."
            },
            {
                "question": "Why does modern NCSC guidance recommend AGAINST forcing frequent password changes?",
                "options": {"A": "Password changes take too long", "B": "Users choose weaker passwords and follow predictable patterns when forced to change regularly", "C": "New passwords are harder to remember", "D": "It wastes IT department time"},
                "correct": "B",
                "explanation": "Forced rotation leads to Password1 → Password2 → Password3. This predictability makes passwords weaker, not stronger."
            },
            {
                "question": "What is a password manager's primary security benefit?",
                "options": {"A": "It stores passwords in plain text for easy access", "B": "It allows you to use the same strong password everywhere", "C": "It enables use of unique, strong passwords for every account without memorising them", "D": "It replaces the need for 2FA"},
                "correct": "C",
                "explanation": "Password managers solve the impossible choice between memorability and uniqueness — you only need to remember one master password."
            },
            {
                "question": "Which website allows you to check if your email address appears in known data breaches?",
                "options": {"A": "norton.com", "B": "haveibeenpwned.com", "C": "passwordcheck.gov.uk", "D": "breachreport.io"},
                "correct": "B",
                "explanation": "Have I Been Pwned (haveibeenpwned.com), created by security researcher Troy Hunt, is the most trusted breach notification service."
            }
        ]
    },
    {
        "id": "def_2",
        "type": "defence",
        "title": "Anti-Phishing",
        "subtitle": "Don't Take the Bait",
        "description": "Learn to identify and neutralise phishing attempts",
        "order": 2,
        "slides": [
            {
                "title": "Your Human Firewall",
                "content": "Technology alone cannot stop phishing. Every spam filter and email gateway can be bypassed — but an educated human is the most powerful defence.\n\nThis stage turns the knowledge from the Phishing Attacks hacking stage into defensive skills. You'll learn to recognise attacks that even technical professionals fall for.\n\nStatistics to remember:\n• 91% of cyber attacks begin with a phishing email\n• The average time to click a phishing link is just 82 seconds\n• 95% of successful breaches involve human error\n\nA single well-trained employee can stop an attack that would cost millions in damages. Being that employee starts here.",
                "icon": "🛡️"
            },
            {
                "title": "Red Flags in Emails",
                "content": "Train yourself to spot these warning signs:\n\n🚨 SENDER ADDRESS — Not the domain you'd expect? 'support@paypa1.com', 'noreply@amazon-support.net'\n\n🚨 URGENCY — 'Immediate action required', 'Account suspended in 2 hours', 'Final warning'\n\n🚨 UNEXPECTED REQUESTS — Banks will never ask for your full password by email\n\n🚨 HOVER BEFORE CLICKING — Hover over any link and check the real URL in your browser's status bar\n\n🚨 SUSPICIOUS ATTACHMENTS — Unexpected invoices, shipping notices, tax documents\n\n🚨 GRAMMAR & DESIGN — Typos, misaligned logos, odd formatting (less common now with AI-generated phishing)\n\n🚨 'TOO GOOD TO BE TRUE' — Prizes, refunds, inheritances",
                "icon": "🚨"
            },
            {
                "title": "URL & Link Analysis",
                "content": "Links are the delivery mechanism for most phishing attacks. Learn to analyse them:\n\n🔍 HOVER before clicking — See the real destination URL\n\n🔍 CHECK THE DOMAIN — The actual domain is the last part before the first '/':\n• 'paypal.com.secure-login.net/paypal' — the domain is 'secure-login.net', NOT PayPal\n\n🔍 HTTPS ≠ SAFE — The padlock only means the connection is encrypted, NOT that the site is legitimate. Phishing sites use HTTPS too.\n\n🔍 URL SHORTENERS — bit.ly, tinyurl etc. hide the real destination. Use unshorten.it to reveal them.\n\n🔍 TYPOSQUATTING — goggle.com, arnazon.com, micros0ft.com\n\nWhen in doubt: go to the official website by typing the URL yourself, never via a link.",
                "icon": "🔗"
            },
            {
                "title": "Handling Suspicious Messages",
                "content": "What to do when you receive a suspicious email:\n\n✅ DO NOT click any links or open attachments\n✅ DO NOT reply to the email\n✅ DO hover over links to check real URLs\n✅ DO verify through an official channel — if it claims to be your bank, call their official number\n✅ DO report it — use your email client's 'Report Phishing' button, or forward to report@phishing.gov.uk (UK)\n✅ DO delete it after reporting\n\nIn a work context:\n✅ Report to your IT/security team immediately\n✅ Do NOT forward to colleagues to 'warn' them — this spreads the phishing link\n✅ Document what you did and saw for your security team's investigation",
                "icon": "📋"
            },
            {
                "title": "Phishing Simulations & Training",
                "content": "Many organisations run regular phishing simulations — authorised fake phishing emails sent to employees to test their awareness.\n\nIf you click a simulated phishing link, you'll typically see an educational page explaining what you missed and how to spot it next time. This is not punishment — it's training.\n\nEffective security awareness training:\n• Regular, realistic simulations\n• Immediate feedback when someone falls for a test\n• Clear reporting procedures\n• Positive reinforcement for correct reporting\n• Updates to cover new phishing techniques\n\nOrganisations with strong security cultures regularly achieve near-zero click rates on simulated phishing. This is achievable through consistent training.",
                "icon": "🎓"
            },
            {
                "title": "Multi-Factor Authentication as a Safety Net",
                "content": "Even if phishing successfully steals a password, MFA (Multi-Factor Authentication) provides a critical safety net.\n\n🛡️ Standard 2FA (authenticator app) — Attacker has your password but not your phone. They're blocked.\n\n⚠️ HOWEVER — Advanced phishing uses real-time proxy attacks (Evilginx2) that can steal MFA codes too, by sitting between you and the real site.\n\n🛡️ PHISHING-RESISTANT MFA — Hardware keys (FIDO2/WebAuthn) are bound to the specific domain. A fake site can't use your key even if you fall for the phishing attempt. This is why hardware keys are the gold standard.\n\nIf your organisation uses hardware keys: never insert them into unknown computers, and never approve unexpected push notifications.",
                "icon": "🔐"
            }
        ],
        "quiz": [
            {
                "question": "You receive an email from 'support@amazon-helpdesk.net' saying your order is delayed. What is the first red flag?",
                "options": {"A": "The email is about a delivery", "B": "The sender domain is not amazon.com", "C": "The email mentions customer support", "D": "The email was unexpected"},
                "correct": "B",
                "explanation": "The sender domain 'amazon-helpdesk.net' is not Amazon's domain (amazon.com). Attackers register lookalike domains to impersonate legitimate companies."
            },
            {
                "question": "A link in an email shows 'paypal.com' as the text, but when you hover it shows 'paypa1.com/login'. What should you do?",
                "options": {"A": "Click it — PayPal sometimes uses different URLs", "B": "The padlock means it's safe, so click it", "C": "Do not click — the real URL is a phishing site pretending to be PayPal", "D": "Reply to the email asking if it's legitimate"},
                "correct": "C",
                "explanation": "Always check the actual URL shown when hovering, not the displayed link text. 'paypa1.com' uses the number 1 instead of the letter l — a common typosquatting technique."
            },
            {
                "question": "A website uses HTTPS (shows a padlock). Does this mean it's safe to enter your password?",
                "options": {"A": "Yes — the padlock guarantees the site is legitimate", "B": "No — HTTPS only encrypts the connection, not that the site itself is trustworthy", "C": "Yes — phishing sites can't use HTTPS", "D": "Only if the padlock is green"},
                "correct": "B",
                "explanation": "HTTPS means the connection is encrypted — it says nothing about whether the site is legitimate. Phishing sites routinely use HTTPS."
            },
            {
                "question": "What is the CORRECT action when you receive a suspicious work email with an attachment you didn't expect?",
                "options": {"A": "Open it to check what it is, then delete if suspicious", "B": "Forward it to colleagues to warn them", "C": "Don't open it — report it to your IT/security team immediately", "D": "Reply asking if it's legitimate"},
                "correct": "C",
                "explanation": "Never open suspicious attachments. Report immediately to IT/security. Forwarding it to colleagues spreads the phishing link further."
            },
            {
                "question": "Which type of MFA is resistant to real-time phishing proxy attacks?",
                "options": {"A": "SMS text message codes", "B": "Time-based one-time passwords (TOTP) from an authenticator app", "C": "Email verification codes", "D": "Hardware security keys using FIDO2/WebAuthn"},
                "correct": "D",
                "explanation": "FIDO2/WebAuthn hardware keys are phishing-resistant because they're bound to the specific domain. They won't work on fake sites, even if the victim is tricked into visiting one."
            }
        ]
    },
    {
        "id": "def_3",
        "type": "defence",
        "title": "Network Defence",
        "subtitle": "Fortify Your Digital Perimeter",
        "description": "Firewalls, IDS, VPNs and network hardening",
        "order": 3,
        "slides": [
            {
                "title": "Defence in Depth",
                "content": "Network defence is built on the principle of DEFENCE IN DEPTH — multiple overlapping layers of security, so that if one layer fails, others remain.\n\nThink of a medieval castle: moat, outer walls, inner walls, keep, guards at every door. An attacker must defeat every layer.\n\nNetwork security layers:\n1. Perimeter — Firewall, DMZ\n2. Network — IDS/IPS, network segmentation\n3. Host — Endpoint security, patch management\n4. Application — WAF, input validation\n5. Data — Encryption, access control\n\nNo single security control is perfect. Multiple layers mean an attacker who bypasses the firewall still faces endpoint security, encrypted data, and more.",
                "icon": "🏰"
            },
            {
                "title": "Firewalls",
                "content": "A firewall monitors and controls incoming and outgoing network traffic based on defined security rules.\n\nTypes:\n🔷 PACKET FILTERING — Inspects each packet's source/destination IP and port. Fast but simple.\n🔷 STATEFUL INSPECTION — Tracks connection state. Knows if traffic is part of an established connection.\n🔷 NEXT-GENERATION FIREWALL (NGFW) — Deep packet inspection, application awareness, intrusion prevention. Modern standard.\n\nKey principles:\n• Default DENY — Block everything, then explicitly allow what's needed\n• Least privilege — Only open ports that are absolutely required\n• Egress filtering — Monitor outbound traffic too (data exfiltration)\n\n🛠️ Common tools: pfSense, Cisco ASA, Palo Alto, Windows Defender Firewall",
                "icon": "🔥"
            },
            {
                "title": "Intrusion Detection & Prevention",
                "content": "While firewalls control traffic at the perimeter, IDS/IPS monitor traffic patterns for signs of attack.\n\n🔍 IDS (Intrusion Detection System) — DETECTS suspicious activity and alerts administrators. Passive.\n\n🚫 IPS (Intrusion Prevention System) — DETECTS AND BLOCKS suspicious activity automatically. Active.\n\nDetection methods:\n• Signature-based — Matches known attack patterns (like antivirus). Fast but misses new attacks.\n• Anomaly-based — Establishes a 'normal' baseline and flags deviations. Catches new threats but more false positives.\n• Behaviour-based — Analyses behaviour patterns over time.\n\n🛠️ Tools: Snort, Suricata (open source), Cisco Firepower, CrowdStrike",
                "icon": "🚨"
            },
            {
                "title": "VPNs and Zero Trust",
                "content": "VPN (Virtual Private Network) creates an encrypted tunnel for network traffic — essential for remote workers accessing corporate resources.\n\nHow a VPN works:\n1. Client connects to VPN server\n2. All traffic is encrypted end-to-end\n3. Traffic appears to originate from the VPN server's IP\n4. Protects against eavesdropping on untrusted networks (public WiFi)\n\nZero Trust Architecture — Modern approach replacing traditional perimeter-based security:\n• 'Never trust, always verify'\n• Every access request is authenticated and authorised, even from inside the network\n• Assumes the network is already compromised\n• Micro-segmentation limits attacker movement\n\nZero Trust is increasingly the standard for large organisations following high-profile supply chain attacks.",
                "icon": "🔒"
            },
            {
                "title": "Network Segmentation",
                "content": "Network segmentation divides a network into isolated zones to limit the damage of a breach.\n\nWithout segmentation: One compromised device can reach every other device. An attacker on the guest WiFi could access your servers.\n\nWith segmentation:\n• Guest WiFi: internet access only, no access to internal resources\n• Corporate network: separated by department/function\n• DMZ (Demilitarised Zone): public-facing servers isolated from internal network\n• OT/IoT network: industrial devices kept completely separate\n\nImplemented using VLANs (Virtual LANs) on managed switches and enforced by firewall rules between segments.\n\nPrinciple: Lateral movement (spreading through a network after initial access) should be as difficult as possible.",
                "icon": "🗂️"
            },
            {
                "title": "Patch Management & Hardening",
                "content": "The majority of successful attacks exploit KNOWN vulnerabilities — ones that already have patches available.\n\nWannaCry (2017): Infected 230,000 computers in 150 countries using a Windows vulnerability. Microsoft had released a patch 2 months earlier.\n\nPatch management best practice:\n✅ Inventory all systems and software\n✅ Monitor CVE databases for new vulnerabilities\n✅ Test patches in a staging environment\n✅ Deploy critical patches within 24-72 hours\n✅ Have a documented patch management process\n\nSystem hardening — Reducing attack surface:\n• Disable all unused services and ports\n• Remove default accounts and change default passwords\n• Enable logging and monitoring\n• Apply least privilege to all accounts",
                "icon": "🔧"
            }
        ],
        "quiz": [
            {
                "question": "What is the principle of 'Defence in Depth'?",
                "options": {"A": "Using the most expensive security tools available", "B": "Having a very strong single firewall", "C": "Using multiple overlapping layers of security so no single failure is catastrophic", "D": "Monitoring the network 24/7"},
                "correct": "C",
                "explanation": "Defence in depth means multiple security layers — if one fails, others remain. No single control is assumed to be perfect."
            },
            {
                "question": "What is the key difference between an IDS and an IPS?",
                "options": {"A": "IDS is more expensive than IPS", "B": "IDS only monitors and alerts; IPS actively blocks threats", "C": "IPS only monitors email traffic", "D": "IDS requires hardware; IPS is software only"},
                "correct": "B",
                "explanation": "IDS = Intrusion Detection System (passive — alerts only). IPS = Intrusion Prevention System (active — detects and blocks)."
            },
            {
                "question": "A company puts its web servers in a DMZ. What is the purpose of this?",
                "options": {"A": "To make the web servers faster", "B": "To isolate public-facing servers from the internal corporate network", "C": "To provide a backup if the main network fails", "D": "To give customers direct access to internal databases"},
                "correct": "B",
                "explanation": "A DMZ (Demilitarised Zone) isolates public-facing servers. If a web server is compromised, the attacker can't directly reach internal systems."
            },
            {
                "question": "The WannaCry ransomware attack in 2017 exploited a Windows vulnerability. When had Microsoft released a patch for that vulnerability?",
                "options": {"A": "The same day as the attack", "B": "A year before the attack", "C": "Two months before the attack", "D": "No patch existed"},
                "correct": "C",
                "explanation": "Microsoft patched the EternalBlue vulnerability 2 months before WannaCry. Organisations that hadn't patched were devastated — highlighting why patch management is critical."
            },
            {
                "question": "Zero Trust Architecture follows which core principle?",
                "options": {"A": "Trust devices inside the network perimeter by default", "B": "Never trust, always verify — authenticate every request regardless of network location", "C": "Block all external traffic unless explicitly whitelisted", "D": "Trust verified users on all internal systems"},
                "correct": "B",
                "explanation": "Zero Trust assumes the network is already compromised. Every access request — even from inside — must be authenticated and authorised."
            }
        ]
    },
    {
        "id": "def_4",
        "type": "defence",
        "title": "Incident Response",
        "subtitle": "When Attacks Succeed",
        "description": "How to detect, contain, and recover from cyber incidents",
        "order": 4,
        "slides": [
            {
                "title": "Why Incident Response Matters",
                "content": "No organisation is perfectly secure. Every security team must assume that at some point, an attacker will succeed. The question is not IF you'll be breached — it's WHEN, and how ready you'll be when it happens.\n\nA well-executed incident response can:\n• Stop an attack before significant damage occurs\n• Preserve evidence for investigation\n• Minimise downtime and financial loss\n• Meet legal and regulatory reporting obligations\n• Prevent the same incident from recurring\n\nWithout a plan, breaches become disasters. The average cost of a data breach in 2024 was $4.88 million. Organisations with mature IR programmes spend significantly less per incident.",
                "icon": "🚨"
            },
            {
                "title": "The IR Lifecycle (NIST Framework)",
                "content": "The NIST Cybersecurity Framework defines 5 phases of incident response:\n\n1️⃣ PREPARATION — Build the team, create playbooks, test systems, train staff\n2️⃣ DETECTION & ANALYSIS — Identify indicators of compromise (IoCs), determine scope and severity\n3️⃣ CONTAINMENT — Isolate affected systems to prevent spread, short-term then long-term\n4️⃣ ERADICATION — Remove the threat: malware, backdoors, compromised accounts\n5️⃣ RECOVERY — Restore systems from clean backups, monitor closely, return to operations\n6️⃣ LESSONS LEARNED — Post-incident review, update defences, document findings\n\nThis isn't a linear process — teams often cycle between phases as new information emerges.",
                "icon": "🔄"
            },
            {
                "title": "Detection & Triage",
                "content": "Detecting an incident quickly is critical. The average time to detect a breach is 194 days — meaning attackers have months of undetected access.\n\nDetection sources:\n• SIEM (Security Information and Event Management) — Aggregates and analyses logs from across the network\n• IDS/IPS alerts\n• Antivirus/EDR alerts\n• User reports ('something weird is happening')\n• Threat intelligence feeds\n• External notification (from law enforcement, other companies)\n\nTriage questions:\n• What systems are affected?\n• What data may be compromised?\n• Is the attack ongoing?\n• What is the business impact?\n• Does this trigger legal reporting obligations (GDPR: 72 hours)?\n\nNot every alert is an incident — triage separates real incidents from false positives.",
                "icon": "🔍"
            },
            {
                "title": "Containment & Evidence Preservation",
                "content": "Once an incident is confirmed, CONTAINMENT is the immediate priority — stopping the spread.\n\nShort-term containment:\n• Isolate affected systems from the network (network segmentation pays off here)\n• Block malicious IPs at the firewall\n• Disable compromised accounts\n• Take memory dumps BEFORE shutting down (volatile evidence)\n\nEvidence preservation:\n• Do NOT switch off systems hastily — you may destroy valuable volatile evidence\n• Create forensic images of affected systems\n• Preserve all logs before they're overwritten\n• Maintain a strict chain of custody\n\nLong-term containment allows normal business operations to continue while investigation proceeds — using clean backup systems where possible.",
                "icon": "🔒"
            },
            {
                "title": "Eradication & Recovery",
                "content": "ERADICATION removes everything the attacker left behind:\n• All malware, backdoors, and remote access tools\n• All compromised accounts and credentials\n• All attacker infrastructure (C2 callbacks)\n\nCommon mistakes:\n❌ Removing malware but missing the backdoor that reinstalls it\n❌ Rebuilding from a backup that was already compromised\n❌ Restoring too quickly before fully understanding the attack\n\nRECOVERY returns to normal operations:\n• Restore from KNOWN CLEAN backups (before infection)\n• Force password resets for all potentially affected accounts\n• Apply all missing patches\n• Increase monitoring for recurrence\n• Validate that systems are clean before going live\n\n'Return to normal' should be gradual, verified, and monitored.",
                "icon": "🔧"
            },
            {
                "title": "Lessons Learned & Legal Obligations",
                "content": "Post-Incident Review (PIR) — conducted after every significant incident:\n• What happened and how?\n• What worked well in the response?\n• What failed or was missing?\n• What changes will prevent recurrence?\n• What was the total impact (financial, reputational)?\n\nLegal obligations (UK/EU):\n• GDPR Article 33 — Personal data breaches must be reported to the ICO within 72 HOURS\n• NIS Regulations — Operators of essential services must report significant incidents\n• Financial sector — FCA requires reporting within prescribed timeframes\n\nFailure to report a qualifying breach can result in fines up to £17.5 million or 4% of global annual turnover under GDPR.\n\nDocumentation is critical — both for regulatory compliance and for improving future defences.",
                "icon": "📋"
            }
        ],
        "quiz": [
            {
                "question": "According to the NIST framework, what is the FIRST phase of incident response?",
                "options": {"A": "Detection and Analysis", "B": "Containment", "C": "Preparation", "D": "Eradication"},
                "correct": "C",
                "explanation": "Preparation comes first — building the IR team, creating playbooks, training staff, and setting up monitoring before incidents occur."
            },
            {
                "question": "Under GDPR, how long does an organisation have to report a personal data breach to the ICO?",
                "options": {"A": "24 hours", "B": "72 hours", "C": "7 days", "D": "30 days"},
                "correct": "B",
                "explanation": "GDPR Article 33 requires notification to the supervisory authority (ICO in the UK) within 72 hours of becoming aware of a personal data breach."
            },
            {
                "question": "During containment, why should you take a memory dump BEFORE shutting down a compromised system?",
                "options": {"A": "To speed up the shutdown process", "B": "To preserve volatile evidence like running processes and network connections that would be lost on shutdown", "C": "To comply with GDPR", "D": "To create a backup for recovery"},
                "correct": "B",
                "explanation": "RAM contains volatile evidence — running malware, network connections, encryption keys — that vanishes when power is cut. Capture it first."
            },
            {
                "question": "What is the average time for organisations to detect a cyber breach?",
                "options": {"A": "Hours", "B": "Days", "C": "194 days", "D": "2 years"},
                "correct": "C",
                "explanation": "The average dwell time (attacker presence before detection) has historically been around 194 days — meaning attackers often have months of undetected access."
            },
            {
                "question": "During recovery, you restore from a backup made during the suspected infection window. What is the risk?",
                "options": {"A": "The backup may be too large", "B": "The backup may also be compromised, reintroducing the attacker's foothold", "C": "Regulatory requirements prevent restoring from old backups", "D": "There is no risk if the backup was encrypted"},
                "correct": "B",
                "explanation": "Restoring from a compromised backup reintroduces the attack. Always verify backup integrity and ensure you're restoring from a clean, pre-infection point."
            }
        ]
    }
]

# lookup dictionary
STAGES_BY_ID = {s["id"]: s for s in STAGES}

def get_completed_stages(user_id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT stage_id FROM user_progress WHERE user_id = %s AND completed = TRUE",
                (user_id,)
            )
            rows = cur.fetchall()
    finally:
        db.close()
    return {row['stage_id'] for row in rows}

def is_stage_unlocked(stage_id, completed_stages):
    stage = STAGES_BY_ID.get(stage_id)
    if not stage:
        return False
    if stage['order'] == 1:
        return True
    # Find previous stage in same type
    prev_order = stage['order'] - 1
    for s in STAGES:
        if s['type'] == stage['type'] and s['order'] == prev_order:
            return s['id'] in completed_stages
    return False

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/health')
def health():
    db = None
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute('SELECT 1')
            cur.fetchone()
        return jsonify({'status': 'ok'}), 200
    except psycopg2.Error:
        app.logger.exception('Health check failed while querying the database')
        return jsonify({'status': 'unhealthy'}), 503
    finally:
        if db is not None:
            db.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('stages'))
    return render_template('index.html')

@app.route('/stages')
@login_required
def stages():
    return render_template('stages.html', username=session.get('username'))

@app.route('/lesson/<stage_id>')
@login_required
def lesson(stage_id):
    stage = STAGES_BY_ID.get(stage_id)
    if not stage:
        return redirect(url_for('stages'))
    completed = get_completed_stages(session['user_id'])
    if not is_stage_unlocked(stage_id, completed):
        return redirect(url_for('stages'))
    return render_template('lesson.html', stage=stage)

@app.route('/quiz/<stage_id>')
@login_required
def quiz(stage_id):
    stage = STAGES_BY_ID.get(stage_id)
    if not stage:
        return redirect(url_for('stages'))
    completed = get_completed_stages(session['user_id'])
    if not is_stage_unlocked(stage_id, completed):
        return redirect(url_for('stages'))
    return render_template('quiz.html', stage=stage)

# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    db = None
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
                (username, email, password_hash)
            )
            user_id = cur.fetchone()['id']
        db.commit()
        session['user_id'] = user_id
        session['username'] = username
        return jsonify({'success': True, 'redirect': '/stages'})
    except psycopg2.IntegrityError:
        return jsonify({'error': 'Username or email already exists'}), 409
    except psycopg2.Error:
        app.logger.exception('Registration failed while querying the database')
        return jsonify({'error': 'Registration failed'}), 500
    finally:
        if db is not None:
            db.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'All fields are required'}), 400

    db = None
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, username, password_hash FROM users WHERE username = %s OR email = %s",
                (username, username.lower())
            )
            user = cur.fetchone()

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid username or password'}), 401

        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'success': True, 'redirect': '/stages'})
    except psycopg2.Error:
        app.logger.exception('Login failed while querying the database')
        return jsonify({'error': 'Login failed'}), 500
    finally:
        if db is not None:
            db.close()

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/stages')
@login_required
def api_stages():
    completed = get_completed_stages(session['user_id'])
    result = []
    for stage in STAGES:
        result.append({
            'id': stage['id'],
            'type': stage['type'],
            'title': stage['title'],
            'subtitle': stage['subtitle'],
            'description': stage['description'],
            'order': stage['order'],
            'completed': stage['id'] in completed,
            'unlocked': is_stage_unlocked(stage['id'], completed)
        })
    return jsonify(result)

@app.route('/api/quiz/submit/<stage_id>', methods=['POST'])
@login_required
def submit_quiz(stage_id):
    stage = STAGES_BY_ID.get(stage_id)
    if not stage:
        return jsonify({'error': 'Stage not found'}), 404

    data = request.get_json()
    answers = data.get('answers', {})
    quiz = stage['quiz']

    correct = 0
    results = []
    for i, q in enumerate(quiz):
        key = str(i)
        user_answer = answers.get(key)
        is_correct = user_answer == q['correct']
        if is_correct:
            correct += 1
        results.append({
            'question': q['question'],
            'user_answer': user_answer,
            'correct_answer': q['correct'],
            'correct_option': q['options'][q['correct']],
            'is_correct': is_correct,
            'explanation': q['explanation']
        })

    score = int((correct / len(quiz)) * 100)
    passed = score >= 80

    if passed:
        db = None
        try:
            db = get_db()
            with db.cursor() as cur:
                cur.execute("""
                INSERT INTO user_progress (user_id, stage_id, completed, score, completed_at)
                VALUES (%s, %s, TRUE, %s, %s)
                ON CONFLICT (user_id, stage_id)
                DO UPDATE SET completed = TRUE,
                              score = GREATEST(user_progress.score, EXCLUDED.score),
                              completed_at = EXCLUDED.completed_at
                """, (session['user_id'], stage_id, score, datetime.now(timezone.utc)))
            db.commit()
        except psycopg2.Error:
            app.logger.exception('Failed to save quiz progress')
            return jsonify({'error': 'Could not save quiz progress'}), 503
        finally:
            if db is not None:
                db.close()

    return jsonify({
        'score': score,
        'correct': correct,
        'total': len(quiz),
        'passed': passed,
        'results': results
    })

if __name__ == '__main__':
    app.run()