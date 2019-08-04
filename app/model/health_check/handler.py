from app.util.handler_util import BasicHandler


class HealthCheckHandler(BasicHandler):
    
    def get(self):
        return self.finish("pong!")
