"""Seed script for ReviewBoost AI Firestore collections."""
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-95b844f06177"

def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    print(f"Connecting to Firestore with hardcoded project ID: {PROJECT_ID}")

    # 1. Seed QR Campaigns Collection
    campaigns_ref = db.collection("qr_campaigns")
    initial_campaigns = [
        {
            "campaign_id": "camp_001",
            "business_name": "Padaria & Café Bella Vista",
            "location_tag": "Mesa 05 / Balcão Principal",
            "qr_code_target_url": "https://g.page/r/bellavista-cafe/review",
            "scan_count": 142,
            "rating_goal": 4.8,
            "status": "active",
            "created_at": "2026-09-15T10:00:00Z"
        },
        {
            "campaign_id": "camp_002",
            "business_name": "Padaria & Café Bella Vista",
            "location_tag": "Recibo de Caixa Delivery",
            "qr_code_target_url": "https://g.page/r/bellavista-delivery/review",
            "scan_count": 89,
            "rating_goal": 4.9,
            "status": "active",
            "created_at": "2026-09-20T14:30:00Z"
        }
    ]

    for camp in initial_campaigns:
        campaigns_ref.document(camp["campaign_id"]).set(camp)
        print(f"Seeded campaign: {camp['campaign_id']} - {camp['location_tag']}")

    # 2. Seed Customer Reviews Collection
    reviews_ref = db.collection("customer_reviews")
    initial_reviews = [
        {
            "review_id": "rev_101",
            "author_name": "Carlos Silva",
            "rating": 5,
            "comment": "O atendimento foi rápido e o pão na chapa com café expresso é excelente!",
            "sentiment": "POSITIVE",
            "response_status": "RESPONDED",
            "generated_response": "Muito obrigado pelo carinho, Carlos! Ficamos muito felizes que gostou do nosso pão na chapa!",
            "created_at": "2026-10-01T09:15:00Z"
        },
        {
            "review_id": "rev_102",
            "author_name": "Mariana Oliveira",
            "rating": 2,
            "comment": "Demorou bastante para trazerem a conta no horário do almoço de sexta.",
            "sentiment": "NEGATIVE",
            "response_status": "PENDING",
            "generated_response": "",
            "created_at": "2026-10-02T12:45:00Z"
        },
        {
            "review_id": "rev_103",
            "author_name": "Roberto Costa",
            "rating": 5,
            "comment": "Ambiente super agradável e café de altíssima qualidade. Recomendo!",
            "sentiment": "POSITIVE",
            "response_status": "RESPONDED",
            "generated_response": "Agradecemos a recomendação, Roberto! Esperamos ver você de volta em breve!",
            "created_at": "2026-10-02T15:30:00Z"
        }
    ]

    for rev in initial_reviews:
        reviews_ref.document(rev["review_id"]).set(rev)
        print(f"Seeded review: {rev['review_id']} by {rev['author_name']}")

    print("\n✅ Firestore seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
