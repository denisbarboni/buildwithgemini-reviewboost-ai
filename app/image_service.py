"""Image generation service for ReviewBoost AI using Gemini 3.1 Flash Lite Image model.
Hardcoded Bucket Name: reviewboost-ai-media-qwiklabs-gcp-03-95b844f06177
Hardcoded Project ID: qwiklabs-gcp-03-95b844f06177
"""
import uuid
from typing import Optional
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded literals required for Agent Platform deployment
PROJECT_ID = "qwiklabs-gcp-03-95b844f06177"
BUCKET_NAME = "reviewboost-ai-media-qwiklabs-gcp-03-95b844f06177"


async def generate_campaign_image(prompt: str, tool_context: ToolContext) -> str:
    """Generates a promotional campaign image or display flyer using gemini-3.1-flash-lite-image model in global region.

    Saves the generated image as an ADK artifact and uploads it to public Cloud Storage.

    Args:
        prompt: Detailed visual prompt describing the promotional card or flyer (e.g., 'Modern counter display card for Padaria Bella Vista asking customers for a 5-star Google review').
        tool_context: ADK ToolContext used to record artifacts for Playground UI.

    Returns:
        String message containing the public Cloud Storage HTTPS URL of the image.
    """
    # 1. Initialize Gemini client with global region as requested
    client = genai.Client(
        vertexai=True,
        location="global",
        project=PROJECT_ID
    )

    # 2. Call gemini-3.1-flash-lite-image model
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"]
        )
    )

    image_bytes: Optional[bytes] = None
    mime_type: str = "image/jpeg"

    if response.candidates:
        for candidate in response.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.data:
                        image_bytes = part.inline_data.data
                        if part.inline_data.mime_type:
                            mime_type = part.inline_data.mime_type
                        break

    if not image_bytes:
        return "Erro: O modelo não retornou bytes de imagem na resposta."

    # 3. (1) Save with tool_context.save_artifact for Playground Artifacts panel
    filename = f"campaign_flyer_{uuid.uuid4().hex[:8]}.jpg"
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 4. (2) Upload image bytes directly to public GCS bucket (no local file path returned)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return f"Imagem promocional gerada com sucesso! URL pública: {public_url}"
