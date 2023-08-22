from isucon.portal.docker_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'prod-!rrh-a==+s2dbqxx^xkoxx)ygo=8q45ge@i0&lztw2sixet4'

# 動作設定

# 登録期間
REGISTRATION_START_AT = portal_utils.get_jst_datetime(2023, 8, 30, 10, 0, 0)
REGISTRATION_END_AT = portal_utils.get_jst_datetime(2023, 9, 3, 9, 0, 0)
