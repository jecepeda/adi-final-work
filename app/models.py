from google.appengine.ext import ndb
from passlib.apps import custom_app_context as pwd_context
import re


class User(ndb.Model):
    nick = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    hashed_password = ndb.StringProperty()
    last_name = ndb.StringProperty(required=True)

    def hash_password(self, password):
        self.hashed_password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)

    def __repr__(self):
        return "User: email:{}".format(self.key.id())

    def __str__(self):
        return self.__repr__()

    @property
    def toJSON(self):
        return {"id": self.key.id(),
                "nick": self.nick,
                "name": self.name,
                "lastName": self.last_name}

    @classmethod
    def getAll(self):
        users = []
        for user in User.query():
            users.append(user.toJSON)
        return users


class Author(ndb.Model):
    organism = ndb.KeyProperty(kind='Organism', required=True)
    name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)

    def __repr__(self):
        return "Author: name: {}".format(self.name)

    def __str__(self):
        return self.__repr__()

    @property
    def toJSON(self):
        return {"id": self.key.id(),
                "organism": self.organism.get().toJSON,
                "name": self.name,
                "lastName": self.last_name}

    @classmethod
    def getAll(self):
        authors = []
        for author in Author.query():
            authors.append(author.toJSON)
        return authors


class Organism(ndb.Model):
    name = ndb.StringProperty(repeated=False)
    address = ndb.StringProperty(required=True)
    country = ndb.StringProperty(required=True)

    @property
    def toJSON(self):
        return {"id": self.key.urlsafe(),
                "name": self.name,
                "address": self.address,
                "country": self.country}

    @classmethod
    def getAll(self):
        organisms = []
        for organism in Organism.query():
            organisms.append(organism.toJSON)
        return organisms


class Paper(ndb.Model):
    author = ndb.KeyProperty(kind='Author', required=True)
    title = ndb.StringProperty(required=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @property
    def toJSON(self):
        return {"id": self.key.urlsafe(),
                "title": self.title,
                "author": self.author.id(),
                "updated": str(self.updated)}

    @classmethod
    def getAll(self):
        papers = []
        for paper in Paper.query():
            papers.append(paper.toJSON)
        return papers
