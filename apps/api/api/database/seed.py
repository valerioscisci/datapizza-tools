from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from api.database.connection import SessionLocal, engine, Base
from api.database.models import Job, User, Application, News, Course, Experience, Education, Proposal, ProposalCourse, ProposalMilestone, ProposalMessage, EmailLog, NotificationPreference, AIReadinessAssessment
from api.auth import hash_password


def seed_jobs():
    """Seed the database with 10 fake job listings."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Drop and re-create for fresh seed
        db.query(Job).delete()
        db.commit()

        jobs = [
            Job(
                title="Senior Frontend Developer",
                company="TechFlow Italia",
                location="Milano",
                work_mode="hybrid",
                description="Cerchiamo un Senior Frontend Developer con esperienza in React e Next.js per guidare lo sviluppo della nostra piattaforma SaaS. Lavorerai con un team internazionale su prodotti innovativi nel settore fintech. Responsabilita': architettura frontend, code review, mentoring junior, ottimizzazione performance.",
                salary_min=45000,
                salary_max=60000,
                tags_json=json.dumps(["React", "Next.js", "TypeScript", "Tailwind CSS"]),
                experience_level="senior",
                experience_years="4+ anni",
                employment_type="full-time",
                smart_working="2-3 giorni/settimana",
                welfare="Welfare aziendale di \u20ac 1.500",
                language="Inglese: B2",
                created_at=datetime.now(timezone.utc) - timedelta(days=2),
            ),
            Job(
                title="Backend Engineer - Python",
                company="DataSphere",
                location="Roma",
                work_mode="remote",
                description="Unisciti al nostro team come Backend Engineer. Svilupperai API REST con FastAPI e gestirai infrastrutture cloud su AWS. Esperienza con database SQL e NoSQL richiesta. Team distribuito, metodologia agile, deploy continuo.",
                salary_min=40000,
                salary_max=55000,
                tags_json=json.dumps(["Python", "FastAPI", "AWS", "PostgreSQL"]),
                experience_level="mid",
                experience_years="3-4 anni",
                employment_type="full-time",
                smart_working="Full Remote",
                language="Inglese: B2",
                created_at=datetime.now(timezone.utc) - timedelta(days=3),
            ),
            Job(
                title="Full Stack Developer",
                company="InnovaHub",
                location="Torino",
                work_mode="onsite",
                description="Stiamo cercando un Full Stack Developer per il nostro team di prodotto. Lavorerai su applicazioni web moderne con React frontend e Node.js backend. Ambiente giovane e dinamico con possibilita' di crescita rapida.",
                salary_min=35000,
                salary_max=48000,
                tags_json=json.dumps(["React", "Node.js", "MongoDB", "Docker"]),
                experience_level="mid",
                experience_years="2-3 anni",
                employment_type="full-time",
                welfare="Buoni pasto \u20ac 8/giorno",
                created_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
            Job(
                title="AI/ML Engineer",
                company="NeuralTech",
                location="Milano",
                work_mode="remote",
                description="Cerchiamo un AI/ML Engineer per sviluppare modelli di machine learning e integrare soluzioni AI nei nostri prodotti. Esperienza con PyTorch e LLM richiesta. Lavorerai su progetti cutting-edge con dataset su larga scala.",
                salary_min=50000,
                salary_max=70000,
                tags_json=json.dumps(["Python", "PyTorch", "LLM", "MLOps"]),
                experience_level="senior",
                experience_years="5+ anni",
                employment_type="full-time",
                smart_working="Full Remote",
                welfare="Welfare aziendale di \u20ac 2.000",
                language="Inglese: C1",
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            Job(
                title="DevOps Engineer",
                company="CloudBase",
                location="Bologna",
                work_mode="hybrid",
                description="Gestisci e ottimizza la nostra infrastruttura cloud. Esperienza con Kubernetes, Terraform e CI/CD pipeline. Ambiente dinamico e in forte crescita. Parteciperai alla definizione dell'architettura cloud-native.",
                salary_min=42000,
                salary_max=58000,
                tags_json=json.dumps(["Kubernetes", "Terraform", "AWS", "CI/CD"]),
                experience_level="mid",
                experience_years="3-5 anni",
                employment_type="full-time",
                smart_working="1 giorno al mese in ufficio",
                language="Inglese: B1",
                created_at=datetime.now(timezone.utc) - timedelta(days=4),
            ),
            Job(
                title="Mobile Developer - React Native",
                company="AppFactory",
                location="Firenze",
                work_mode="hybrid",
                description="Sviluppa applicazioni mobile cross-platform con React Native. Collaborerai con designer e backend team per creare esperienze utente eccellenti. Pubblicazione su App Store e Google Play.",
                salary_min=35000,
                salary_max=50000,
                tags_json=json.dumps(["React Native", "TypeScript", "iOS", "Android"]),
                experience_level="mid",
                experience_years="2-4 anni",
                employment_type="full-time",
                smart_working="Smart 2-3 giorni/settimana",
                welfare="Buoni pasto + welfare \u20ac 500",
                created_at=datetime.now(timezone.utc) - timedelta(days=6),
            ),
            Job(
                title="Data Engineer",
                company="DataPipeline Srl",
                location="Milano",
                work_mode="remote",
                description="Progetta e implementa pipeline di dati scalabili. Lavorerai con big data, Apache Spark e strumenti di data orchestration. Team internazionale, stack moderno, cultura engineering-first.",
                salary_min=45000,
                salary_max=62000,
                tags_json=json.dumps(["Python", "Apache Spark", "Airflow", "SQL"]),
                experience_level="senior",
                experience_years="4+ anni",
                employment_type="full-time",
                smart_working="Full Remote",
                welfare="Welfare aziendale di \u20ac 1.000",
                language="Inglese: B2",
                created_at=datetime.now(timezone.utc) - timedelta(days=7),
            ),
            Job(
                title="Frontend Developer - Vue.js",
                company="WebCraft Studio",
                location="Napoli",
                work_mode="onsite",
                description="Cerchiamo un Frontend Developer con esperienza in Vue.js per sviluppare interfacce web moderne e performanti per i nostri clienti enterprise. Lavoro su progetti variegati e stimolanti.",
                salary_min=30000,
                salary_max=42000,
                tags_json=json.dumps(["Vue.js", "JavaScript", "Sass", "Vite"]),
                experience_level="mid",
                experience_years="2-3 anni",
                employment_type="full-time",
                created_at=datetime.now(timezone.utc) - timedelta(days=8),
            ),
            Job(
                title="Cybersecurity Analyst",
                company="SecureNet Italia",
                location="Roma",
                work_mode="hybrid",
                description="Proteggi le infrastrutture dei nostri clienti. Analisi delle vulnerabilita', penetration testing e implementazione di soluzioni di sicurezza. Certificazioni come CEH, CISSP o OSCP sono un plus.",
                salary_min=38000,
                salary_max=52000,
                tags_json=json.dumps(["Cybersecurity", "SIEM", "Penetration Testing", "Cloud Security"]),
                experience_level="mid",
                experience_years="3-4 anni",
                employment_type="full-time",
                smart_working="2 giorni/settimana",
                language="Inglese: B2",
                created_at=datetime.now(timezone.utc) - timedelta(days=10),
            ),
            Job(
                title="Tech Lead - Microservices",
                company="ScaleUp Ventures",
                location="Milano",
                work_mode="hybrid",
                description="Guida il team di sviluppo nella migrazione a microservizi. Definisci l'architettura, mentoring del team e hands-on coding. Stack: Go, gRPC, Kubernetes. Ruolo chiave nella crescita tecnica dell'azienda.",
                salary_min=55000,
                salary_max=75000,
                tags_json=json.dumps(["Go", "gRPC", "Kubernetes", "Microservices"]),
                experience_level="senior",
                experience_years="5+ anni",
                employment_type="full-time",
                smart_working="1 giorno al mese in ufficio",
                welfare="Welfare aziendale di \u20ac 2.500",
                language="Inglese: C1",
                created_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
        ]

        db.add_all(jobs)
        db.commit()
        print(f"Seeded {len(jobs)} jobs successfully.")

        # Store job IDs for application seeding
        all_jobs = db.query(Job).all()
        job_ids = [j.id for j in all_jobs]

        return job_ids
    finally:
        db.close()


def seed_users(job_ids: list[str] | None = None):
    """Seed the database with 10 Italian developer profiles and some applications."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Clean existing data — must respect FK constraints
        db.query(ProposalCourse).delete()
        db.query(Proposal).delete()
        db.query(Application).delete()
        db.query(User).delete()
        db.commit()

        hashed = hash_password("password123")

        users = [
            User(
                email="marco.rossi@email.it",
                password_hash=hashed,
                full_name="Marco Rossi",
                phone="+39 333 1234567",
                bio="Frontend developer appassionato di React e performance web. Contributore open source.",
                location="Milano",
                experience_level="senior",
                experience_years="5+ anni",
                current_role="Frontend Developer",
                skills_json=json.dumps(["React", "Next.js", "TypeScript", "Tailwind CSS", "GraphQL"]),
                availability_status="available",
                linkedin_url="https://linkedin.com/in/marco-rossi-dev",
                github_url="https://github.com/marcorossi",
                user_type="talent",
                ai_readiness_score=84,
                ai_readiness_level="expert",
                is_public=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=30),
            ),
            User(
                email="giulia.bianchi@email.it",
                password_hash=hashed,
                full_name="Giulia Bianchi",
                phone="+39 340 2345678",
                bio="Backend engineer con focus su architetture distribuite e microservizi. Ex Amazon.",
                location="Roma",
                experience_level="senior",
                experience_years="6+ anni",
                current_role="Backend Engineer",
                skills_json=json.dumps(["Python", "FastAPI", "AWS", "Docker", "Kubernetes"]),
                availability_status="available",
                linkedin_url="https://linkedin.com/in/giulia-bianchi",
                github_url="https://github.com/giuliabianchi",
                user_type="talent",
                ai_readiness_score=62,
                ai_readiness_level="advanced",
                is_public=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=25),
            ),
            User(
                email="luca.ferrari@email.it",
                password_hash=hashed,
                full_name="Luca Ferrari",
                phone="+39 347 3456789",
                bio="Full stack developer con background in startup. Amo costruire prodotti da zero.",
                location="Torino",
                experience_level="mid",
                experience_years="3-4 anni",
                current_role="Full Stack Developer",
                skills_json=json.dumps(["React", "Node.js", "PostgreSQL", "MongoDB", "Docker"]),
                availability_status="available",
                github_url="https://github.com/lucaferrari",
                user_type="talent",
                ai_readiness_score=44,
                ai_readiness_level="intermediate",
                is_public=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=20),
            ),
            User(
                email="sara.romano@email.it",
                password_hash=hashed,
                full_name="Sara Romano",
                bio="Data scientist in transizione verso ML engineering. Appassionata di NLP e LLM.",
                location="Milano",
                experience_level="mid",
                experience_years="3-4 anni",
                current_role="Data Scientist",
                skills_json=json.dumps(["Python", "PyTorch", "TensorFlow", "SQL", "Pandas"]),
                availability_status="reskilling",
                reskilling_status="in_progress",
                user_type="talent",
                ai_readiness_score=19,
                ai_readiness_level="beginner",
                is_public=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=18),
            ),
            User(
                email="andrea.conti@email.it",
                password_hash=hashed,
                full_name="Andrea Conti",
                phone="+39 335 5678901",
                bio="DevOps engineer con esperienza in ambienti enterprise. Certificato AWS Solutions Architect.",
                location="Bologna",
                experience_level="senior",
                experience_years="5+ anni",
                current_role="DevOps Engineer",
                skills_json=json.dumps(["Kubernetes", "Terraform", "AWS", "CI/CD", "Linux"]),
                availability_status="employed",
                user_type="talent",
                ai_readiness_score=72,
                ai_readiness_level="advanced",
                is_public=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=15),
            ),
            User(
                email="chiara.moretti@email.it",
                password_hash=hashed,
                full_name="Chiara Moretti",
                bio="Mobile developer specializzata in React Native. Due app in top 100 su App Store Italia.",
                location="Firenze",
                experience_level="mid",
                experience_years="3-4 anni",
                current_role="Mobile Developer",
                skills_json=json.dumps(["React Native", "TypeScript", "iOS", "Android", "Firebase"]),
                availability_status="available",
                user_type="talent",
                is_public=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=12),
            ),
            User(
                email="matteo.ricci@email.it",
                password_hash=hashed,
                full_name="Matteo Ricci",
                phone="+39 339 7890123",
                bio="Data engineer con esperienza in pipeline ETL su larga scala. Ex consultant Deloitte.",
                location="Milano",
                experience_level="senior",
                experience_years="4+ anni",
                current_role="Data Engineer",
                skills_json=json.dumps(["Python", "Apache Spark", "Airflow", "SQL", "dbt"]),
                availability_status="available",
                user_type="talent",
                is_public=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=10),
            ),
            User(
                email="elena.colombo@email.it",
                password_hash=hashed,
                full_name="Elena Colombo",
                bio="Frontend developer Vue.js con passione per l'accessibilita' web e il design system.",
                location="Napoli",
                experience_level="mid",
                experience_years="2-3 anni",
                current_role="Frontend Developer",
                skills_json=json.dumps(["Vue.js", "JavaScript", "Sass", "Figma", "Storybook"]),
                availability_status="available",
                user_type="talent",
                is_public=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=8),
            ),
            User(
                email="davide.gallo@email.it",
                password_hash=hashed,
                full_name="Davide Gallo",
                phone="+39 342 9012345",
                bio="Cybersecurity analyst con background in ethical hacking. Certificato OSCP e CEH.",
                location="Roma",
                experience_level="mid",
                experience_years="3-4 anni",
                current_role="Security Analyst",
                skills_json=json.dumps(["Cybersecurity", "Penetration Testing", "SIEM", "Cloud Security"]),
                availability_status="available",
                user_type="talent",
                is_public=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            User(
                email="francesca.bruno@email.it",
                password_hash=hashed,
                full_name="Francesca Bruno",
                bio="Tech lead con esperienza in architetture a microservizi. Mentore in community tech italiane.",
                location="Milano",
                experience_level="senior",
                experience_years="7+ anni",
                current_role="Tech Lead",
                skills_json=json.dumps(["Go", "gRPC", "Kubernetes", "Microservices", "System Design"]),
                availability_status="employed",
                user_type="talent",
                is_public=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=3),
            ),
        ]

        db.add_all(users)
        db.commit()
        print(f"Seeded {len(users)} users successfully.")

        # Fetch job IDs if not provided
        if not job_ids:
            all_jobs = db.query(Job).all()
            job_ids = [j.id for j in all_jobs]

        if not job_ids:
            print("No jobs found, skipping application seeding.")
            return

        # Fetch user IDs
        all_users = db.query(User).all()

        # Create some applications (4 users with 1-2 applications each)
        applications = [
            # Marco Rossi -> Senior Frontend Developer (job 0)
            Application(
                user_id=all_users[0].id,
                job_id=job_ids[0],
                status="attiva",
                status_detail="In valutazione",
                recruiter_name="Laura Verdi",
                recruiter_role="HR Manager - TechFlow Italia",
                applied_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            # Marco Rossi -> Full Stack Developer (job 2)
            Application(
                user_id=all_users[0].id,
                job_id=job_ids[2],
                status="archiviata",
                status_detail="Posizione chiusa",
                applied_at=datetime.now(timezone.utc) - timedelta(days=15),
            ),
            # Giulia Bianchi -> Backend Engineer Python (job 1)
            Application(
                user_id=all_users[1].id,
                job_id=job_ids[1],
                status="attiva",
                status_detail="Colloquio tecnico schedulato",
                recruiter_name="Paolo Neri",
                recruiter_role="CTO - DataSphere",
                applied_at=datetime.now(timezone.utc) - timedelta(days=3),
            ),
            # Luca Ferrari -> Full Stack Developer (job 2)
            Application(
                user_id=all_users[2].id,
                job_id=job_ids[2],
                status="da_completare",
                status_detail="Questionario tecnico da completare",
                applied_at=datetime.now(timezone.utc) - timedelta(days=7),
            ),
            # Chiara Moretti -> Mobile Developer React Native (job 5)
            Application(
                user_id=all_users[5].id,
                job_id=job_ids[5],
                status="proposta",
                status_detail="Proposta ricevuta dall'azienda",
                recruiter_name="Alessia Martini",
                recruiter_role="Talent Acquisition - AppFactory",
                applied_at=datetime.now(timezone.utc) - timedelta(days=2),
            ),
            # Davide Gallo -> Cybersecurity Analyst (job 8)
            Application(
                user_id=all_users[8].id,
                job_id=job_ids[8],
                status="attiva",
                status_detail="In valutazione",
                recruiter_name="Marco Rossi",
                recruiter_role="Security Director - SecureNet Italia",
                applied_at=datetime.now(timezone.utc) - timedelta(days=4),
            ),
        ]

        db.add_all(applications)
        db.commit()
        print(f"Seeded {len(applications)} applications successfully.")
    finally:
        db.close()


def seed_news():
    """Seed the database with 10 real news items from Hacker News and TLDR Tech."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Drop and re-create for fresh seed
        db.query(News).delete()
        db.commit()

        news_items = [
            # --- Hacker News (verified real articles, Feb 2026) ---
            News(
                title="Firefox 148: protezione XSS con la nuova Sanitizer API",
                summary="Firefox 148 e' il primo browser a implementare la Sanitizer API standardizzata, che aiuta gli sviluppatori a prevenire attacchi cross-site scripting (XSS). Il nuovo metodo setHTML() offre un'alternativa piu' semplice e sicura rispetto all'uso error-prone di innerHTML.",
                source="Mozilla Hacks",
                source_url="https://hacks.mozilla.org/2026/02/goodbye-innerhtml-hello-sethtml-stronger-xss-protection-in-firefox-148/",
                category="tech",
                tags_json=json.dumps(["Firefox", "Web Security", "XSS", "Browser"]),
                author="Tom Schuster",
                published_at=datetime.now(timezone.utc) - timedelta(hours=6),
            ),
            News(
                title="Stripe raggiunge una valutazione di 159 miliardi di dollari",
                summary="Stripe ha annunciato una valutazione di 159 miliardi di dollari tramite un'offerta pubblica. Le aziende sulla piattaforma Stripe hanno generato 1,9 trilioni di dollari in volume, un aumento del 34% anno su anno, e la suite Revenue ha raggiunto un miliardo di dollari di run rate annuale.",
                source="Stripe Newsroom",
                source_url="https://stripe.com/newsroom/news/stripe-2025-update",
                category="tech",
                tags_json=json.dumps(["Fintech", "Stripe", "Valuation", "Payments"]),
                author="Stripe",
                published_at=datetime.now(timezone.utc) - timedelta(hours=12),
            ),
            News(
                title="Diode: progetta, programma e simula hardware nel browser",
                summary="Diode e' una piattaforma browser-based che permette di progettare e testare circuiti elettronici senza componenti fisici. Un'esperienza di laboratorio virtuale con accesso a componenti come resistori, condensatori, transistor e LED per prototipare progetti hardware online.",
                source="Hacker News",
                source_url="https://www.withdiode.com/",
                category="tech",
                tags_json=json.dumps(["Hardware", "Simulation", "Electronics", "Maker"]),
                author="WithDiode",
                published_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
            News(
                title="Lettera aperta a Google sulla registrazione obbligatoria degli sviluppatori",
                summary="Una lettera aperta firmata da 37 organizzazioni, tra cui EFF e Free Software Foundation, si oppone alla policy di Google che richiede a tutti gli sviluppatori Android di registrarsi con Google per distribuire app fuori dal Play Store. La registrazione obbligatoria crea barriere all'innovazione.",
                source="Keep Android Open",
                source_url="https://keepandroidopen.org/open-letter/",
                category="tech",
                tags_json=json.dumps(["Android", "Google", "Open Source", "Privacy"]),
                author="EFF & FSF Coalition",
                published_at=datetime.now(timezone.utc) - timedelta(days=1, hours=5),
            ),
            News(
                title="Il piu' grande data breach della storia USA: 190 milioni di americani esposti",
                summary="L'attacco informatico a Change Healthcare ha esposto i dati sanitari e assicurativi di circa 190 milioni di americani. Gli aggressori hanno sfruttato un portale Citrix privo di autenticazione multifattore per infiltrarsi nei sistemi di UnitedHealth Group.",
                source="Morning Overview",
                source_url="https://morningoverview.com/massive-federal-data-breach-may-be-the-biggest-hack-in-us-history/",
                category="tech",
                tags_json=json.dumps(["Cybersecurity", "Data Breach", "Healthcare", "Hacking"]),
                author="Cassian Holt",
                published_at=datetime.now(timezone.utc) - timedelta(days=2),
            ),
            # --- TLDR Tech (verified real articles, Feb 2026) ---
            News(
                title="OpenAI riuscira' a costruire Alexa prima che Amazon costruisca ChatGPT?",
                summary="Un'analisi sulla partnership di OpenAI con il team di design LoveFrom di Jony Ive per sviluppare uno smart speaker competitivo. Il dispositivo in arrivo, con un prezzo tra 200 e 300 dollari e capacita' fotografiche, potrebbe ridefinire il mercato della smart home.",
                source="TLDR Tech",
                source_url="https://spyglass.org/openai-smart-speaker/",
                category="AI",
                tags_json=json.dumps(["OpenAI", "Smart Speaker", "Amazon", "Hardware"]),
                author="M.G. Siegler",
                published_at=datetime.now(timezone.utc) - timedelta(days=2, hours=10),
            ),
            News(
                title="Code Mode: dai agli agenti AI un'intera API in 1.000 token",
                summary="Cloudflare ha introdotto Code Mode, una tecnica che comprime l'accesso all'intera API di Cloudflare (oltre 2.500 endpoint) in soli due tool che consumano circa 1.000 token. Invece di elencare ogni operazione API, gli agenti scrivono codice JavaScript contro un SDK tipizzato.",
                source="TLDR Tech",
                source_url="https://blog.cloudflare.com/code-mode-mcp/",
                category="AI",
                tags_json=json.dumps(["Cloudflare", "MCP", "AI Agents", "API"]),
                author="Matt Carey",
                published_at=datetime.now(timezone.utc) - timedelta(days=3),
            ),
            News(
                title="Smettila di pensare all'AI come un collega. E' un esoscheletro.",
                summary="Le organizzazioni che vedono l'AI come agenti autonomi spesso rimangono deluse, mentre quelle che la trattano come amplificatore di capacita' ottengono risultati migliori. Un framework dove gli strumenti AI potenziano il processo decisionale umano piuttosto che sostituirlo.",
                source="TLDR Tech",
                source_url="https://www.kasava.dev/blog/ai-as-exoskeleton",
                category="AI",
                tags_json=json.dumps(["AI Strategy", "Productivity", "Human-AI", "Management"]),
                author="Ben Gregory",
                published_at=datetime.now(timezone.utc) - timedelta(days=4),
            ),
            # --- TechCrunch (verified real articles, Feb 2026) ---
            News(
                title="Particle: l'app AI che ascolta i podcast per te ed estrae i momenti chiave",
                summary="Particle, un'applicazione di notizie alimentata dall'AI, ha introdotto una funzionalita' che estrae momenti significativi dai podcast e mostra clip audio rilevanti accanto alle notizie correlate. Accesso rapido ai segmenti pertinenti senza ascoltare interi episodi.",
                source="TechCrunch",
                source_url="https://techcrunch.com/2026/02/23/particles-ai-news-app-listens-to-podcasts-for-interesting-clips-so-you-you-dont-have-to/",
                category="AI",
                tags_json=json.dumps(["AI News", "Podcasts", "Startup", "Media"]),
                author="Sarah Perez",
                published_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            News(
                title="VP di Google avverte: due tipi di startup AI potrebbero non sopravvivere",
                summary="Secondo un VP di Google, due categorie di startup AI affrontano minacce esistenziali. I wrapper LLM e gli aggregatori AI stanno lottando con margini in calo e differenziazione limitata, mettendo in discussione la loro sostenibilita' a lungo termine nel mercato.",
                source="TechCrunch",
                source_url="https://techcrunch.com/2026/02/21/google-vp-warns-that-two-types-of-ai-startups-may-not-survive/",
                category="careers",
                tags_json=json.dumps(["AI Startups", "Google", "Venture Capital", "Market Trends"]),
                author="Rebecca Bellan",
                published_at=datetime.now(timezone.utc) - timedelta(days=6),
            ),
        ]

        db.add_all(news_items)
        db.commit()
        print(f"Seeded {len(news_items)} news items successfully.")
    finally:
        db.close()


def seed_courses():
    """Seed the database with 10 real courses from Coursera and Udemy."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Drop and re-create for fresh seed
        db.query(Course).delete()
        db.commit()

        courses = [
            # --- Coursera (all URLs verified via WebFetch, Feb 2026) ---
            Course(
                title="Machine Learning Specialization",
                description="Programma fondamentale di 3 corsi creato da Andrew Ng in collaborazione con Stanford University e DeepLearning.AI. Copre regressione, classificazione, sistemi di raccomandazione, apprendimento per rinforzo e le best practice del machine learning. Ideale per chi vuole iniziare una carriera nell'AI.",
                provider="Coursera",
                url="https://www.coursera.org/specializations/machine-learning-introduction",
                instructor="Andrew Ng",
                level="beginner",
                duration="3 mesi (~5 ore/settimana)",
                price="Gratis (audit)",
                rating="4.9",
                students_count=4800000,
                category="ML",
                tags_json=json.dumps(["Machine Learning", "Python", "Regression", "Neural Networks"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
            Course(
                title="Deep Learning Specialization",
                description="Specializzazione di 5 corsi che copre reti neurali, CNN, RNN, modelli sequenziali e le tecniche avanzate del deep learning. Insegna a costruire e addestrare architetture di deep learning con TensorFlow, preparando gli studenti allo sviluppo di applicazioni AI all'avanguardia.",
                provider="Coursera",
                url="https://www.coursera.org/specializations/deep-learning",
                instructor="Andrew Ng",
                level="intermediate",
                duration="5 mesi (~5 ore/settimana)",
                price="Gratis (audit)",
                rating="4.9",
                students_count=120000,
                category="AI",
                tags_json=json.dumps(["Deep Learning", "Neural Networks", "TensorFlow", "CNN"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=2),
            ),
            Course(
                title="Prompt Engineering for ChatGPT",
                description="Corso della Vanderbilt University che insegna a scrivere prompt efficaci per ChatGPT e altri modelli di linguaggio. Si parte dalle basi fino a tecniche sofisticate per risolvere problemi in qualsiasi dominio, inclusi scrittura, pianificazione, simulazione e programmazione.",
                provider="Coursera",
                url="https://www.coursera.org/learn/prompt-engineering",
                instructor="Dr. Jules White",
                level="beginner",
                duration="~18 ore",
                price="Gratis (audit)",
                rating="4.8",
                students_count=631907,
                category="AI",
                tags_json=json.dumps(["Prompt Engineering", "ChatGPT", "LLM", "Generative AI"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=3),
            ),
            Course(
                title="Generative AI with Large Language Models",
                description="Corso intermedio sviluppato da DeepLearning.AI e AWS che insegna i fondamenti dell'AI generativa e dei Large Language Models. Copre il ciclo di vita completo di un progetto LLM: scoping, selezione del modello, fine-tuning, ottimizzazione e deployment in applicazioni reali.",
                provider="Coursera",
                url="https://www.coursera.org/learn/generative-ai-with-llms",
                instructor="Chris Fregly",
                level="intermediate",
                duration="3 settimane (~16 ore)",
                price="Gratis (audit)",
                rating="4.8",
                students_count=427349,
                category="AI",
                tags_json=json.dumps(["LLM", "Generative AI", "Fine-tuning", "AWS"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=4),
            ),
            Course(
                title="AI For Everyone",
                description="Corso introduttivo di Andrew Ng pensato per un pubblico non tecnico che vuole capire l'intelligenza artificiale. Insegna il significato dei termini AI, come identificare opportunita' per applicare l'AI nella propria organizzazione e come costruire una strategia AI, affrontando anche le questioni etiche.",
                provider="Coursera",
                url="https://www.coursera.org/learn/ai-for-everyone",
                instructor="Andrew Ng",
                level="beginner",
                duration="~7 ore",
                price="Gratis (audit)",
                rating="4.8",
                students_count=2410000,
                category="AI",
                tags_json=json.dumps(["AI Fundamentals", "AI Strategy", "Non-Technical", "Business AI"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            # --- Udemy (verified real course slugs, Feb 2026) ---
            Course(
                title="Machine Learning A-Z: AI, Python & R + ChatGPT Prize [2026]",
                description="Corso bestseller con oltre 1 milione di studenti che copre machine learning supervisionato, non supervisionato e per rinforzo usando Python e R. Include implementazioni pratiche di regressione, classificazione, clustering, NLP e deep learning con esercizi hands-on.",
                provider="Udemy",
                url="https://www.udemy.com/course/machinelearning/",
                instructor="Kirill Eremenko, Hadelin de Ponteves",
                level="intermediate",
                duration="42,5 ore",
                price="\u20ac89.99",
                rating="4.5",
                students_count=1171036,
                category="ML",
                tags_json=json.dumps(["Machine Learning", "Python", "R", "Scikit-Learn"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=6),
            ),
            Course(
                title="Deep Learning A-Z 2026: Neural Networks, AI & ChatGPT Prize",
                description="Corso pratico che insegna a costruire reti neurali artificiali, convoluzionali e ricorrenti da zero. Copre ANN, CNN, RNN, Self-Organizing Maps, Boltzmann Machines e AutoEncoders con applicazioni reali come il riconoscimento di immagini e l'analisi di testo.",
                provider="Udemy",
                url="https://www.udemy.com/course/deeplearning/",
                instructor="Kirill Eremenko, Hadelin de Ponteves",
                level="intermediate",
                duration="22 ore",
                price="\u20ac89.99",
                rating="4.5",
                students_count=350000,
                category="AI",
                tags_json=json.dumps(["Deep Learning", "Neural Networks", "CNN", "RNN"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=7),
            ),
            Course(
                title="Python for Data Science and Machine Learning Bootcamp",
                description="Bootcamp completo che insegna ad usare Python per la data science e il machine learning. Copre NumPy, Pandas, Matplotlib, Seaborn, Plotly, Scikit-Learn, reti neurali con TensorFlow e tecniche di machine learning con progetti pratici su dataset reali.",
                provider="Udemy",
                url="https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/",
                instructor="Jose Portilla",
                level="beginner",
                duration="25 ore",
                price="\u20ac89.99",
                rating="4.6",
                students_count=803210,
                category="ML",
                tags_json=json.dumps(["Python", "Data Science", "Pandas", "Scikit-Learn"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=8),
            ),
            Course(
                title="AI Engineer Core Track: LLM Engineering, RAG, QLoRA, Agents",
                description="Percorso pratico di 8 settimane per diventare un LLM Engineer. Si costruiscono 8 applicazioni AI reali esplorando oltre 20 modelli, padroneggiando tecniche all'avanguardia come RAG, fine-tuning con QLoRA e sistemi multi-agente autonomi.",
                provider="Udemy",
                url="https://www.udemy.com/course/llm-engineering-master-ai-and-large-language-models/",
                instructor="Ed Donner",
                level="intermediate",
                duration="46 ore",
                price="\u20ac89.99",
                rating="4.7",
                students_count=50000,
                category="AI",
                tags_json=json.dumps(["LLM", "RAG", "QLoRA", "AI Agents"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=9),
            ),
            Course(
                title="Complete A.I. & Machine Learning, Data Science Bootcamp",
                description="Bootcamp completo che parte da zero e arriva fino al deep learning e TensorFlow 2.0. Copre l'intero workflow della data science: esplorazione dati, visualizzazione, ingegnerizzazione delle feature, addestramento modelli e deployment.",
                provider="Udemy",
                url="https://www.udemy.com/course/complete-machine-learning-and-data-science-zero-to-mastery/",
                instructor="Andrei Neagoie, Daniel Bourke",
                level="beginner",
                duration="44 ore",
                price="\u20ac89.99",
                rating="4.6",
                students_count=200000,
                category="ML",
                tags_json=json.dumps(["Data Science", "TensorFlow", "Python", "Machine Learning"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=10),
            ),
        ]

        db.add_all(courses)
        db.commit()
        print(f"Seeded {len(courses)} courses successfully.")
    finally:
        db.close()


def seed_experiences_and_educations():
    """Seed experiences and educations for the first 5 seed users."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Clean existing data
        db.query(Experience).delete()
        db.query(Education).delete()
        db.commit()

        # Fetch user IDs
        all_users = db.query(User).order_by(User.created_at.asc()).all()
        if len(all_users) < 5:
            print("Not enough users found, skipping experience/education seeding.")
            return

        # --- Marco Rossi (index 0) ---
        experiences = [
            Experience(
                user_id=all_users[0].id,
                title="Senior Frontend Developer",
                company="TechFlow Italia",
                employment_type="full-time",
                location="Milano",
                start_month=3,
                start_year=2022,
                is_current=1,
                description="Guido lo sviluppo frontend della piattaforma SaaS fintech. Architettura React/Next.js, code review, mentoring junior, ottimizzazione performance. Stack: React, Next.js, TypeScript, Tailwind CSS.",
                created_at=datetime.now(timezone.utc) - timedelta(days=30),
            ),
            Experience(
                user_id=all_users[0].id,
                title="Frontend Developer",
                company="WebStudio Milano",
                employment_type="full-time",
                location="Milano",
                start_month=6,
                start_year=2019,
                end_month=2,
                end_year=2022,
                is_current=0,
                description="Sviluppo di applicazioni web per clienti enterprise. Migrazione da jQuery a React, implementazione design system, integrazione API REST.",
                created_at=datetime.now(timezone.utc) - timedelta(days=30),
            ),
            Experience(
                user_id=all_users[0].id,
                title="Junior Developer",
                company="StartupXYZ",
                employment_type="full-time",
                location="Milano",
                start_month=9,
                start_year=2017,
                end_month=5,
                end_year=2019,
                is_current=0,
                description="Primo ruolo come sviluppatore. Sviluppo frontend con React e backend con Node.js. Partecipazione attiva a sprint planning e code review.",
                created_at=datetime.now(timezone.utc) - timedelta(days=30),
            ),
        ]

        educations = [
            Education(
                user_id=all_users[0].id,
                institution="Politecnico di Milano",
                degree="Laurea Magistrale",
                degree_type="master",
                field_of_study="Informatica",
                start_year=2015,
                end_year=2017,
                is_current=0,
                description="Tesi su ottimizzazione delle performance di Single Page Applications. Voto: 110/110 con lode.",
                created_at=datetime.now(timezone.utc) - timedelta(days=30),
            ),
            Education(
                user_id=all_users[0].id,
                institution="Universita' degli Studi di Milano",
                degree="Laurea Triennale",
                degree_type="bachelor",
                field_of_study="Ingegneria Informatica",
                start_year=2012,
                end_year=2015,
                is_current=0,
                description="Fondamenti di informatica, algoritmi, basi di dati e ingegneria del software. Voto: 105/110.",
                created_at=datetime.now(timezone.utc) - timedelta(days=30),
            ),
        ]

        # --- Giulia Bianchi (index 1) ---
        experiences += [
            Experience(
                user_id=all_users[1].id,
                title="Senior Backend Engineer",
                company="DataSphere",
                employment_type="full-time",
                location="Roma (Remote)",
                start_month=1,
                start_year=2021,
                is_current=1,
                description="Architettura e sviluppo di microservizi Python/FastAPI su AWS. Gestione infrastruttura Kubernetes, CI/CD pipeline, mentoring del team backend.",
                created_at=datetime.now(timezone.utc) - timedelta(days=25),
            ),
            Experience(
                user_id=all_users[1].id,
                title="Software Development Engineer",
                company="Amazon",
                employment_type="full-time",
                location="Dublino, Irlanda",
                start_month=3,
                start_year=2018,
                end_month=12,
                end_year=2020,
                is_current=0,
                description="Sviluppo di servizi backend per AWS Marketplace. Architetture distribuite, DynamoDB, Lambda, SQS. On-call rotation e operational excellence.",
                created_at=datetime.now(timezone.utc) - timedelta(days=25),
            ),
            Experience(
                user_id=all_users[1].id,
                title="Backend Developer",
                company="Accenture Italia",
                employment_type="full-time",
                location="Roma",
                start_month=9,
                start_year=2016,
                end_month=2,
                end_year=2018,
                is_current=0,
                description="Sviluppo backend per progetti enterprise nel settore bancario. Java Spring Boot, Oracle DB, integrazione sistemi legacy.",
                created_at=datetime.now(timezone.utc) - timedelta(days=25),
            ),
        ]

        educations += [
            Education(
                user_id=all_users[1].id,
                institution="Universita' La Sapienza",
                degree="Laurea Magistrale",
                degree_type="master",
                field_of_study="Ingegneria Informatica",
                start_year=2014,
                end_year=2016,
                is_current=0,
                description="Specializzazione in sistemi distribuiti e cloud computing. Tesi su architetture event-driven. Voto: 110/110 con lode.",
                created_at=datetime.now(timezone.utc) - timedelta(days=25),
            ),
            Education(
                user_id=all_users[1].id,
                institution="Universita' La Sapienza",
                degree="Laurea Triennale",
                degree_type="bachelor",
                field_of_study="Informatica",
                start_year=2011,
                end_year=2014,
                is_current=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=25),
            ),
        ]

        # --- Luca Ferrari (index 2) ---
        experiences += [
            Experience(
                user_id=all_users[2].id,
                title="Full Stack Developer",
                company="InnovaHub",
                employment_type="full-time",
                location="Torino",
                start_month=4,
                start_year=2021,
                is_current=1,
                description="Sviluppo full stack di applicazioni web con React e Node.js. Progettazione database, API REST, deployment su AWS. Team agile di 6 persone.",
                created_at=datetime.now(timezone.utc) - timedelta(days=20),
            ),
            Experience(
                user_id=all_users[2].id,
                title="Junior Full Stack Developer",
                company="Digital Garage Torino",
                employment_type="full-time",
                location="Torino",
                start_month=10,
                start_year=2019,
                end_month=3,
                end_year=2021,
                is_current=0,
                description="Sviluppo di MVP per startup early-stage. React, Express.js, MongoDB. Coinvolto in tutte le fasi del prodotto dalla progettazione al lancio.",
                created_at=datetime.now(timezone.utc) - timedelta(days=20),
            ),
        ]

        educations += [
            Education(
                user_id=all_users[2].id,
                institution="Politecnico di Torino",
                degree="Laurea Triennale",
                degree_type="bachelor",
                field_of_study="Ingegneria Informatica",
                start_year=2016,
                end_year=2019,
                is_current=0,
                description="Progetto finale su sviluppo di applicazioni web progressive (PWA). Voto: 100/110.",
                created_at=datetime.now(timezone.utc) - timedelta(days=20),
            ),
        ]

        # --- Sara Romano (index 3) ---
        experiences += [
            Experience(
                user_id=all_users[3].id,
                title="Data Scientist",
                company="AI Lab Milano",
                employment_type="full-time",
                location="Milano",
                start_month=2,
                start_year=2021,
                is_current=1,
                description="Sviluppo modelli NLP per analisi del sentiment e classificazione testi. Pipeline ML con PyTorch, MLflow per experiment tracking. In transizione verso ML engineering.",
                created_at=datetime.now(timezone.utc) - timedelta(days=18),
            ),
            Experience(
                user_id=all_users[3].id,
                title="Data Analyst",
                company="ConsultingTech",
                employment_type="full-time",
                location="Milano",
                start_month=7,
                start_year=2019,
                end_month=1,
                end_year=2021,
                is_current=0,
                description="Analisi dati per clienti enterprise. Dashboard con Tableau, query SQL complesse, reporting automatizzato con Python.",
                created_at=datetime.now(timezone.utc) - timedelta(days=18),
            ),
        ]

        educations += [
            Education(
                user_id=all_users[3].id,
                institution="Universita' degli Studi di Milano-Bicocca",
                degree="Laurea Magistrale",
                degree_type="master",
                field_of_study="Data Science",
                start_year=2017,
                end_year=2019,
                is_current=0,
                description="Specializzazione in machine learning e statistica applicata. Tesi su modelli NLP per l'italiano.",
                created_at=datetime.now(timezone.utc) - timedelta(days=18),
            ),
        ]

        # --- Andrea Conti (index 4) ---
        experiences += [
            Experience(
                user_id=all_users[4].id,
                title="Senior DevOps Engineer",
                company="CloudBase",
                employment_type="full-time",
                location="Bologna (Hybrid)",
                start_month=5,
                start_year=2020,
                is_current=1,
                description="Gestione infrastruttura cloud multi-account AWS. Kubernetes cluster management, Terraform IaC, CI/CD con GitHub Actions. Certificato AWS Solutions Architect Professional.",
                created_at=datetime.now(timezone.utc) - timedelta(days=15),
            ),
            Experience(
                user_id=all_users[4].id,
                title="DevOps Engineer",
                company="Enterprise Solutions Srl",
                employment_type="full-time",
                location="Bologna",
                start_month=3,
                start_year=2018,
                end_month=4,
                end_year=2020,
                is_current=0,
                description="Migrazione da on-premise a cloud AWS. Setup pipeline CI/CD con Jenkins, containerizzazione con Docker, monitoring con Prometheus e Grafana.",
                created_at=datetime.now(timezone.utc) - timedelta(days=15),
            ),
            Experience(
                user_id=all_users[4].id,
                title="System Administrator",
                company="IT Services Bologna",
                employment_type="full-time",
                location="Bologna",
                start_month=6,
                start_year=2016,
                end_month=2,
                end_year=2018,
                is_current=0,
                description="Amministrazione sistemi Linux, gestione server, networking. Primi passi nell'automazione con Ansible e scripting Bash.",
                created_at=datetime.now(timezone.utc) - timedelta(days=15),
            ),
        ]

        educations += [
            Education(
                user_id=all_users[4].id,
                institution="Universita' di Bologna",
                degree="Laurea Magistrale",
                degree_type="master",
                field_of_study="Ingegneria Informatica",
                start_year=2014,
                end_year=2016,
                is_current=0,
                description="Specializzazione in sistemi e reti. Tesi su automazione infrastrutturale con approccio Infrastructure as Code.",
                created_at=datetime.now(timezone.utc) - timedelta(days=15),
            ),
            Education(
                user_id=all_users[4].id,
                institution="Universita' di Bologna",
                degree="Laurea Triennale",
                degree_type="bachelor",
                field_of_study="Informatica",
                start_year=2011,
                end_year=2014,
                is_current=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=15),
            ),
        ]

        db.add_all(experiences)
        db.add_all(educations)
        db.commit()
        print(f"Seeded {len(experiences)} experiences and {len(educations)} educations successfully.")
    finally:
        db.close()


def seed_companies_and_proposals():
    """Seed 3 company users and 4 proposals linking companies to talents with courses, milestones, and messages."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Clean existing data
        db.query(ProposalMessage).delete()
        db.query(ProposalMilestone).delete()
        db.query(ProposalCourse).delete()
        db.query(Proposal).delete()
        db.commit()

        hashed = hash_password("password123")

        company_users = [
            User(
                email="hr@techflow.it",
                password_hash=hashed,
                full_name="Laura Verdi",
                phone="+39 02 1234567",
                bio="HR Manager presso TechFlow Italia. Cerchiamo talenti per il nostro team di sviluppo.",
                location="Milano",
                user_type="company",
                company_name="TechFlow Italia",
                company_website="https://techflow.it",
                company_size="51-200",
                industry="Software & Technology",
                is_active=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=60),
            ),
            User(
                email="info@aisolutions.it",
                password_hash=hashed,
                full_name="Roberto Mancini",
                phone="+39 06 2345678",
                bio="CEO di AI Solutions Srl. Startup specializzata in soluzioni AI per il settore enterprise.",
                location="Roma",
                user_type="company",
                company_name="AI Solutions Srl",
                company_website="https://aisolutions.it",
                company_size="11-50",
                industry="Artificial Intelligence",
                is_active=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=45),
            ),
            User(
                email="recruiting@datasphere.it",
                password_hash=hashed,
                full_name="Paolo Neri",
                phone="+39 051 3456789",
                bio="Head of Recruiting presso DataSphere. Costruiamo il futuro dei dati in Italia.",
                location="Bologna",
                user_type="company",
                company_name="DataSphere",
                company_website="https://datasphere.it",
                company_size="201-500",
                industry="Data & Analytics",
                is_active=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=30),
            ),
        ]

        db.add_all(company_users)
        db.commit()
        print(f"Seeded {len(company_users)} company users successfully.")

        # Fetch talent users and courses for proposals
        talents = db.query(User).filter(User.user_type == "talent", User.is_public == 1).order_by(User.created_at.asc()).all()
        courses = db.query(Course).filter(Course.is_active == 1).order_by(Course.created_at.asc()).all()

        if len(talents) < 4 or len(courses) < 8:
            print("Not enough talents or courses found, skipping proposal seeding.")
            return

        # Proposal 1: TechFlow Italia -> Marco Rossi (talent[0]) with 3 AI courses (accepted, 1 completed)
        proposal1 = Proposal(
            company_id=company_users[0].id,
            talent_id=talents[0].id,
            status="accepted",
            message="Ciao Marco, siamo interessati al tuo profilo frontend. Ti proponiamo un percorso di formazione AI per integrarti nel nostro team che lavora su prodotti AI-driven.",
            budget_range="5000-8000",
            total_xp=235,
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
        db.add(proposal1)
        db.flush()

        pc1_courses = [
            ProposalCourse(
                proposal_id=proposal1.id, course_id=courses[0].id, order=0,
                is_completed=1, completed_at=datetime.now(timezone.utc) - timedelta(days=3),
                started_at=datetime.now(timezone.utc) - timedelta(days=8),
                xp_earned=200,
                company_notes="Inizia da qui, e' il corso fondamentale.",
                deadline=datetime.now(timezone.utc) + timedelta(days=20),
            ),
            ProposalCourse(
                proposal_id=proposal1.id, course_id=courses[1].id, order=1,
                is_completed=0,
                started_at=datetime.now(timezone.utc) - timedelta(days=1),
                company_notes="Secondo passo, dopo aver completato il primo.",
                deadline=datetime.now(timezone.utc) + timedelta(days=30),
            ),
            ProposalCourse(
                proposal_id=proposal1.id, course_id=courses[3].id, order=2,
                is_completed=0,
                deadline=datetime.now(timezone.utc) + timedelta(days=45),
            ),
        ]
        db.add_all(pc1_courses)

        # Milestones for proposal 1
        milestones1 = [
            ProposalMilestone(
                proposal_id=proposal1.id, milestone_type="first_course",
                title="Primo corso iniziato!",
                description="Bonus per aver iniziato il percorso formativo",
                xp_reward=25,
                achieved_at=datetime.now(timezone.utc) - timedelta(days=8),
            ),
            ProposalMilestone(
                proposal_id=proposal1.id, milestone_type="course_started",
                title="Corso iniziato",
                xp_reward=10,
                achieved_at=datetime.now(timezone.utc) - timedelta(days=8),
            ),
            ProposalMilestone(
                proposal_id=proposal1.id, milestone_type="course_completed",
                title="Corso completato: " + courses[0].title,
                xp_reward=200,
                achieved_at=datetime.now(timezone.utc) - timedelta(days=3),
            ),
        ]
        db.add_all(milestones1)

        # Proposal 2: AI Solutions Srl -> Giulia Bianchi (talent[1]) with 2 ML courses (accepted)
        proposal2 = Proposal(
            company_id=company_users[1].id,
            talent_id=talents[1].id,
            status="accepted",
            message="Buongiorno Giulia, il tuo profilo di backend engineer e' perfetto per noi. Ecco un percorso formativo personalizzato.",
            budget_range="3000-5000",
            total_xp=0,
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
        )
        db.add(proposal2)
        db.flush()

        pc2_courses = [
            ProposalCourse(proposal_id=proposal2.id, course_id=courses[2].id, order=0, is_completed=0),
            ProposalCourse(proposal_id=proposal2.id, course_id=courses[4].id, order=1, is_completed=0),
        ]
        db.add_all(pc2_courses)

        # Proposal 3: DataSphere -> Luca Ferrari (talent[2]) with 2 courses (sent)
        proposal3 = Proposal(
            company_id=company_users[2].id,
            talent_id=talents[2].id,
            status="sent",
            message="Luca, la tua esperienza full stack e' impressionante. Vorremmo proporti un percorso per consolidare le tue competenze AI e unirti al nostro team dati.",
            budget_range="4000-6000",
            total_xp=0,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        db.add(proposal3)
        db.flush()

        pc3_courses = [
            ProposalCourse(proposal_id=proposal3.id, course_id=courses[6].id, order=0, is_completed=0),
            ProposalCourse(proposal_id=proposal3.id, course_id=courses[7].id, order=1, is_completed=0),
        ]
        db.add_all(pc3_courses)

        # Proposal 4: DataSphere -> Sara Romano (talent[3]) - HIRED
        proposal4 = Proposal(
            company_id=company_users[2].id,
            talent_id=talents[3].id,
            status="hired",
            message="Sara, il tuo percorso formativo e' stato eccellente. Siamo lieti di offrirti una posizione nel nostro team.",
            budget_range="6000-10000",
            total_xp=650,
            hired_at=datetime.now(timezone.utc) - timedelta(days=1),
            hiring_notes="Sara ha completato brillantemente il percorso formativo. Assunta come ML Engineer.",
            created_at=datetime.now(timezone.utc) - timedelta(days=20),
        )
        db.add(proposal4)
        db.flush()

        pc4_courses = [
            ProposalCourse(
                proposal_id=proposal4.id, course_id=courses[2].id, order=0,
                is_completed=1, completed_at=datetime.now(timezone.utc) - timedelta(days=10),
                started_at=datetime.now(timezone.utc) - timedelta(days=18),
                xp_earned=200,
            ),
            ProposalCourse(
                proposal_id=proposal4.id, course_id=courses[4].id, order=1,
                is_completed=1, completed_at=datetime.now(timezone.utc) - timedelta(days=5),
                started_at=datetime.now(timezone.utc) - timedelta(days=9),
                xp_earned=300,
            ),
        ]
        db.add_all(pc4_courses)

        # Milestones for proposal 4
        milestones4 = [
            ProposalMilestone(
                proposal_id=proposal4.id, milestone_type="first_course",
                title="Primo corso iniziato!",
                description="Bonus per aver iniziato il percorso formativo",
                xp_reward=25,
                achieved_at=datetime.now(timezone.utc) - timedelta(days=18),
            ),
            ProposalMilestone(
                proposal_id=proposal4.id, milestone_type="course_completed",
                title="Corso completato: " + courses[2].title,
                xp_reward=200,
                achieved_at=datetime.now(timezone.utc) - timedelta(days=10),
            ),
            ProposalMilestone(
                proposal_id=proposal4.id, milestone_type="course_completed",
                title="Corso completato: " + courses[4].title,
                xp_reward=300,
                achieved_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            ProposalMilestone(
                proposal_id=proposal4.id, milestone_type="all_complete",
                title="Percorso completato al 100%",
                xp_reward=50,
                achieved_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
        ]
        db.add_all(milestones4)

        # Update Sara Romano: hired by DataSphere
        sara = talents[3]
        sara.availability_status = "employed"
        sara.reskilling_status = "completed"
        sara.adopted_by_company = "DataSphere"

        # Messages between companies and talents
        messages = [
            ProposalMessage(
                proposal_id=proposal1.id,
                sender_id=company_users[0].id,
                content="Ciao Marco, come procede il primo corso? Se hai domande non esitare a scriverci.",
                created_at=datetime.now(timezone.utc) - timedelta(days=7),
            ),
            ProposalMessage(
                proposal_id=proposal1.id,
                sender_id=talents[0].id,
                content="Grazie Laura! Ho completato il primo modulo, molto interessante. Procedo con il secondo.",
                created_at=datetime.now(timezone.utc) - timedelta(days=6),
            ),
            ProposalMessage(
                proposal_id=proposal1.id,
                sender_id=company_users[0].id,
                content="Ottimo lavoro! Ti abbiamo aggiornato le note del corso con alcune risorse aggiuntive.",
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            ProposalMessage(
                proposal_id=proposal4.id,
                sender_id=company_users[2].id,
                content="Complimenti Sara per aver completato il percorso! Ti contatteremo presto per i prossimi step.",
                created_at=datetime.now(timezone.utc) - timedelta(days=3),
            ),
            ProposalMessage(
                proposal_id=proposal4.id,
                sender_id=talents[3].id,
                content="Grazie mille! Sono molto entusiasta di questa opportunita'.",
                created_at=datetime.now(timezone.utc) - timedelta(days=2),
            ),
        ]
        db.add_all(messages)

        db.commit()
        print("Seeded 4 proposals with courses, milestones, and messages successfully.")
    finally:
        db.close()


def seed_notification_preferences():
    """Seed notification preferences for all users (all enabled by default)."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.query(NotificationPreference).delete()
        db.commit()

        users = db.query(User).all()
        prefs = []
        for user in users:
            prefs.append(NotificationPreference(
                user_id=user.id,
                email_notifications=1,
                daily_digest=1,
                channel="email",
                telegram_chat_id=None,
                telegram_notifications=0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ))
        db.add_all(prefs)
        db.commit()
        print(f"Seeded {len(prefs)} notification preferences successfully.")
    finally:
        db.close()


def seed_email_logs():
    """Seed sample email log entries."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.query(EmailLog).delete()
        db.commit()

        # Fetch first talent (Marco Rossi) and first company (TechFlow Italia)
        talents = db.query(User).filter(User.user_type == "talent", User.is_public == 1).order_by(User.created_at.asc()).all()
        companies = db.query(User).filter(User.user_type == "company").order_by(User.created_at.asc()).all()
        proposals = db.query(Proposal).order_by(Proposal.created_at.asc()).all()

        if not talents or not companies:
            print("No users found, skipping email log seeding.")
            return

        talent = talents[0]  # Marco Rossi
        company = companies[0]  # TechFlow Italia (Laura Verdi)
        proposal = proposals[0] if proposals else None

        from api.services.email_service import _email_wrapper

        emails = [
            EmailLog(
                recipient_id=talent.id,
                recipient_email=talent.email,
                sender_label="Datapizza",
                email_type="proposal_received",
                subject=f"Nuova proposta formativa da {company.company_name or company.full_name}",
                body_html=_email_wrapper(
                    f"<h2 style='margin-top: 0;'>Hai ricevuto una nuova proposta!</h2>"
                    f"<p>Ciao <strong>{talent.full_name}</strong>,</p>"
                    f"<p><strong>{company.company_name}</strong> ti ha inviato una proposta formativa personalizzata.</p>"
                    f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
                ),
                body_text=f"Nuova proposta formativa da {company.company_name}.",
                related_proposal_id=proposal.id if proposal else None,
                is_read=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=9),
            ),
            EmailLog(
                recipient_id=company.id,
                recipient_email=company.email,
                sender_label="Datapizza",
                email_type="proposal_accepted",
                subject=f"{talent.full_name} ha accettato la tua proposta",
                body_html=_email_wrapper(
                    f"<h2 style='margin-top: 0;'>Proposta accettata!</h2>"
                    f"<p><strong>{talent.full_name}</strong> ha accettato la tua proposta formativa.</p>"
                    f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
                ),
                body_text=f"{talent.full_name} ha accettato la tua proposta.",
                related_proposal_id=proposal.id if proposal else None,
                is_read=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=8),
            ),
            EmailLog(
                recipient_id=company.id,
                recipient_email=company.email,
                sender_label="Datapizza",
                email_type="course_started",
                subject=f"{talent.full_name} ha iniziato il corso: Introduzione al Machine Learning",
                body_html=_email_wrapper(
                    f"<h2 style='margin-top: 0;'>Corso iniziato</h2>"
                    f"<p><strong>{talent.full_name}</strong> ha iniziato un nuovo corso nel percorso formativo.</p>"
                    f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
                ),
                body_text=f"{talent.full_name} ha iniziato il corso.",
                related_proposal_id=proposal.id if proposal else None,
                is_read=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=7),
            ),
            EmailLog(
                recipient_id=talent.id,
                recipient_email=talent.email,
                sender_label="Datapizza",
                email_type="daily_digest",
                subject="Il tuo digest giornaliero — Datapizza",
                body_html=_email_wrapper(
                    f"<h2 style='margin-top: 0;'>Buongiorno {talent.full_name}!</h2>"
                    f"<p>Ecco il tuo digest giornaliero con suggerimenti personalizzati.</p>"
                    f"<h3>Corsi in evidenza</h3>"
                    f"<ul><li><strong>AI Fundamentals</strong> (Coursera) — Livello: beginner</li></ul>"
                    f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
                ),
                body_text=f"Digest giornaliero per {talent.full_name}.",
                is_read=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
            EmailLog(
                recipient_id=talent.id,
                recipient_email=talent.email,
                sender_label="Datapizza",
                email_type="milestone_reached",
                subject="Traguardo raggiunto! +200 XP",
                body_html=_email_wrapper(
                    f"<h2 style='margin-top: 0;'>Congratulazioni!</h2>"
                    f"<p>Ciao <strong>{talent.full_name}</strong>,</p>"
                    f"<p>Hai raggiunto un nuovo traguardo: <strong>course_completed</strong></p>"
                    f"<p>Hai guadagnato <strong>+200 XP</strong>!</p>"
                    f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
                ),
                body_text="Traguardo raggiunto: course_completed. +200 XP",
                related_proposal_id=proposal.id if proposal else None,
                is_read=0,
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
        ]
        db.add_all(emails)
        db.commit()
        print(f"Seeded {len(emails)} email log entries successfully.")
    finally:
        db.close()


def seed_ai_readiness_assessments():
    """Seed AI readiness assessment rows for the first 5 talent users."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.query(AIReadinessAssessment).delete()
        db.commit()

        # Fetch first 5 talent users (ordered by created_at asc, matching seed order)
        talents = (
            db.query(User)
            .filter(User.user_type == "talent")
            .order_by(User.created_at.asc())
            .limit(5)
            .all()
        )

        if len(talents) < 5:
            print("Not enough talent users found, skipping AI readiness assessment seeding.")
            return

        # Realistic answer sets that produce the correct scores
        # Marco Rossi: score=84 -> raw=27 -> 27/32*100=84.375 rounds to 84 -> expert
        marco_answers = {
            "q1_ai_coding_assistants": 4,
            "q2_prompt_writing": 4,
            "q3_agentic_workflows": 3,
            "q4_ai_code_review": 4,
            "q5_ai_api_integration": 3,
            "q6_ai_output_evaluation": 3,
            "q7_rag_systems": 3,
            "q8_prompt_engineering": 3,
        }

        # Giulia Bianchi: score=62 -> raw=20 -> 20/32*100=62.5 rounds to 62 -> advanced
        giulia_answers = {
            "q1_ai_coding_assistants": 3,
            "q2_prompt_writing": 3,
            "q3_agentic_workflows": 2,
            "q4_ai_code_review": 3,
            "q5_ai_api_integration": 3,
            "q6_ai_output_evaluation": 2,
            "q7_rag_systems": 2,
            "q8_prompt_engineering": 2,
        }

        # Luca Ferrari: score=44 -> raw=14 -> 14/32*100=43.75 rounds to 44 -> intermediate
        luca_answers = {
            "q1_ai_coding_assistants": 2,
            "q2_prompt_writing": 2,
            "q3_agentic_workflows": 1,
            "q4_ai_code_review": 2,
            "q5_ai_api_integration": 2,
            "q6_ai_output_evaluation": 1,
            "q7_rag_systems": 2,
            "q8_prompt_engineering": 2,
        }

        # Sara Romano: score=19 -> raw=6 -> 6/32*100=18.75 rounds to 19 -> beginner
        sara_answers = {
            "q1_ai_coding_assistants": 1,
            "q2_prompt_writing": 1,
            "q3_agentic_workflows": 0,
            "q4_ai_code_review": 1,
            "q5_ai_api_integration": 1,
            "q6_ai_output_evaluation": 1,
            "q7_rag_systems": 0,
            "q8_prompt_engineering": 1,
        }

        # Andrea Conti: score=72 -> raw=23 -> 23/32*100=71.875 rounds to 72 -> advanced
        andrea_answers = {
            "q1_ai_coding_assistants": 3,
            "q2_prompt_writing": 3,
            "q3_agentic_workflows": 3,
            "q4_ai_code_review": 3,
            "q5_ai_api_integration": 3,
            "q6_ai_output_evaluation": 2,
            "q7_rag_systems": 3,
            "q8_prompt_engineering": 3,
        }

        assessment_data = [
            (talents[0], marco_answers, 84, "expert"),
            (talents[1], giulia_answers, 62, "advanced"),
            (talents[2], luca_answers, 44, "intermediate"),
            (talents[3], sara_answers, 19, "beginner"),
            (talents[4], andrea_answers, 72, "advanced"),
        ]

        assessments = []
        for user, answers, score, level in assessment_data:
            assessments.append(AIReadinessAssessment(
                user_id=user.id,
                answers_json=json.dumps(answers),
                total_score=score,
                readiness_level=level,
                quiz_version=1,
                created_at=datetime.now(timezone.utc) - timedelta(days=2),
            ))

        db.add_all(assessments)
        db.commit()
        print(f"Seeded {len(assessments)} AI readiness assessments successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    job_ids = seed_jobs()
    seed_users(job_ids)
    seed_news()
    seed_courses()
    seed_experiences_and_educations()
    seed_companies_and_proposals()
    seed_notification_preferences()
    seed_email_logs()
    seed_ai_readiness_assessments()
