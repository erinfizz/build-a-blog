
import webapp2
import cgi
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
        
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
        
class Content(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

        
class MainPage(Handler):
    def render_base(self, title="", content="", error=""):
        contents = db.GqlQuery("SELECT * FROM Content ORDER By created DESC")
        self.render("base.html", title=title, content=content, error=error, contents=contents)
    def get(self):
        self.render_base()
        
    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        
        if title and content:
            c = Content(title=title, content = content)
            c.put()
            
            self.redirect("/")
            
        else:
            error = "there must be both a title and a blog post!"
            self.render_base(title, content, error)

class BlogPage(Handler):
    def render_blog(self, title="", content=""):
        contents = db.GqlQuery("SELECT * FROM Content ORDER by created DESC LIMIT 5")
        self.render("blog.html", title=title, content=content, contents=contents)
    def get(self):
        self.render_blog()
    
        
    
class NewPost(Handler):
    def render_new(self, title="", content="", error=""):
        contents = db.GqlQuery("SELECT * FROM Content ORDER By created DESC")
        self.render("newpost.html", title=title, content=content, error=error, contents=contents)
    def get(self):
        self.render_new()
        
    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        
        if title and content:
            c = Content(title=title, content = content)
            c.put()
            
            post_id = c.key().id()
            
            self.redirect("/blog/" + str(post_id))
            
        else:
            error = "there must be both a title and a blog post!"
            self.render_new(title, content, error)
        
class ViewPostHandler(Handler):
    
    def get(self, id):
        if Content.get_by_id(int(id)) == None:
            error = "That doesn't exist!"
            self.response.write(error)
        
        else:
            post_id = Content.get_by_id(int(id))
            self.render("single.html", post_id= post_id )

        
    

app = webapp2.WSGIApplication([
    ('/', MainPage), 
    ('/blog', BlogPage), 
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
