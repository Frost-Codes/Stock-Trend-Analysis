import fxcmpy

api_logs = './data/api_logs.log'
access_token = '6a86b7d8cf1ad038e444db321ac95fe7279c607f'
trader = fxcmpy.fxcmpy(access_token=access_token, log_level='error', log_file=api_logs)