
from flask import Flask, render_template, redirect, url_for, request, session
import os
import sqlite3 as sql
import hashlib

app = Flask(__name__)

template_folder = os.path.join(os.path.dirname(__file__), "templates/")
app.static_folder = 'static'
app.static_url_path = '/static'

#File size upload not over 4MB
app.config['MAX_CONTENT_LENGTH'] = 4 * 1000 * 1000 

#Upload Folder 
UPLOAD_PROFILE_FOLDER = os.path.join(os.path.dirname(__file__), "static/profile")

app.secret_key = "I-BIT"

#Database
database = os.path.join(os.path.dirname(__file__), "database/abc_company.db")

#Upload folder
UPLOAD_IMG_FOLDER = os.path.join(os.path.dirname(__file__), "static/teams")

@app.route('/', methods=["GET"])
def index():
    session['username'] = ''
    session['audit'] = False
    return render_template("sign-in.html")

@app.route('/sign-in', methods=["GET"])
def sing_in():
    return render_template("sign-in.html")

@app.route('/sign-up', methods=["GET"]) #<a href="/sign-up">Register here</a>
def sign_up():
    return render_template("sign-up.html")

@app.route('/validate-sign-in', methods=["POST"])
def validate_sign_in():
    try:
        user = request.form['user'] #request.form.get('user')
        passwd = request.form['password']
        encrypt_pass = hashlib.md5(passwd.encode()).hexdigest()

        conn = sql.connect(database)
        cur = conn.cursor()
        sql_select = """
        SELECT username, password FROM username WHERE username = ?
        """
        val = (user,) #tuple

        cur.execute(sql_select, val)
        record = cur.fetchone()
        conn.close()
        
        if encrypt_pass == record[1]:
            session['username'] = user
            session['audit'] = True
            return redirect("/main-program")
        else: 
            return render_template("error-sign-in.html")
    except:
        return render_template("error-sign-in.html")

@app.route('/validate-sign-up', methods=["POST"])
def validate_sign_up():
    fname = request.form['fname'] #request.form.get('user')
    user = request.form['user']
    passwd = request.form['password']
    cfpasswd = request.form['cfpassword']
    
    encrypt_pass = hashlib.md5(passwd.encode()).hexdigest()

    if fname !="" and user !="" and passwd !="" and passwd == cfpasswd:
        #save to db
        conn = sql.connect(database) 
        cur = conn.cursor()
        sql_insert = '''
        INSERT INTO username(username,fullname,password,authorize)
        VALUES(?,?,?,?)
        '''
        val = (user,fname,encrypt_pass,1)
        cur.execute(sql_insert,val)
        conn.commit()
        conn.close()
        return render_template("sign-up-success.html")
    else:
        return render_template("error-sign-up.html")

@app.route("/main-program", methods=["GET"])
def main_program():
    if session['audit'] == True:
        return render_template("main.html")
    else:
        return redirect("/sign-in")

@app.route("/sign-out", methods=["GET"])
def sign_out():
    session.pop('username',None)
    session.pop('audit',None)
    return redirect("/")

@app.route("/user", methods=["GET"])
def user():
    if session['audit'] == True:

        conn = sql.connect(database)
        cur = conn.cursor()
        sql_select = """
        SELECT fullname,username,authorize 
        FROM username
        ORDER BY fullname
        """
        cur.execute(sql_select)
        record = cur.fetchall() #(Tongpool Heeptaisong, tongpool.h@itd.kmutnb.ac.th, 1)
        conn.close()
        
        return render_template("user.html", user=record)
    else:
        return redirect('/sign-in')

@app.route('/user-delete/<user>', methods=["GET"])
def user_delete(user):
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_delete = """
    DELETE 
    FROM username
    WHERE username=?
    """
    val = (user,)
    cur.execute(sql_delete,val)
    conn.commit()
    conn.close()
    
    return redirect("/user")

@app.route('/user-edit/<user>', methods=["GET"])
def user_edit(user):
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_edit = """
    SELECT username, fullname, authorize 
    FROM username
    WHERE username=?
    """
    val = (user,)
    cur.execute(sql_edit,val)
    record = cur.fetchone()
    conn.close()
    
    return render_template('user-edit.html',user=record)

@app.route('/user-edit-post', methods=["POST"])
def user_edit_post():
    fname = request.form['fname']
    user = request.form['email']
    passwd = request.form['password']
    cfpasswd = request.form['cfpassword']

    if fname !="" and user !="":
        conn = sql.connect(database)
        cur = conn.cursor()
        sql_edit = """
        UPDATE username
        SET fullname=?
        WHERE username=?
        """
        val = (fname,user)
        cur.execute(sql_edit,val)
        conn.commit()
        conn.close()
        return redirect('/user')
    else:
        return redirect('/user')

@app.route('/user-add', methods=["GET"])
def user_add():
    return render_template('user-add.html')

@app.route('/user-add-post', methods=["POST"])
def user_add_post():
    fname = request.form['fname'] #request.form.get('user')
    user = request.form['user']
    passwd = request.form['password']
    cfpasswd = request.form['cfpassword']
    
    encrypt_pass = hashlib.md5(passwd.encode()).hexdigest()

    if fname !="" and user !="" and passwd !="" and passwd == cfpasswd:
        #save to db
        conn = sql.connect(database) 
        cur = conn.cursor()
        sql_insert = '''
        INSERT INTO username(username,fullname,password,authorize)
        VALUES(?,?,?,?)
        '''
        val = (user,fname,encrypt_pass,1)
        cur.execute(sql_insert,val)
        conn.commit()
        conn.close()
        return redirect('/user')
    else:
        return redirect('/user-add')

@app.route('/teams', methods=["GET"])
def teams():
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_query = '''
    SELECT team_id, fullname, email, images, fb, line_id, mobile
    FROM teams
    order by fullname
    '''
    cur.execute(sql_query)
    record = cur.fetchall()
    conn.close()

    return render_template('teams.html', names=record)

@app.route('/teams-add', methods=["GET"])
def teams_add():
    return render_template('teams-add.html')

@app.route('/teams-add-post', methods=["POST"])
def teams_add_post():

    fname = request.form['fname']
    email = request.form['email']
    fb = request.form['fb']
    line_id = request.form['line_id']
    mobile = request.form['mobile']
    filename = request.files['image']

    if filename !="":
        filename.save(os.path.join(UPLOAD_PROFILE_FOLDER, filename.filename))

    if fname !="" and email !="":
        conn = sql.connect(database)
        cur = conn.cursor()
        sql_insert = '''
        INSERT INTO teams(fullname,email,images,fb,line_id,mobile)
        VALUES (?,?,?,?,?,?)
        '''
        val = (fname,email,filename.filename,fb,line_id,mobile)
        cur.execute(sql_insert, val)
        conn.commit()
        conn.close()
        return redirect('/teams')
    else:
        return redirect('/teams-add')

@app.route('/teams-delete/<team_id>', methods=["GET"])
def teams_delete(team_id):
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_delete = '''
    DELETE FROM teams 
    WHERE team_id=?
    '''
    val = (team_id,)
    cur.execute(sql_delete, val)
    conn.commit()
    conn.close()
    return redirect('/teams')

@app.route('/teams-edit/<team_id>', methods=["GET"])
def teams_edit(team_id):
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_query = '''
    SELECT team_id, fullname, email, images, fb ,line_id, mobile
    FROM teams
    WHERE team_id=?
    '''
    val = (team_id,)
    cur.execute(sql_query, val)
    record = cur.fetchone()
    conn.close()
    return render_template('teams-edit.html', name=record)

@app.route('/teams-edit-post/<team_id>', methods=["POST"])
def teams_edit_post(team_id):
    fname = request.form['fname']
    email = request.form['email']
    fb = request.form['fb']
    line_id = request.form['line_id']
    mobile = request.form['mobile']

    filename = request.files['image']
        
    if fname !="" and email !="":
        conn = sql.connect(database)
        cur = conn.cursor()
        if filename.filename !="":
            filename.save(os.path.join(UPLOAD_PROFILE_FOLDER, filename.filename))
            sql_update = '''
            UPDATE teams 
            SET fullname=?, email=?, fb=?, line_id=?, mobile=?, images=?
            WHERE team_id=?
            '''
            val = (fname,email,fb,line_id,mobile,filename.filename,team_id)
        else:
            sql_update = '''
            UPDATE teams 
            SET fullname=?, email=?, fb=?, line_id=?, mobile=?
            WHERE team_id=?
            '''
            val = (fname,email,fb,line_id,mobile,team_id)

        cur.execute(sql_update, val)
        conn.commit()
        conn.close()
        return redirect('/teams')

    else:
        return redirect('/teams-edit' + team_id)

@app.route("/gallery", methods=["GET"])
def gallery():
    if session['audit'] == True:

        conn = sql.connect(database)
        cur = conn.cursor()
        sql_select = """
        SELECT gallery_id,link,image,category,detail 
        FROM gallery
        ORDER BY gallery_id
        """
        cur.execute(sql_select)
        record = cur.fetchall()
        conn.close()

        return render_template("gallery.html", gallery=record)
    else:
        return redirect('/sign-in')

@app.route('/gallery-add', methods=["GET"])
def gallery_add():
    return render_template('gallery-add.html')

@app.route('/gallery-add-post', methods=["POST"])
def gallery_add_post():

    link = request.form['link']
    category = request.form['category']
    detail = request.form['detail']
    picturename = request.files['image']

    if picturename !="":
        picturename.save(os.path.join(UPLOAD_PROFILE_FOLDER, picturename.filename))

    if link !="" and category !="":
        conn = sql.connect(database)
        cur = conn.cursor()
        sql_insert = '''
        INSERT INTO gallery(link,category,detail,image)
        VALUES (?,?,?,?)
        '''
        val = (link,category,detail,picturename.filename)
        cur.execute(sql_insert, val)
        conn.commit()
        conn.close()
        return redirect('/gallery')
    else:
        return redirect('/gallery-add')

@app.route('/gallery-delete/<gallery_id>', methods=["GET"])
def gallery_delete(gallery_id):
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_delete = '''
    DELETE FROM gallery
    WHERE gallery_id=?
    '''
    val = (gallery_id,)
    cur.execute(sql_delete, val)
    conn.commit()
    conn.close()
    return redirect('/gallery')

@app.route('/gallery-edit/<gallery_id>', methods=["GET"])
def gallery_edit(gallery_id):
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_query = '''
    SELECT gallery_id, link, image, category ,detail
    FROM gallery
    WHERE gallery_id=?
    '''
    val = (gallery_id,)
    cur.execute(sql_query, val)
    record = cur.fetchone()
    conn.close()
    return render_template('gallery-edit.html', gallery=record)


@app.route('/gallery-edit-post/<gallery_id>', methods=["POST"])
def gallery_edit_post(gallery_id):
    link = request.form['link']
    category = request.form['category']
    detail = request.form['detail']

    filename = request.files['image']
        
    if link !="" and category !="":
        conn = sql.connect(database)
        cur = conn.cursor()
        if filename.filename !="":
            filename.save(os.path.join(UPLOAD_PROFILE_FOLDER, filename.filename))
            sql_update = '''
            UPDATE gallery
            SET link=?, category=?, detail=?, images=?
            WHERE gallery_id=?
            '''
            val = (link,category,detail,filename.filename,gallery_id)
        else:
            sql_update = '''
            UPDATE gallery
            SET link=?, category=?, detail=?
            WHERE gallery_id=?
            '''
            val = (link,category,detail,gallery_id)

        cur.execute(sql_update, val)
        conn.commit()
        conn.close()
        return redirect('/gallery')

    else:
        return redirect('/gallery-edit' + gallery_id)

@app.route("/product", methods=["GET"])
def product():
    if session['audit'] == True:

        conn = sql.connect(database)
        cur = conn.cursor()
        sql_select = """
        SELECT product_id,title,detail,price,image
        FROM product
        ORDER BY product_id
        """
        cur.execute(sql_select)
        record = cur.fetchall()
        conn.close()
        
        return render_template("product.html", product=record)
    else:
        return redirect('/sign-in')

@app.route('/product-add', methods=["GET"])
def product_add():
    return render_template('product-add.html')

@app.route('/product-add-post', methods=["POST"])
def product_add_post():

    title = request.form['title']
    detail = request.form['detail']
    price = request.form['price']
    picturename = request.files['image']

    if picturename !="":
        picturename.save(os.path.join(UPLOAD_PROFILE_FOLDER, picturename.filename))

    if title !="" and price !="":
        conn = sql.connect(database)
        cur = conn.cursor()
        sql_insert = '''
        INSERT INTO product(title,detail,price,image)
        VALUES (?,?,?,?)
        '''
        val = (title,detail,price,picturename.filename)
        cur.execute(sql_insert, val)
        conn.commit()
        conn.close()
        return redirect('/product')
    else:
        return redirect('/product-add')

@app.route('/product-delete/<product_id>', methods=["GET"])
def product_delete(product_id):
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_delete = '''
    DELETE FROM product
    WHERE product_id=?
    '''
    val = (product_id,)
    cur.execute(sql_delete, val)
    conn.commit()
    conn.close()
    return redirect('/product')

@app.route('/product-edit/<product_id>', methods=["GET"])
def product_edit(product_id):
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_query = '''
    SELECT product_id, title, detail, price, image
    FROM product
    WHERE product_id=?
    '''
    val = (product_id,)
    cur.execute(sql_query, val)
    record = cur.fetchone()
    conn.close()
    return render_template('product-edit.html', product=record)

@app.route('/product-edit-post/<product_id>', methods=["POST"])
def product_edit_post(product_id):
    title = request.form['title']
    detail = request.form['detail']
    price = request.form['price']

    filename = request.files['image']
        
    if title !="" and price !="":
        conn = sql.connect(database)
        cur = conn.cursor()
        if filename.filename !="":
            filename.save(os.path.join(UPLOAD_PROFILE_FOLDER, filename.filename))
            sql_update = '''
            UPDATE product
            SET title=?, detail=?, price=?, image=?
            WHERE product_id=?
            '''
            val = (title,detail,price,filename.filename,product_id)
        else:
            sql_update = '''
            UPDATE product
            SET title=?, detail=?, price=?
            WHERE product_id=?
            '''
            val = (title,detail,price,product_id)

        cur.execute(sql_update, val)
        conn.commit()
        conn.close()
        return redirect('/product')

    else:
        return redirect('/product-edit' + product_id)

@app.route("/document", methods=["GET"])
def document():
    if session['audit'] == True:

        conn = sql.connect(database)
        cur = conn.cursor()
        sql_select = """
        SELECT document_id,title,category,file 
        FROM document
        ORDER BY document_id
        """
        cur.execute(sql_select)
        record = cur.fetchall()
        conn.close()
        print(record)
        return render_template("document.html", document=record)
    else:
        return redirect('/sign-in')

@app.route('/document-add', methods=["GET"])
def document_add():
    return render_template('document-add.html')



@app.route('/document-edit/<document_id>', methods=["GET"])
def document_edit(document_id):
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_query = """
    SELECT document_id, title, category, file 
    FROM document
    WHERE document_id=?
    """
    val = (document_id,)
    cur.execute(sql_query,val)
    record = cur.fetchone()
    conn.close()
    
    return render_template('document-edit.html',document=record)


@app.route('/document-edit-post/<document_id>', methods=["POST"])
def document_edit_post(document_id):
    title = request.form['title']
    category = request.form['category']
    file = request.files['file']

    if title !="" and file !="" and category !="":
        #save to db
        conn = sql.connect(database) 
        cur = conn.cursor()
        
        if file.filename !="":
            file.save(os.path.join(UPLOAD_PROFILE_FOLDER,file.filename))
            sql_update = '''
            UPDATE document
            SET title=?, category=?, file=?
            WHERE document_id=?
            '''
            val = (title, category, file.filename,document_id)
        else: 
            sql_update = '''
            UPDATE document
            SET title=?, category=?
            WHERE document_id=?
            '''
            val = (title, category,document_id)
        cur.execute(sql_update,val)
        conn.commit()
        conn.close()
        return redirect('/document')
    else:
        return redirect('/document-edit/' + document_id)



@app.route('/document-add-post', methods=["POST"])
def document_add_post():
    title = request.form['title']
    category = request.form['category']
    file = request.files['file']

    if title !="" and file !="" and category !="":
        #save to db
        conn = sql.connect(database) 
        cur = conn.cursor()
        
        if file.filename !="":
            file.save(os.path.join(UPLOAD_PROFILE_FOLDER,file.filename))
            sql_insert = '''
            INSERT INTO document(title,category,file)
            VALUES(?,?,?)
            '''
            val = (title, category, file.filename)
        else: 
            sql_insert = '''
            INSERT INTO document(title,category)
            VALUES(?,?)
            '''
            val = (title, category)
        cur.execute(sql_insert,val)
        conn.commit()
        conn.close()
        return redirect('/document')
    else:
        return redirect('/document-add')

@app.route('/document-delete/<document_id>', methods=["GET"])
def document_delete(document_id):
    conn = sql.connect(database)
    cur = conn.cursor()
    sql_delete = '''
    DELETE FROM document
    WHERE document_id=?
    '''
    val = (document_id,)
    cur.execute(sql_delete, val)
    conn.commit()
    conn.close()
    return redirect('/document')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)