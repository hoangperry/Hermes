class DatabaseConfiguration:
    host_name = "localhost"
    db_name = "default"
    user_name = "user"
    password = ""
    db_port = 2706

    def __init__(self, host_name="localhost", db_name="default", user_name="user", password="", db_port=2706):
        """Init configuration """
        self.host_name = host_name
        self.db_name = db_name
        self.user_name = user_name
        self.password = password
        self.db_port = db_port

    @staticmethod
    def set_config(host_name="localhost", db_name="default", user_name="user", password="", db_port=2706):
        """
        Set static database configuration
        :param host_name:
        :param db_name:
        :param user_name:
        :param password:
        :param db_port:
        :return:
        """
        DatabaseConfiguration.host_name = host_name
        DatabaseConfiguration.db_name = db_name
        DatabaseConfiguration.user_name = user_name
        DatabaseConfiguration.password = password
        DatabaseConfiguration.db_port = db_port


class CrawlerConfiguration:
    proxies = []
    num_threads = 2

    @staticmethod
    def set_config(proxy_file):
        """
        Set crawler configs
        :param proxy_file:
        :param num_threads:
        :return:
        """
        #CrawlerConfiguration.num_threads = num_threads
        try:
            CrawlerConfiguration.proxies = open(proxy_file).readlines()
        except Exception as ex:
            print("Proxy error: " , ex)
