from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField ,FileField
from wtforms.validators import DataRequired, Length

class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

class PostForm(Form):
    post = TextAreaField('post', validators=[Length(min=0, max=140)])
    image = FileField(u'Image File', validators=[regexp(u'^[^/\\]\.jpg$')])
    def validate_image(form, field):
        if field.data:
            field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)

class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])
