class SubmissionError(ValueError): pass
def validate_forecast(frame):
 if frame.isna().any().any() or frame.week_start.duplicated().any(): raise SubmissionError('invalid')
