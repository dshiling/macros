from macros import app

'''jinja template formatter to make 'added_on' date column human readable on frontend'''


@app.template_filter('datetime_format')
def datetimeformat(value, format='%B %d, %Y'):
    return value.strftime(format)
