from wtforms import Form, StringField, validators

class HostNameForm(Form):

    hostname = StringField('hostname', [validators.Length(min=5, max=25)])