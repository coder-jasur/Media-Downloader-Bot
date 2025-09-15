from src.app.texts import admin_menu_texts


async def admin_menu_text_getter(lang: str, **_kwargs) -> dict:

    return {
        **admin_menu_texts[lang],
        "title": admin_menu_texts["choose_menu"][lang]
    }
