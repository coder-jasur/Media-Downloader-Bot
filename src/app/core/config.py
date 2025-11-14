import environs

env = environs.Env()
env.read_env()

class Settings:
    bot_token = env.str("BOT_TOKEN")
    bot_user_redis = env.bool("BOT_USE_REDIS")
    tg_api_server_url = env.str("TG_API_SERVER_URL", default="https://api.telegram.org")
    admins_ids = env.list("ADMINS_IDS")

    db_name = env.str("POSTGRES_DB")
    db_user = env.str("POSTGRES_USER")
    db_password = env.str("POSTGRES_PASSWORD")
    db_host = env.str("POSTGRES_HOST")
    db_port = env.str("POSTGRES_PORT")

    redis_host = env.str("REDIS_HOST")
    redis_db_name = env.str("REDIS_DB")

    selenium_url = env.str("SELENIUM_REMOTE_URL")

    lastfm_api_key = env.str("LASTFM_API_KEY")