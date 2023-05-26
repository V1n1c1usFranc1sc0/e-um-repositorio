from flask import Flask, jsonify, request
import json
import psycopg2

hostname = 'kbdb-instance.c23eopijqhjn.us-east-1.rds.amazonaws.com'
database = 'KBPROD'
username = 'kbAdm'
pwd = 'Kb451274'
port_id = 5432
conn = None
cur = None

app = Flask(__name__)

try:
    #conexao com banco
    conn = psycopg2.connect(
        host = hostname,
        dbname = database,
        user = username,
        password = pwd,
        port = port_id)

    cur = conn.cursor()

    '''cur.execute('select * from public."user"')
    for record in cur.fetchall():
        print(record)'''
    
    '''@app.route('/user', methods=['GET'])
    def get_users():
        cur.execute('select * from public."user"')
        return jsonify(cur.fetchall())'''
    
    # consultar usuario
    @app.route('/user/authenticate/<string:user_email>',methods=['GET'])
    def authenticate_user(user_email):
        #select por email
        cur.execute(('select user_name, user_email, user_password from public."user" where user_email = %s'), (user_email,))
        return jsonify(cur.fetchall())
    
    # adicionar usuario
    # nome , email, senha , telefone
    @app.route('/user/adduser', methods=['POST'])
    def add_user():
        user_name = request.args.get('user_name', None)
        user_email = request.args.get('user_email', None)
        user_password = request.args.get('user_password', None)
        user_phone = request.args.get('user_phone', None)

        cur.execute(('insert into public."user" (user_name, user_email, user_password, user_phone) values (%s, %s, %s, %s)'), (user_name, user_email, user_password, user_phone))
        conn.commit()
        cur.execute(('select user_name, user_email, user_password from public."user" where user_email = %s'), (user_email,))
        return jsonify(cur.fetchall())
    

    # deletar usuario
    @app.route('/user/deleteuser/<string:user_email>', methods=['DELETE'])
    def delete_user(user_email):
        cur.execute(('select user_id from public."user" where user_email = %s'), (user_email,))
        size = cur.fetchall()
        if len(size) > 0:
            cur.execute(('delete from public."user" where user_email = %s'), (user_email,))
            conn.commit()
            return jsonify('usuario deletado')
        else:
            return jsonify('usuario nao encontrado')

    

    #consultar projeto
    @app.route('/project/owner/search/<int:project_owner>', methods=['GET'])
    def search_project(project_owner):
        cur.execute(('select project_id, project_name from public.project where project_owner = %s'), (project_owner,))
        return jsonify(cur.fetchall())

    #criar projeto
    @app.route('/project/create', methods=['POST'])
    def create_project():
        project_name = request.args.get('project_name', None)
        project_owner = request.args.get('project_owner', None)

        #criar o projeto
        cur.execute(('insert into public.project (project_name, project_owner) values (%s, %s)'), (project_name, project_owner))
        conn.commit()

        #adicionar owner como membro do projeto

        
        return jsonify('projeto criado')

    #deletar projeto
    @app.route('/project/delete/<int:project_id>', methods=['DELETE'])
    def delete_project(project_id):
        cur.execute(('select * from public.project where project_id = %s'), (project_id,))
        size = cur.fetchall()
        if len(size) > 0:
            cur.execute(('delete from public.project where project_id = %s'), (project_id,))
            conn.commit()
            return jsonify('projeto deletado')
        else:
            return jsonify('projeto nao encontrado')


    #consultar membro
    @app.route('/member/fetch/<int:project_id>', methods=['GET'])
    def fetch_member(project_id):
        cur.execute(('select * from public."member" where project_id = %s'), (project_id,))
        return jsonify(cur.fetchall())

    #adicionar membro
    @app.route('/member/addmember', methods=['POST'])
    def add_member():

        #recebo os membros associados ao projeto via json na api
        body = request.get_json()
        
        #armazeno os dados recebidos em uma lista
        member_list = []
        for info in body['values']:
            member_list.append([info['project_id'], info['user_id']])

        #percorro a lista e adiciono o par
        for member in member_list:
            print(member[0],member[1])
            cur.execute(('insert into public."member" (project_id, user_id) values (%s,%s)'), (member[0], member[1]))
            conn.commit()            

        return jsonify(body)

    #remover membro
    @app.route('/member/delete/<int:member_id>', methods=['DELETE'])
    def delete_member(member_id):
        cur.execute(('select * from public."member" where member_id = %s'),(member_id,))
        size = cur.fetchall()
        if len(size) > 0:
            cur.execute(('delete from public."member" where member_id = %s'),(member_id,))
            conn.commit()
            return jsonify('membro removido')
        else:
            return jsonify('membro nao encontrado')



    #criar coluna
    @app.route('/column/addcolumn/', methods=['POST'])
    def add_column():
        project_id = request.args.get('project_id', None)
        column_name = request.args.get('column_name', None)

        cur.execute(('insert into public."column" (project_id, column_name) values (%s, %s)'), (project_id,column_name))
        conn.commit()
        return jsonify('coluna criada')
    

    #consultar coluna
    @app.route('/column/fetchcolumn/<int:project_id>', methods=['GET'])
    def fetch_column(project_id):
        cur.execute(('select * from public."column" where project_id = %s'),(project_id,))
        return jsonify(cur.fetchall())


    #deletar coluna
    @app.route('/column/delete/<int:column_id>', methods=['DELETE'])
    def delete_column(column_id):
        cur.execute(('select * from public."column" where column_id = %s'),(column_id,))
        size = cur.fetchall()
        if len(size) > 0:
            cur.execute(('delete from public."column" where column_id = %s'),(column_id,))
            conn.commit()
            return jsonify('coluna removida')
        else:
            return jsonify('coluna nao encontrada')
        

    #criar tarefa
    @app.route('/task/addtask/', methods=['POST'])
    def add_task():
        project_id = request.args.get('project_id', None)
        column_id = request.args.get('column_id', None)
        task_description = request.args.get('task_description', None)

        cur.execute(('insert into public.task (project_id, column_id, task_description) values (%s, %s, %s)'),(project_id, column_id, task_description))
        conn.commit()
        return jsonify('tarefa criada')


    #consultar tarefa
    @app.route('/task/fetchtask/', methods=['GET'])
    def fetch_task():
        project_id = request.args.get('project_id', None)
        column_id = request.args.get('column_id', None)

        cur.execute(('select * from public.task where project_id = %s and column_id = %s'),(project_id,column_id))
        return jsonify(cur.fetchall())

    #deletar tarefa
    @app.route('/task/delete/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        cur.execute(('select * from public.task where task_id = %s'),(task_id,))
        size = cur.fetchall()
        if len(size) > 0:
            cur.execute(('delete from public.task where task_id = %s'),(task_id,))
            conn.commit()
            return jsonify('tarefa removida')
        else:
            return jsonify('tarefa nao encontrada')


        


    app.run(port=5000,host='localhost',debug=True)

except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()