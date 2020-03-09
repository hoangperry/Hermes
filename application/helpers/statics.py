import ssl


class Context:
    sasl_mechanism = 'PLAIN'
    security_protocol = 'SASL_PLAINTEXT'

    @staticmethod
    def get_context():
        context = ssl.create_default_context()
        context.options &= ssl.OP_NO_TLSv1
        context.options &= ssl.OP_NO_TLSv1_1
