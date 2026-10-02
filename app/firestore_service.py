"""Firestore database service for ReviewBoost AI.
Hardcoded Project ID: qwiklabs-gcp-03-95b844f06177
"""
from typing import List, Dict, Any, Optional
from google.cloud import firestore

# IMPORTANT: Hardcoded Project ID string as required for Agent Platform deployment
PROJECT_ID = "qwiklabs-gcp-03-95b844f06177"


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded GCP Project ID."""
    return firestore.Client(project=PROJECT_ID)


def list_qr_campaigns() -> List[Dict[str, Any]]:
    """Retrieves all QR code review campaigns from Firestore.

    Returns:
        List of dictionaries containing campaign details (campaign_id, business_name, location_tag, scan_count, rating_goal, status, etc.).
    """
    db = get_firestore_client()
    docs = db.collection("qr_campaigns").stream()
    campaigns = []
    for doc in docs:
        data = doc.to_dict()
        data["doc_id"] = doc.id
        campaigns.append(data)
    return campaigns


def create_qr_campaign(
    campaign_id: str,
    business_name: str,
    location_tag: str,
    qr_code_target_url: str,
    rating_goal: float = 4.8
) -> str:
    """Creates a new QR Code review campaign in Firestore.

    Args:
        campaign_id: Unique identifier for the campaign (e.g., 'camp_003').
        business_name: Name of the business (e.g., 'Padaria Bella Vista').
        location_tag: Placement tag (e.g., 'Mesa 12', 'Balcão de Caixa').
        qr_code_target_url: URL destination for the QR code.
        rating_goal: Target Google rating goal (default: 4.8).

    Returns:
        Success confirmation message string.
    """
    db = get_firestore_client()
    doc_data = {
        "campaign_id": campaign_id,
        "business_name": business_name,
        "location_tag": location_tag,
        "qr_code_target_url": qr_code_target_url,
        "scan_count": 0,
        "rating_goal": float(rating_goal),
        "status": "active",
        "created_at": firestore.SERVER_TIMESTAMP
    }
    db.collection("qr_campaigns").document(campaign_id).set(doc_data)
    return f"Campaign '{campaign_id}' for location '{location_tag}' successfully created in Firestore!"


def list_customer_reviews(sentiment_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches customer reviews from Firestore, optionally filtered by sentiment.

    Args:
        sentiment_filter: Optional filter ('POSITIVE', 'NEUTRAL', 'NEGATIVE').

    Returns:
        List of dictionaries containing customer reviews.
    """
    db = get_firestore_client()
    query = db.collection("customer_reviews")
    if sentiment_filter and sentiment_filter.upper() in ["POSITIVE", "NEUTRAL", "NEGATIVE"]:
        query = query.where("sentiment", "==", sentiment_filter.upper())

    docs = query.stream()
    reviews = []
    for doc in docs:
        data = doc.to_dict()
        data["doc_id"] = doc.id
        reviews.append(data)
    return reviews


def update_review_response(review_id: str, response_text: str) -> str:
    """Updates a customer review with an AI-generated response in Firestore.

    Args:
        review_id: The review ID (e.g. 'rev_102').
        response_text: The response text generated for the customer.

    Returns:
        Success confirmation message string.
    """
    db = get_firestore_client()
    doc_ref = db.collection("customer_reviews").document(review_id)
    doc = doc_ref.get()
    if not doc.exists:
        return f"Error: Review '{review_id}' not found in Firestore."

    doc_ref.update({
        "generated_response": response_text,
        "response_status": "RESPONDED",
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    return f"Response for review '{review_id}' updated successfully in Firestore!"
