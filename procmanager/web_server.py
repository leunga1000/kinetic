# webapp.py - example from RealPython https://realpython.com/python-http-server/ with some tweaks for updates

from procmanager import config

# testing url http://localhost:3000/runjob/hello?authorization=13131
async def runjob(res, req, jobname):
    #print(user)
    #print(dir(res))
    #print(dir(req))
    #print(res.user)
    from job_instance import run_job
    run_job(jobname)
    res.end('jobname  ab' + jobname + ' ' + str(req.user))



def start_web_server(web_app=None, args=None):
    return
    

if __name__ == "__main__":
    start_web_server()


# import asyncio
# import tornado

# def authenticate(handler):
#     auth = handler.request.headers.get('Authorization')
#     print(auth)
#     if not auth:
#         auth = request.get_argument('Authorization')
#     if auth:
#         print(auth)

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello, world")

# class RunJobHandler(tornado.web.RequestHandler):
#     def get(self):
#         job_name = self.get_argument('jobname')
#         if not authenticate(self):
#             self.write("unauthenticated")
#             return
#         self.write("Running job " + job_name)
#         print(self.request.headers)

# class RunJobPathHandler(tornado.web.RequestHandler):
#     def get(self, path):
#         #job_name = self.get_argument('jobname')
#         if not authenticate(self.request):
#             self.write("unauthenticated")
#             return
#         self.write("Running job21123 " + path)
#         print(self.request.headers)

# def make_app():
#     return tornado.web.Application([
#         (r"/", MainHandler),
#         (r"/runjob", RunJobHandler),
#         (r"/runjob/(.*)", RunJobPathHandler)

#     ],
#     autoreload=config.AUTORELOAD)

# async def main():
#     app = make_app()
#     app.listen(8888)
#     await asyncio.Event().wait()


# def start_web_server():
#     # from tornado.autoreload import main as ta_main
#     # import sys
#     # print(sys.argv)
#     # sys.argv = sys.argv * 2
#     # ta_main()
#     asyncio.run(main())

# if __name__ == "__main__":
#     start_web_server()


# import json
# from functools import cached_property
# from http.cookies import SimpleCookie
# from http.server import BaseHTTPRequestHandler, HTTPServer
# from urllib.parse import parse_qsl, urlparse

# class WebRequestHandler(BaseHTTPRequestHandler):
    

#     def get_response(self):
#         print(self)
#         print(dir(self))
#         print(self.path)
#         #quit()
#         return json.dumps(
#             {
#                 #"path": self.url.path,
# "path": self.path,
#                 # "query_data": self.query_data,
#                 # "post_data": self.post_data.decode("utf-8"),
#                 # "form_data": self.form_data,
#                 # "cookies": {
#                 #     name: cookie.value
#                 #     for name, cookie in self.cookies.items()
#                 # },
#             }
#         )

#     def do_GET(self):
#         self.send_response(200)
#         self.send_header("Content-Type", "application/json")
#         self.end_headers()
#         self.wfile.write(self.get_response().encode("utf-8"))

#     def do_POST(self):
#         self.do_GET()


# def start_web_server(host='localhost', port=8002):
#     host = "0.0.0.0"
#     server = HTTPServer((host, port), WebRequestHandler)
#     #log.info
#     print('\033[32m' + 'Running Python Process Runner, spawning web server')
#     print('\033[39m') # and reset to default color
#     server.serve_forever()


if __name__ == "__main__":
    start_web_server()
