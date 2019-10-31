from termcolor import colored
import itertools
import functools
import asyncio
from aiohttp import web
from ..clients import clients
from ..models import models
from ..cli import set_logger

STATUS = {
    200: lambda x: web.json_response(x, status=200),
    500: lambda x: web.json_response(dict(error=str(x), type=type(x).__name__), status=500)
}


class RankProxy:
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.queries = dict()
        self.logger = set_logger(self.__class__.__name__)
        self.model = getattr(models, self.args.model)(self.args)
        self.client = getattr(clients, self.args.client)(self.args)

    @property
    def status(self):
        return dict(res='Chillin')

    async def route_handler(self, f):
        @functools.wraps(f)
        def decorator(*args, **kwargs):
            try:
                self.logger.info('new %s request' % f.__name__)
                return STATUS[200](f(*args, **kwargs))
            except Exception as ex:
                self.logger.error('Error on %s request' % f.__name__, exc_info=True)
                return STATUS[500](ex)

        return decorator

    @route_handler
    async def status(self):
        return self.status

    @route_handler
    async def query(self, request):
        response, candidates, q = await self.client.query(request)
        ranks = self.model(q, candidates)
        self.queries[next(counter)] = q, candidates
        return client.reorder(response, ranks)

    @route_handler
    async def train(self, request):
        q, candidates = self.queries[request.query.qid]
        labels = [0] * len(candidates)
        labels[request.query.cid] = 1
        return model(q, candidates, labels=labels)

    def create_site(self):

        counter = itertools.count()
        loop = asyncio.get_event_loop()

    async def main():
        app = web.Application()
        app.add_routes([
            web.get('/status', status),
            web.get('/query', query),
            web.post('/train', train),
        ])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.args.proxy_host, self.args.proxy_port)
        await site.start()

        logger.info('proxy forwarding %s:%d to %s:%d' % (
            self.args.proxy_host, self.args.proxy_port,
            self.args.server_host, self.args.server_port))

        loop.run_until_complete(main())

    def run(self):
        self.create_site()
