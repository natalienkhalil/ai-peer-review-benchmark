from providers.anthropic_provider import make_anthropic_providers
from providers.openai_provider import make_openai_providers
from providers.gemini_provider import make_gemini_providers
from providers.refine_provider import make_refine_providers
from providers.reviewer3_provider import make_reviewer3_providers
from providers.flatfile_provider import FlatFileProvider


def get_all_providers() -> list:
    providers = []
    providers.extend(make_anthropic_providers())
    providers.extend(make_openai_providers())
    providers.extend(make_gemini_providers())
    providers.extend(make_refine_providers())
    providers.extend(make_reviewer3_providers())
    return providers


def get_provider_by_name(name: str):
    for p in get_all_providers():
        if p.name == name:
            return p
    raise ValueError(f"Unknown provider: {name}. Available: {[p.name for p in get_all_providers()]}")
