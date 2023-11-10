

#######
# Job #
#######

class DuplicateJobError(Exception):
    """キューに重複してジョブが登録された際に発生する例外"""
    pass

class TeamBenchTargetDoesNotExistError(Exception):
    """チームのベンチマーク対象が見つからない際に発生する例外"""
    pass

class TeamBenchTargetTooManyError(Exception):
    """チームのベンチマーク対象が複数存在してしまっている際に発生する例外"""
    pass

class JobDoesNotExistError(Exception):
    """指定されたjob_idのジョブが見つからない際に発生する例外"""
    pass

class TeamScoreDoesNotExistError(Exception):
    """チーム作成時、シグナルによって作成されるはずのScoreが存在しなかった際に発生する例外"""
    pass