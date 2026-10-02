"""Video generation service for ReviewBoost AI using Google's Omni model (gemini-omni-flash-preview).
Hardcoded Bucket Name: reviewboost-ai-media-qwiklabs-gcp-03-95b844f06177
Hardcoded Project ID: qwiklabs-gcp-03-95b844f06177
"""
import base64
import uuid
from typing import Optional
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded literals required for Agent Platform deployment
PROJECT_ID = "qwiklabs-gcp-03-95b844f06177"
BUCKET_NAME = "reviewboost-ai-media-qwiklabs-gcp-03-95b844f06177"


async def generate_campaign_video(prompt: str, tool_context: ToolContext) -> str:
    """Generates a short promotional campaign video for a business using Google's Omni model (gemini-omni-flash-preview) in global region.

    Saves the generated video as an ADK artifact and uploads it to public Cloud Storage.

    Args:
        prompt: Detailed visual prompt describing the promotional video campaign (e.g., 'Dynamic short video showing customer 5-star review highlights for Padaria Bella Vista').
        tool_context: ADK ToolContext used to record artifacts for Playground UI.

    Returns:
        String message containing the public Cloud Storage HTTPS URL of the video.
    """
    client = genai.Client(
        vertexai=True,
        location="global",
        project=PROJECT_ID
    )

    video_bytes: Optional[bytes] = None
    mime_type: str = "video/mp4"

    # Try calling client.interactions.create or client.models.generate_videos
    try:
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt
        )
        if hasattr(interaction, "output_video") and interaction.output_video:
            data = getattr(interaction.output_video, "data", None)
            if isinstance(data, bytes):
                video_bytes = data
            elif isinstance(data, str):
                video_bytes = base64.b64decode(data)
    except Exception as e1:
        try:
            operation = client.models.generate_videos(
                model="gemini-omni-flash-preview",
                prompt=prompt,
            )
            while not operation.done:
                import asyncio
                await asyncio.sleep(5)
                operation = client.operations.get(operation)
            if operation.response and operation.response.generated_videos:
                video = operation.response.generated_videos[0]
                video_bytes = video.video.video_bytes
        except Exception as e2:
            return f"Erro ao gerar vídeo com o modelo gemini-omni-flash-preview: {e1} / {e2}"

    if not video_bytes:
        return "Erro: O modelo gemini-omni-flash-preview não retornou bytes de vídeo na resposta."

    # 1. (1) Save with tool_context.save_artifact for Playground Artifacts panel
    filename = f"campaign_video_{uuid.uuid4().hex[:8]}.mp4"
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. (2) Upload video bytes directly to public GCS bucket (no local file path returned)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return f"Vídeo de campanha gerado com sucesso! URL pública: {public_url}"
