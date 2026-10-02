# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


import math


def calculate_reviews_needed(current_rating: float, current_count: int, target_rating: float = 4.8) -> str:
    """Calculates the number of consecutive 5-star Google reviews needed to reach a target rating.

    Args:
        current_rating: Current average rating (e.g., 4.2).
        current_count: Total number of existing reviews (e.g., 50).
        target_rating: Target Google rating goal (default: 4.8).

    Returns:
        String explanation of how many 5-star reviews are needed.
    """
    if target_rating >= 5.0:
        return "A meta de avaliação deve ser menor que 5.0 estrelas."

    if current_rating >= target_rating:
        return f"Sua avaliação atual de {current_rating} estrelas já atinge ou supera a meta de {target_rating} estrelas!"

    needed = math.ceil((current_count * (target_rating - current_rating)) / (5.0 - target_rating))
    return (
        f"Para subir sua nota de {current_rating:.1f} ({current_count} avaliações) "
        f"para a meta de {target_rating:.1f} estrelas, você precisará de aproximadamente "
        f"{needed} avaliações consecutivas de 5 estrelas."
    )


import json
from pathlib import Path
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

from app.firestore_service import (
    list_qr_campaigns,
    create_qr_campaign,
    list_customer_reviews,
    update_review_response,
)
from app.external_service import (
    generate_qr_code_url,
    search_local_business_address,
)
from app.image_service import generate_campaign_image
from app.video_service import generate_campaign_video

# Load Agent Engine resource name from deployment_metadata.json if available
metadata_file = Path(__file__).parent.parent / "deployment_metadata.json"
agent_engine_resource_name = None
if metadata_file.exists():
    try:
        metadata = json.loads(metadata_file.read_text())
        agent_engine_resource_name = metadata.get("remote_agent_runtime_id")
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=agent_engine_resource_name
)


from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from app.a2ui_utils import a2ui_callback


async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        pass
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "Você é o assistente inteligente da ReviewBoost AI, especializado em ajudar empresas "
        "a gerenciar campanhas de feedback por QR Code no Google Meu Negócio, responder avaliações "
        "de clientes e acompanhar metas de avaliação de reputação. "
        "Você pode executar códigos Python no ambiente seguro (Sandbox) para realizar cálculos avançados e simulações. "
        "Responda em Português."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        get_weather,
        get_current_time,
        calculate_reviews_needed,
        list_qr_campaigns,
        create_qr_campaign,
        list_customer_reviews,
        update_review_response,
        generate_qr_code_url,
        search_local_business_address,
        generate_campaign_image,
        generate_campaign_video,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
