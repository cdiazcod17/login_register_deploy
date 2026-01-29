from flask import Flask, request,url_for,redirect,render_template,flash,session
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash,check_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key =os.getenv('SECRETKEY')

def get_conn():       
    return mysql.connector.connect(
        host=os.getenv('MYSQL_ADDON_HOST'),
        user=os.getenv('MYSQL_ADDON_USER'),
        password=os.getenv('MYSQL_ADDON_PASSWORD'),
        database=os.getenv('MYSQL_ADDON_DB'),
        port=os.getenv('MYSQL_ADDON_PORT'),
        #uri=os.getenv('MYSQL_ADDON_URI')
    )
    

@app.route('/')
def index():
    if 'user_id' in session:        
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register')
def register_form():
    if 'user_id' in session:
        flash('Para registrar un nuevo usuario debes cerrar la sesion actual','danger')
        return redirect(url_for('dashboard'))
    return render_template('register.html',title ='Registro')

@app.route('/register', methods=['POST'])
def register_submit():
    name = request.form.get('name','').strip()
    email = request.form.get('email','').strip().lower()
    password = request.form.get('password','')
    confirm_password = request.form.get('confirm_password','')
    
    ##validar los datos antes de meterlos en la bd
    
    if not name or not email or not password:
        flash('Todos los campos son obligatorios','danger')
        return redirect(url_for('register_form'))
    
    if len(password) < 6:
        flash('La contraseña ha de contener 6 caracteres minimo.' ,'danger')
    
    if password != confirm_password:
        flash('El campo password y confirmar password no son iguales','danger')
        return redirect(url_for('register_form'))
    
    conn = get_conn()
    try:
        ##1.Comprobar si el email existe
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT id FROM users WHERE email = %s',(email,))
        exisiting = cur.fetchone()
        if exisiting:
            flash('Este email ya esta registrado.','danger')
            return redirect(url_for('register_form'))
        ##2 Hashear las contrasenias
        
        password_hash = generate_password_hash(password)
        
        ##3 Insertar en la base de datos el usuario
        cur.execute('INSERT INTO users (name,email,password_hash) VALUES (%s,%s,%s)',(name,email,password_hash))
        conn.commit()
        flash('registro realizado','succes')
        return redirect(url_for('login'))        
    # except Exception as e:
    #     print('Error',e)
    finally:
        conn.close()
        
@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html',title= 'login')
    
@app.route('/login',methods = ['POST'])
def  login_submit():    
    email = request.form.get('email','').strip().lower()
    password = request.form.get('password','')
    
    if not email or not password:
        flash('Email y contrasena obligatorios','danger')
        return redirect(url_for('login'))
    conn = get_conn()
    
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM users WHERE email =%s',(email,))
        user = cur.fetchone()
        print(user)
        
        if not user:
            flash('Usuario incorrecto','danger')
            return redirect(url_for('login'))
        
        if not check_password_hash(user['password_hash'],password):
            flash('contrasena incorrecta','danger')
            return redirect(url_for('login'))
            
        
        ##SESSION
        
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        
        flash('Bienvenido {}'.format(user['name']),'success')
        return redirect(url_for('dashboard'))
        
        
    # except Exception as e:
    #     print(e)
    
    finally:
        conn.close()
        
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Debes iniciar sesion','danger')
          # Para depurar
        print('User ID:', session.get('user_id'))
        print('User Name:', session.get('user_name'))
        return redirect(url_for('login'))
      # Para depurar
    print('User ID:', session.get('user_id'))
    print('User Name:', session.get('user_name'))
    return render_template('dashboard.html',title = 'dashboard',name=session.get('user_name',''))

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesion finalizada','info')
    return redirect(url_for('login'))

if __name__ =='__main__':
    app.run(debug=True)