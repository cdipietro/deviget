class TestResource(object):
    def on_get(self, request, response):
        response.media = 'Minesweeper API is up'
