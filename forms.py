from wtforms import Form, StringField, validators

class DomainNameForm(Form):

    # Check if domain name is valid
    domain_name = StringField('domainName', [
            validators.Length(max=253),
            validators.Regexp(r'(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)')
        ])