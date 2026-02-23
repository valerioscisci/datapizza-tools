from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from api.database.connection import SessionLocal, engine, Base
from api.database.models import Job


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
    db.close()


if __name__ == "__main__":
    seed_jobs()
