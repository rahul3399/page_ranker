import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
import urllib.parse as p

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)
# get the API KEY here: https://developers.google.com/custom-search/v1/overview
API_KEY = "ENTER YOUR API KEY"
# get your Search Engine ID on your CSE control p anel
SEARCH_ENGINE_ID = "cfdb19d7a376066b1"
# target domain you want to track
target_domain = "thepythoncode.com"

class Book(db.Model):
    r_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    c_rank = db.Column(db.Integer, nullable=False)
    c_query = db.Column(db.String(80), nullable=False)
    c_title = db.Column(db.String(80), nullable=False)
    c_snippet = db.Column(db.String(80), nullable=False)
    c_link = db.Column(db.String(80), nullable=False)
    def __repr__(self):
        return f"{self.r_id} - {self.c_rank} - {self.c_query} - {self.c_title} - {self.c_snippet} - {self.c_link}"


@app.route('/')
def hello_world():
    return render_template('index.html')
@app.route('/list/',methods = ['POST', 'GET'])
def list():
    if request.method == 'GET':
        books = Book.query.all()
        return render_template("list.html", books=books)
    if request.method == 'POST':
        
        form_data = request.form.get("name")
        query = form_data
        for page in range(1, 11):
            print("[*] Going for page:", page)
            # calculating start 
            start = (page - 1) * 10 + 1
            # make API request
            url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}"
            data = requests.get(url).json()
            search_items = data.get("items")
            # a boolean that indicates whether `target_domain` is found
            found = False
            for i, search_item in enumerate(search_items, start=1):
                # get the page title
                title = search_item.get("title")
                # page snippet
                snippet = search_item.get("snippet")
                # alternatively, you can get the HTML snippet (bolded keywords)
                html_snippet = search_item.get("htmlSnippet")
                # extract the page url
                link = search_item.get("link")
                # extract the domain name from the URL
                domain_name = p.urlparse(link).netloc
                if domain_name.endswith(target_domain):
                    # get the page rank
                    rank = i + start - 1
                    book = Book(c_rank=rank, c_query = query, c_title = title, c_snippet = snippet,c_link = link)
                    db.session.add(book)
                    db.session.commit()
                    print(f"[+] {target_domain} is found on rank #{rank} for keyword: '{query}'")
                    print("[+] Title:", title)
                    print("[+] Snippet:", snippet)
                    print("[+] URL:", link)
                    found = True
                    break
            if found:
                books = Book.query.all()
                return render_template('list.html',books = books)
@app.route('/delete/<string:r_id>',methods = ['POST','GET']) 
def delete(r_id):
    book = Book.query.filter_by(r_id=r_id).first()
    db.session.delete(book)
    db.session.commit()
    return redirect("/list/")

if __name__ == '__main__':
    app.run(debug=True)
