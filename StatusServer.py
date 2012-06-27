#!/usr/bin/python
# -*- coding: utf-8 *-*

"""
Esta clase tiene como fin poder probar el status de los servidores
remotos para los puertos seleccionados
    :author: Marcelo Martinovic
    :version: 0.1.3
    :organization: Marcelo Martinovic
    :license: GPL
    :contact: marcelo dot martinovic at gmail dot com
    :note: Esta es una version para ser ejecutada en python 2.7+ no funciona en
            python3 por los cambios de mejoras del lenguaje

    :todo: Ver si es mejor implementar Google App Engine o sigo con MySQL
           en modo local.
           Ver como expandir esto a otras plataformas moviles.

"""
import socket
import time
import smtplib
import datetime
import MySQLdb
import pickle
import curses

from email.MIMEText import MIMEText

import servidores


class StatusServers:
    """
    Clase
    """

    # Conexion base de datos
    host = '127.0.0.1'
    user = 'root'
    passwd = '123456'
    db = 'StatusServer'
    # Setea si hace el envio de mails
    # False: No envia
    # True: Envia
    envio = False

    def __init__(self):
        """
        Metodo de inicio
        """

        """
            TODO: Aca deberia cargar un archivo de configuracion
                Colores
                Responsable del sistema
                Tiempo de verificacion
                Idioma principal
                Mensaje en ingles, español, portugues
        """

        # Declaracion de variables de uso comun
        self.screen = curses.initscr()
        self.screen.clear()
        curses.start_color()
        curses.noecho()
        curses.curs_set(0)
        curses.cbreak()
        self.screen.keypad(1)
        # colores
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        #curses.use_default_colors()

        # Datos de inicio
        self.ip = "127.0.0.1"
        self.port = "80"
        self.mailEnviado = False
        self.tiempoEspera = 1.5
        self.errores = []
        self.verificaEstado()

    def verificaEstado(self):
        """
            Verifica el estado de los servicios
        """
        formato = "%a %b %d %H:%M:%S %Y"

        # Aqui es el ciclo de test de los servidores y sus puertos
        while True:
            # Hardcore para pruebas
            # os.system('clear')
            self.servers = servidores.servidores
            cantidadServicios = len(self.servers)
            self.pantalla()
            for srv in range(0, cantidadServicios):
                # Refresca la fecha y la hora
                self.screen.addstr(0, 76,
                    str(datetime.datetime.now().strftime(formato)),
                    curses.color_pair(3))
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Verifica IP y puerto, si hay error envia un correo
                self.ip = self.servers[srv][0]
                self.port = self.servers[srv][1]
                self.responsable = self.servers[srv][2]
                posY = self.servers[srv][4] + 2
                try:
                    s.connect((self.ip, int(self.port)))
                    mensaje = "Servidor [%15s:%5s] \t activo   " % (self.ip,
                        self.port)
                    self.screen.addstr(posY, 10, mensaje, curses.color_pair(1))
                    # Esto permite poner nuevamente el estatus en False
                    # para poder
                    # disparar un nuevo mail si falla el servicio
                    self.servers[srv][3] = 'False'
                except:
                    mensaje = "Servidor [%15s:%5s] \t apagado   " % (self.ip,
                        self.port)
                    # si aun no se envio el correo pone a True
                    # mailEnviado correo
                    # y emite el correo
                    try:
                        self.screen.addstr(posY, 10, mensaje,
                            curses.color_pair(2))
                    except:
                        pass

                    if(self.servers[srv][3] == 'False'):
                        self.servers[srv][3] = 'True'
                        self.mysqlCnx()
                        self.envioDeCorreoAlerta()
                    else:
                        self.screen.addstr(posY, 45, "\t\t ...aviso emitido",
                            curses.color_pair(2))
                # Graba el estado de los servicios para poder pasarlos a
                # android.
                pickle.dump(self.servers, open("servers.pickle", "wb"))
                # Pinta la pantalla
                self.screen.refresh()
                #inicia la espera de 1500ms
                time.sleep(self.tiempoEspera)
        curses.endwin()

    def pantalla(self):
        """
            Header de la pantalla
            diseño de pantalla
        """
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        self.cleanScreen()
        self.screen.addstr(0, 0, "Estado de servicios", curses.color_pair(3))
        self.screen.addstr(1, 0, "Version 0.1", curses.color_pair(3))
        self.screen.addstr(1, 69, "by marcelo.martinovic@gmail.com",
            curses.color_pair(3))
        self.screen.addstr(2, 0, "=" * 100, curses.color_pair(3))
        self.screen.refresh()

    def cleanScreen(self):
        """
            Limpia y pinta la pantalla
        """
        #paint 20 rows, 60 columns cyan
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        i = 0
        while i < 3:
            j = 0
            while j < 110:
                self.screen.addstr(i, j, " ", curses.color_pair(3))
                j += 1
            i += 1
        self.screen.refresh()

    def envioDeCorreoAlerta(self):
        """
            Envia el correo de alerta al usuario especificado
        """
        # Construimos el mensaje simple
        stringDeAviso = "Aviso el servicio en la ip: %s" + \
                    " puerto: %s ha fallado %s"

        mensaje = MIMEText((stringDeAviso % (self.ip,
            self.port, str(datetime.datetime.now()))))
        mensaje['From'] = self.responsable
        mensaje['To'] = self.responsable
        mensaje['Subject'] = "ALERTA !!! Falla en el servicio"
        if(self.envio):
            # Establecemos conexion con el servidor smtp de gmail
            mailServer = smtplib.SMTP('smtp.gmail.com', 587)
            mailServer.ehlo()
            mailServer.starttls()
            mailServer.ehlo()
            # Registro de la cuenta de GMAIL
            mailServer.login("ACA TU CUENTA DE CORREO GMAIL", "TU CLAVE")
            # Envio del mensaje
            mailServer.sendmail(mensaje['From'], mensaje['To'],
                mensaje.as_string())
            # Cierre de la conexion
            mailServer.close()
            print("\t\t ...correo enviado")

    def mysqlCnx(self):
        """
            Conector de base de datos
        """
        fecha = datetime.datetime.strptime(str(datetime.datetime.now()), \
                                        '%Y-%m-%d %H:%M:%S.%f')
        conn = MySQLdb.connect(host=self.host, user=self.user, \
                            passwd=self.passwd, \
                            db=self.db)
        sqlQuery = "INSERT INTO incidencias (ip, port, fecha_hora," + \
            "mail_enviado) values ('%s', '%s', '%s', '%s')"
        qry = (sqlQuery % (str(self.ip), str(self.port), str(fecha), "1"))
        cursorMysql = conn.cursor()
        cursorMysql.execute(qry)
        conn.commit()
        resultado = cursorMysql.fetchall()
        return resultado


def main():
    """
    llama a la clase
    """
    StatusServers()

if __name__ == "__main__":
    main()
