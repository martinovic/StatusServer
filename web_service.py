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
    print("-" * 90)
    print(request.form["param1"])

    print("-" * 90)
    if request.form["param1"] == "app":
        print("Solicitud de APP")
        servers = pickle.load(open("servers.pickle", "rb"))
        incidencias = ""
        incidenciaTpl = '{"ip":"%s","port":"%s","estado":"%s"},'
        for i in servers:
            incidencias += (incidenciaTpl % (str(i[0]), str(i[1]), \
                str(i[3])))
        respuesta = '{"lista": [' + incidencias[:-1] + ']}'
    else:
        print("Solicitud de lista de fallos de un servidor")
        respuesta = mysqlCnx(request.form["ipServer"])
        incidencias = ""
        incidenciaTpl = '{"ip":"%s","port":"%s","fecha":"%s"},'
        for ip, port, fecha_hora in respuesta:
            incidencias += (incidenciaTpl % (str(ip), str(port), \
                str(fecha_hora)))

        respuesta = '{"lista": [' + incidencias[:-1] + ']}'

    return Response(respuesta)


def mysqlCnx(ipServer):
    """
        Conector de base de datos
        y consulta ppor una ip en particular
    """
    host = '127.0.0.1'
    user = 'root'
    passwd = '123456'
    dbUse = 'StatusServer'
    conn = MySQLdb.connect(host=host, user=user, \
                        passwd=passwd, \
                        db=dbUse)
    sqlQuery = "select ip, port, fecha_hora from incidencias "
    sqlQuery += " where ip='" + ipServer + "' "
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
