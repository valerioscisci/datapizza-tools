from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from api.database.connection import SessionLocal, engine, Base
from api.database.models import Job, User, Application
from api.auth import hash_password


def seed_jobs():
    """Seed the database with 10 fake job listings."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

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

    db.close()
    return job_ids


def seed_users(job_ids: list[str] | None = None):
    """Seed the database with 10 Italian developer profiles and some applications."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

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
        db.close()
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
    db.close()


if __name__ == "__main__":
    job_ids = seed_jobs()
    seed_users(job_ids)
