from isucon.portal.docker_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'prod-!rrh-a==+s2dbqxx^xkoxx)ygo=8q45ge@i0&lztw2sixet4'

# 動作設定

# 登録期間
REGISTRATION_START_AT = portal_utils.get_jst_datetime(2023, 9, 9, 10, 0, 0)
REGISTRATION_END_AT = portal_utils.get_jst_datetime(2023, 9, 9, 10, 10, 0)

# 最大チーム数
MAX_TEAM_NUM = 220 + 200 + 200

# Discord
DISCORD_APPLICATION_ID = os.environ.get("DISCORD_APPLICATION_ID", "")
DISCORD_SECRET = os.environ.get("DISCORD_SECRET", "")
DISCORD_OAUTH_CLIENT_ID = os.environ.get("DISCORD_OAUTH_CLIENT_ID", "")
DISCORD_OAUTH_CLIENT_SECRET = os.environ.get("DISCORD_OAUTH_CLIENT_SECRET", "")

DISCORD_SERVER_ID = os.environ.get("DISCORD_SERVER_ID", "")
DISCORD_BOT_ACCESS_TOKEN = os.environ.get("DISCORD_BOT_ACCESS_TOKEN", "")
DISCORD_USER_ROLE_ID = os.environ.get("DISCORD_USER_ROLE_ID", "")
