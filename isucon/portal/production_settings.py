from isucon.portal.docker_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'prod-!rrh-a==+s2dbqxx^xkoxx)ygo=8q45ge@i0&lztw2sixet4'

# 動作設定

# 登録期間
REGISTRATION_START_AT = portal_utils.get_jst_datetime(2023, 10, 17, 18, 0, 0)
REGISTRATION_END_AT = portal_utils.get_jst_datetime(2023, 10, 20, 22, 00, 0)

# コンテスト開催期間
# 日付
CONTEST_DATE = datetime.date(2023, 11, 25)

# 時刻
CONTEST_START_TIME = portal_utils.get_jst_time(10, 0, 0)
CONTEST_END_TIME = portal_utils.get_jst_time(18, 0, 0)

# Result
SHOW_RESULT_AFTER = portal_utils.get_jst_datetime(2023, 11, 26, 22, 0, 0)


# 最大チーム数
MAX_TEAM_NUM = 636

# Discord
DISCORD_APPLICATION_ID = os.environ.get("DISCORD_APPLICATION_ID", "")
DISCORD_SECRET = os.environ.get("DISCORD_SECRET", "")
DISCORD_OAUTH_CLIENT_ID = os.environ.get("DISCORD_OAUTH_CLIENT_ID", "")
DISCORD_OAUTH_CLIENT_SECRET = os.environ.get("DISCORD_OAUTH_CLIENT_SECRET", "")

DISCORD_SERVER_ID = os.environ.get("DISCORD_SERVER_ID", "")
DISCORD_BOT_ACCESS_TOKEN = os.environ.get("DISCORD_BOT_ACCESS_TOKEN", "")
DISCORD_USER_ROLE_ID = os.environ.get("DISCORD_USER_ROLE_ID", "")
DISCORD_USER_LOCAL_PARTICIPATION_ROLE_ID = os.environ.get("DISCORD_USER_LOCAL_PARTICIPATION_ROLE_ID", "")

# AWS
SQS_JOB_URLS = {
    "apne1-az1": "https://sqs.ap-northeast-1.amazonaws.com/424484851194/prod-job-queue-apne1-az1.fifo",
    "apne1-az2": "https://sqs.ap-northeast-1.amazonaws.com/424484851194/prod-job-queue-apne1-az2.fifo",
    "apne1-az4": "https://sqs.ap-northeast-1.amazonaws.com/424484851194/prod-job-queue-apne1-az4.fifo",
}

SQS_JOB_RESULT_URL = "https://sqs.ap-northeast-1.amazonaws.com/424484851194/prod-job-result"
