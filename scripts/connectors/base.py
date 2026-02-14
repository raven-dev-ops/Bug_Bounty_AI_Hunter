class Connector:
    name = "base"

    def list_programs(self, fetcher, fixtures_dir=None):
        raise NotImplementedError

    def fetch_details(self, fetcher, program, fixtures_dir=None):
        return program
