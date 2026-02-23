from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from api.database.connection import SessionLocal, engine, Base
from api.database.models import Job, User, Application, News, Course, Experience, Education
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
        # Clean existing data
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
            # --- Hacker News (real stories, real URLs) ---
            News(
                title="Introducing Claude Sonnet 4.6",
                summary="Anthropic ha rilasciato Claude Sonnet 4.6, un modello aggiornato con finestra di contesto da 1 milione di token e capacita' migliorate in coding e ragionamento. Il modello rappresenta un significativo passo avanti nella famiglia Claude 4.",
                source="TLDR Tech",
                source_url="https://www.anthropic.com/news/claude-sonnet-4-6",
                category="AI",
                tags_json=json.dumps(["AI", "LLM", "Anthropic", "Claude"]),
                author="TLDR Newsletter",
                published_at=datetime.now(timezone.utc) - timedelta(hours=6),
            ),
            News(
                title="Ladybird Browser adopts Rust",
                summary="Il browser Ladybird ha annunciato l'adozione di Rust come linguaggio principale per lo sviluppo. La decisione segna un importante cambiamento architetturale per il progetto open-source, che punta a costruire un browser web indipendente da zero.",
                source="Hacker News",
                source_url="https://news.ycombinator.com/item?id=47120899",
                category="tech",
                tags_json=json.dumps(["Rust", "Browser", "Open Source", "Web"]),
                author="adius",
                published_at=datetime.now(timezone.utc) - timedelta(hours=12),
            ),
            News(
                title="Repeating Prompts migliora le performance dei modelli AI",
                summary="Una ricerca dimostra che ripetere il prompt di input migliora le performance dei modelli AI piu' popolari senza aumentare il numero di token generati o la latenza. Una tecnica semplice ma efficace per ottenere risultati migliori dai LLM.",
                source="TLDR Tech",
                source_url="https://daoudclarke.net/2026/02/19/repeating-prompt",
                category="AI",
                tags_json=json.dumps(["AI", "Prompt Engineering", "LLM", "Research"]),
                author="TLDR Newsletter",
                published_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
            News(
                title="I sistemi AI agentici non falliscono improvvisamente - degradano nel tempo",
                summary="Un'analisi su CIO.com spiega come i sistemi AI agentici subiscano un degrado graduale delle performance che richiede monitoraggio continuo e tecniche di rilevamento del drift statistico. Un tema cruciale per chi deploya AI in produzione.",
                source="TLDR Tech",
                source_url="https://www.cio.com/article/4134051/",
                category="AI",
                tags_json=json.dumps(["AI", "Agentic AI", "MLOps", "Monitoring"]),
                author="TLDR Newsletter",
                published_at=datetime.now(timezone.utc) - timedelta(days=1, hours=5),
            ),
            News(
                title="Coding Agents nel febbraio 2026: stato dell'arte",
                summary="Un'analisi approfondita dei diversi coding agent disponibili nel 2026. I vari agenti eccellono in task differenti, e l'architettura e il sequencing dei progetti limitano sempre piu' la qualita' del prodotto finale. Una lettura essenziale per chi lavora con AI nel coding.",
                source="TLDR Tech",
                source_url="https://calv.info/agents-feb-2026",
                category="AI",
                tags_json=json.dumps(["AI", "Coding", "Agents", "Developer Tools"]),
                author="TLDR Newsletter",
                published_at=datetime.now(timezone.utc) - timedelta(days=2),
            ),
            News(
                title="Come lavora il team Codex di OpenAI sfruttando l'AI",
                summary="Un articolo dettagliato su come il team di engineering di OpenAI che sviluppa Codex opera con la velocita' di una startup trattando l'AI come un 'teammate di prima classe'. Uno sguardo dentro le pratiche di sviluppo AI-first.",
                source="TLDR Tech",
                source_url="https://newsletter.eng-leadership.com/p/how-openais-codex-team-works-and",
                category="careers",
                tags_json=json.dumps(["AI", "OpenAI", "Engineering", "Carriera"]),
                author="TLDR Newsletter",
                published_at=datetime.now(timezone.utc) - timedelta(days=2, hours=10),
            ),
            News(
                title="Timeframe: un e-paper dashboard familiare DIY",
                summary="Un progetto open-source che ha raccolto oltre 1300 punti su Hacker News. L'autore ha costruito Timeframe, un dashboard su display e-paper per la famiglia che mostra calendario, meteo e informazioni utili. Un esempio ispirante di hardware hacking casalingo.",
                source="Hacker News",
                source_url="https://news.ycombinator.com/item?id=47113728",
                category="tech",
                tags_json=json.dumps(["Hardware", "DIY", "E-Paper", "Open Source"]),
                author="saeedesmaili",
                published_at=datetime.now(timezone.utc) - timedelta(days=3),
            ),
            News(
                title="I data center AI adottano superconduttori ad alta temperatura",
                summary="Microsoft investe 75 milioni di dollari in superconduttori ad alta temperatura per migliorare l'efficienza energetica dei data center AI e ridurre le perdite di trasmissione dell'energia. Una tecnologia che potrebbe rivoluzionare l'infrastruttura AI.",
                source="TLDR Tech",
                source_url="https://spectrum.ieee.org/ai-data-centers-hts-superconductors",
                category="tech",
                tags_json=json.dumps(["AI", "Data Center", "Microsoft", "Energia"]),
                author="TLDR Newsletter",
                published_at=datetime.now(timezone.utc) - timedelta(days=4),
            ),
            News(
                title="Costruire una cultura di ingegneria AI d'elite nel 2026",
                summary="Un articolo su come costruire team di ingegneria AI efficaci nel 2026. La formula vincente combina contesto strutturato, rigore a livelli e team piu' piccoli per evitare che l'AI amplifichi i problemi esistenti invece di risolverli.",
                source="TLDR Tech",
                source_url="https://www.cjroth.com/blog/2026-02-18-building-an-elite-engineering-culture",
                category="careers",
                tags_json=json.dumps(["AI", "Engineering", "Team", "Carriera"]),
                author="TLDR Newsletter",
                published_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            News(
                title="Loops: un TikTok federato e open-source",
                summary="Loops e' una nuova piattaforma video federata e open-source che offre un'alternativa decentralizzata a TikTok. Il progetto ha raccolto oltre 500 punti su Hacker News, dimostrando il forte interesse della community per alternative open ai social media.",
                source="Hacker News",
                source_url="https://news.ycombinator.com/item?id=47113618",
                category="tech",
                tags_json=json.dumps(["Open Source", "Social Media", "Fediverse", "Video"]),
                author="Gooblebrai",
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
            # --- Coursera (verified real URLs) ---
            Course(
                title="Generative AI with Large Language Models",
                description="Impara come funziona l'AI generativa e come deployarla in applicazioni reali. Il corso copre il lifecycle dei LLM dalla raccolta dati al deployment, l'architettura transformer, fine-tuning e reinforcement learning. Include prompt engineering, RAG e laboratori pratici su AWS.",
                provider="Coursera",
                url="https://www.coursera.org/learn/generative-ai-with-llms",
                instructor="Chris Fregly",
                level="intermediate",
                duration="3 settimane (~16 ore)",
                price="Gratis (audit)",
                rating="4.8",
                students_count=427226,
                category="AI",
                tags_json=json.dumps(["LLM", "Generative AI", "Transformer", "AWS"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
            Course(
                title="AI For Everyone",
                description="Corso introduttivo all'intelligenza artificiale per professionisti non tecnici e leader aziendali. Spiega il significato della terminologia AI comune (reti neurali, machine learning, deep learning), le applicazioni realistiche e i limiti dell'AI, e come costruire una strategia AI in azienda.",
                provider="Coursera",
                url="https://www.coursera.org/learn/ai-for-everyone",
                instructor="Andrew Ng",
                level="beginner",
                duration="4 settimane (~7 ore)",
                price="Gratis (audit)",
                rating="4.8",
                students_count=2411058,
                category="AI",
                tags_json=json.dumps(["AI", "Business", "Strategy", "Non-Technical"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=2),
            ),
            Course(
                title="Deep Learning Specialization",
                description="Specializzazione in 5 corsi che copre le fondamenta del deep learning. Impara a costruire e addestrare reti neurali profonde, CNN per computer vision, RNN per sequenze, e modelli sequence-to-sequence. Include progetti hands-on con applicazioni reali.",
                provider="Coursera",
                url="https://www.coursera.org/specializations/deep-learning",
                instructor="Andrew Ng",
                level="intermediate",
                duration="5 mesi",
                price="Gratis (audit)",
                rating="4.9",
                students_count=920000,
                category="ML",
                tags_json=json.dumps(["Deep Learning", "Neural Networks", "CNN", "RNN"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=3),
            ),
            Course(
                title="Prompt Engineering for ChatGPT",
                description="Impara a padroneggiare i Large Language Models come ChatGPT con tecniche di prompt engineering. Copre prompt patterns, few-shot examples, e strategie avanzate. Applicazioni pratiche dal tutoring allo sviluppo software e cybersecurity. Oltre 631.000 studenti iscritti.",
                provider="Coursera",
                url="https://www.coursera.org/learn/prompt-engineering",
                instructor="Dr. Jules White",
                level="beginner",
                duration="~19 ore",
                price="Gratis (audit)",
                rating="4.8",
                students_count=631245,
                category="AI",
                tags_json=json.dumps(["Prompt Engineering", "ChatGPT", "LLM", "AI"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=4),
            ),
            Course(
                title="Machine Learning Engineering for Production (MLOps)",
                description="Specializzazione in MLOps che copre l'intero lifecycle di un progetto ML in produzione. Data pipelines, model training, deployment, monitoring e continuous training. Usa TensorFlow Extended (TFX) e Google Cloud Vertex AI.",
                provider="Coursera",
                url="https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops",
                instructor="Robert Crowe",
                level="advanced",
                duration="4 mesi",
                price="Gratis (audit)",
                rating="4.7",
                students_count=150000,
                category="ML",
                tags_json=json.dumps(["MLOps", "TFX", "Model Deployment", "ML Pipeline"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            # --- Udemy (verified real URLs from web search) ---
            Course(
                title="Machine Learning A-Z: AI, Python & R + ChatGPT Prize [2026]",
                description="Il corso di Machine Learning piu' popolare su Udemy con oltre 1 milione di studenti. Copre regressione, classificazione, clustering, deep learning e NLP con implementazioni pratiche in Python e R. Include bonus ChatGPT e progetti reali.",
                provider="Udemy",
                url="https://www.udemy.com/course/machinelearning/",
                instructor="Kirill Eremenko, Hadelin de Ponteves",
                level="beginner",
                duration="40+ ore",
                price="\u20ac49.99",
                rating="4.5",
                students_count=1000000,
                category="ML",
                tags_json=json.dumps(["Machine Learning", "Python", "R", "Deep Learning"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=6),
            ),
            Course(
                title="The AI Engineer Course 2026: Complete AI Engineer Bootcamp",
                description="Bootcamp completo per diventare AI Engineer. Copre l'intero pipeline di LLM engineering, dall'architettura transformer alle applicazioni in produzione. Include LangChain, RAG, vector databases e deployment. Oltre 204.000 studenti con badge Bestseller.",
                provider="Udemy",
                url="https://www.udemy.com/course/the-ai-engineer-course-complete-ai-engineer-bootcamp/",
                instructor="Ed Donner",
                level="intermediate",
                duration="35+ ore",
                price="\u20ac49.99",
                rating="4.7",
                students_count=204000,
                category="AI",
                tags_json=json.dumps(["AI Engineer", "LLM", "LangChain", "RAG"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=7),
            ),
            Course(
                title="LLM Engineering, RAG, & AI Agents Masterclass [2026]",
                description="Masterclass su LLM engineering che copre il pipeline completo: fondamenti LLM, LangChain, LlamaIndex, sistemi RAG, vector databases, prompt engineering e costruzione di AI agents. Oltre 110.000 studenti.",
                provider="Udemy",
                url="https://www.udemy.com/course/become-an-llm-agentic-ai-engineer-14-day-bootcamp-2025/",
                instructor="Ligency Team",
                level="intermediate",
                duration="35+ ore",
                price="\u20ac49.99",
                rating="4.6",
                students_count=110000,
                category="AI",
                tags_json=json.dumps(["LLM", "RAG", "AI Agents", "LangChain"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=8),
            ),
            Course(
                title="The Complete Prompt Engineering for AI Bootcamp (2026)",
                description="Bootcamp completo di prompt engineering per AI. Impara tecniche avanzate di prompting per ChatGPT, Claude, Gemini e altri LLM. Copre zero-shot, few-shot, chain-of-thought, e come costruire applicazioni basate su prompt.",
                provider="Udemy",
                url="https://www.udemy.com/course/prompt-engineering-for-ai/",
                instructor="Mike Taylor",
                level="beginner",
                duration="12+ ore",
                price="\u20ac39.99",
                rating="4.6",
                students_count=85000,
                category="AI",
                tags_json=json.dumps(["Prompt Engineering", "ChatGPT", "AI", "LLM"]),
                image_url=None,
                created_at=datetime.now(timezone.utc) - timedelta(days=9),
            ),
            Course(
                title="Complete A.I. & Machine Learning, Data Science Bootcamp",
                description="Bootcamp completo che copre Python, machine learning, deep learning e data science. Include progetti pratici con TensorFlow, PyTorch, Pandas e scikit-learn. Dalla regressione lineare alle reti neurali e ai modelli generativi.",
                provider="Udemy",
                url="https://www.udemy.com/course/complete-machine-learning-and-data-science-zero-to-mastery/",
                instructor="Andrei Neagoie, Daniel Bourke",
                level="beginner",
                duration="40+ ore",
                price="\u20ac49.99",
                rating="4.6",
                students_count=200000,
                category="ML",
                tags_json=json.dumps(["Python", "Machine Learning", "Data Science", "TensorFlow"]),
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


if __name__ == "__main__":
    job_ids = seed_jobs()
    seed_users(job_ids)
    seed_news()
    seed_courses()
    seed_experiences_and_educations()
