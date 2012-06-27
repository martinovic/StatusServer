# -*- coding: utf-8 *-*

from werkzeug.wrappers import Request, Response

#import datetime
import MySQLdb
import pickle


@Request.application
def application(request):
    """
        Genera el JSON con los datos de la base
        y lo envia como response
    """
    respuesta = ""
    print("in estado")
    servers = pickle.load(open("servers.pickle", "rb"))
    incidencias = ""
    incidenciaTpl = '{"ip":"%s","port":"%s","estado":"%s"},'
    for i in servers:
        incidencias += (incidenciaTpl % (str(i[0]), str(i[1]), \
            str(i[3])))
    respuesta = '{"lista": [' + incidencias[:-1] + ']}'

    return Response(respuesta)


def estado(request):
    """
        Muestra el estado de los servicios
    """
    print("in estado")
    servers = pickle.load(open("servers.pickle", "rb"))
    incidencias = ""
    incidenciaTpl = '{"ip":"%s","port":"%s","estado":"%s"},'
    for i in servers:
        incidencias += (incidenciaTpl % (str(i[0]), str(i[1]), \
            str(i[3])))
    respuesta = '{"lista": [' + incidencias[:-1] + ']}'
    return respuesta


def historial():
    """
        Muestra el historial de eventos
        Limite de eventos 50
    """
    #    fecha = datetime.datetime.strptime(str(datetime.datetime.now()), \
    #                                    '%Y-%m-%d %H:%M:%S.%f')
    #    for idIncidencia, ip, port, fecha, mail_enviado in mysqlCnx():
    #        incidencias += (incidenciaTpl % (ip, port, fecha, mail_enviado))
    pass


def mysqlCnx():
    """
        Conector de base de datos
    """
    host = '127.0.0.1'
    user = 'root'
    passwd = '123456'
    dbUse = 'StatusServer'
    conn = MySQLdb.connect(host=host, user=user, \
                        passwd=passwd, \
                        db=dbUse)
    sqlQuery = "select * from incidencias "
    sqlQuery += "order by fecha_hora, ip desc"
    qry = sqlQuery
    cursorMysql = conn.cursor()
    cursorMysql.execute(qry)
    conn.commit()
    resultado = cursorMysql.fetchall()
    return resultado


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, application, use_debugger=True,
        use_reloader=True)
