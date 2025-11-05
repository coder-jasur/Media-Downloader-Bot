import gettext

LANGUAGES = ["uz", "ru", "en"]

translations = {
    lang: gettext.translation(
        "messages", localedir="translations", languages=[lang], fallback=True)
    for lang in LANGUAGES
}


def get_translator(lang: str):
    return translations.get(lang, translations["ru"])