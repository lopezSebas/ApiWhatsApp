from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)
    
with app.app_context():
    db.create_all()
    
#Funcion para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora,reverse=True)

@app.route('/')
def index():
    #obtener todos los registros ed la base de datos
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html',registros=registros_ordenados)

mensajes_log = []

#Funcion para agregar mensajes y guardar en la base de datos
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #Guardar el mensaje en la base de datos
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

TOKEN_MC = "MOUNTAINCONQUEROR"

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        reponse = recibir_mensajes(request)
        return reponse

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_MC:
        return challenge
    else:
        return jsonify({'error':'Token Invalido'}),401

def recibir_mensajes(req):
    try:
        req = request.get_json()
        entry =req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages["type"]

                #Guardar Log en la BD
                agregar_mensajes_log(json.dumps(messages))

                if tipo == "interactive":
                    tipo_interactivo = messages["interactive"]["type"]

                    if tipo_interactivo == "button_reply":
                        text = messages["interactive"]["button_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)
                    
                    elif tipo_interactivo == "list_reply":
                        text = messages["interactive"]["list_reply"]["id"]
                        numero = messages["from"]

                        enviar_mensajes_whatsapp(text,numero)

                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    enviar_mensajes_whatsapp(text,numero)

                    #Guardar Log en la BD
                    agregar_mensajes_log(json.dumps(messages))

        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})

def enviar_mensajes_whatsapp(texto,number):
    texto = texto.lower()

    if "hola" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, ¿Cómo estás? Bienvenido."
            }
        }
    elif "1" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "text": {
                "preview_url": True,
                "body": "Estos serán nuestros próximos tours! https://mountainconqueror.club/tours"
            }
        }
    elif "2" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "14.622405",
                "longitude": "-90.549373",
                "name": "Punto de reunión Centro Comercial Rus Mall",
                "address": "Centro Comercial Rus Mall"
            }
        }
    elif "3" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "14.854814",
                "longitude": "-91.536485",
                "name": "Punto de reunión Shell • Rotonda Paseo Las Americas",
                "address": "Shell • Rotonda Paseo Las Americas"
            }
        }
    elif "4" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🙋‍♂️ Hola soy asistente de Sebas, lamento que no hayas encontrado la información que buscabas y solicitas apoyo para resolver tus dudas. \n\n📌 *Puedesde escribirme a mi número persona y con gustó te atenderé.* \n\n +502 30247344"
            }
        }    
    elif "5" in texto:
        data ={
            "messaging_product": "whatsapp",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type" : "list",
                "body": {
                    "text": "Seleccionar Lista"
                },
                "footer": {
                    "text": "Selecciona el listado de eventos próximos"
                },
                "action":{
                    "button":"Ver Eventos",
                    "sections":[
                        {
                            "title":"Eventos",
                            "rows":[
                                {
                                    "id":"1l",
                                    "title" : "Volcanes 7 Orejas, Cerro Quemado + Cerro El Granizo",
                                    "description": "Enero 31 - Febrero 02 (Campamento)"
                                },
                                {
                                    "id":"2l",
                                    "title" : "Volcán Pacaya",
                                    "description": "Febrero 09 (Atardecer)"
                                },
                                {
                                    "id":"3l",
                                    "title" : "Volcán Acatenango (Ruta Alotenango)",
                                    "description": "Febrero 08 - 09 (Asalto)"
                                },
                                {
                                    "id":"4l",
                                    "title" : "Volcán Santa María + Campana Abaj",
                                    "description": "Febrero 15 - 16 (Ruta Turistica - Asalto Nocturno)"
                                },
                                {
                                    "id":"5l",
                                    "title" : "Volcán Santa María + Campana Abaj",
                                    "description": "Febrero 15 - 16 (Ruta La Viergen - Asalto Nocturno)"
                                },
                                {
                                    "id":"6l",
                                    "title" : "Volcán Tajumulco",
                                    "description": "Febrero 09 (Asalto - Ruta San Sebastián con acercamiento 4x4)"
                                }
                            ]
                        },{
                            "title":"Retos",
                            "rows":[
                                {
                                    "id":"1r",
                                    "title" : "Reto Jaguar",
                                    "description": "37 Cumbres 2025 (Guatemala)."
                                },
                                {
                                    "id":"2r",
                                    "title" : "Reto Maya",
                                    "description": "Rutas Extremas (Guatemala)."
                                },
                                {
                                    "id":"3r",
                                    "title" : "Reto Tigre",
                                    "description": "15 Volcanes El Salvador 2025"
                                },
                                {
                                    "id":"4r",
                                    "title" : "Reto Chivo",
                                    "description": "37 Cumbres 2025 (Guatemala) - Salida desde Xela"
                                }
                            ]
                        },{
                            "title":"Trail Running",
                            "rows":[
                                {
                                    "id":"1tr",
                                    "title" : "X SkyRace",
                                    "description": "Evento de Trail running a desarrollarse en el parque entre cerros, Quetzaltenango (Xela), con distancias de 10K -14K -24K -42K en los volcanes Cerro Quemado, Santa María, Siete Orejas. \n\n Abril 13 (2025)"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    elif "0" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 *¡Hola!* Gracias por comunicarte con nosotros\n\n📌 *Selecciona una opción del menú para continuar:*\n\n1️⃣ Próximos Eventos ❔\n2️⃣ Salida desde la Capital 📍\n3️⃣ Salida desde Xela 📍\n4️⃣ Hablar con un operador 🙋‍♂️\n5️⃣ Información de Eventos y Retos 🌋\n 0️⃣ Regresar al Menú 🕜\n\n✨ *Escribe el número de la opción que deseas y te ayudaremos de inmediato.* \n\n\n 🌐 Visita nuestro sitio web:\n mountainconqueror.club"
            }
        }
    elif "boton" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive":{
                "type":"button",
                "body": {
                    "text": "¿Confirmas tu registro?"
                },
                "footer": {
                    "text": "Selecciona una de las opciones"
                },
                "action": {
                    "buttons":[
                        {
                            "type": "reply",
                            "reply":{
                                "id":"btnsi",
                                "title":"Si"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"btnno",
                                "title":"No"
                            }
                        },{
                            "type": "reply",
                            "reply":{
                                "id":"btntalvez",
                                "title":"Tal Vez"
                            }
                        }
                    ]
                }
            }
        }
    elif "btnsi" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Muchas Gracias por Aceptar."
            }
        }
    elif "btnno" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Es una Lastima."
            }
        }
    elif "btntalvez" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Estare a la espera."
            }
        }
        
    elif "1l" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/events/0.Volcanes_7_Orejas_Cerro_Quemado_Cerro_El_Granizo.pdf",
                "caption": (
                    "🌋🔥 *¡Aventura Triple: Siete Orejas, Cerro Quemado y Cerro El Granizo!* 🔥🌋\n\n"
                    "Prepárate para una jornada épica en tres de las maravillas naturales más fascinantes de Guatemala. "
                    "Esta travesía te llevará desde las alturas del *Volcán Siete Orejas*, pasando por las formaciones "
                    "místicas del *Cerro Quemado*, hasta la imponencia del *Cerro El Granizo*, todo en una experiencia "
                    "que pondrá a prueba tu resistencia y amor por la montaña. 🏔️✨\n\n"
                    "🔹 *Volcán Siete Orejas*: Con sus siete cumbres, este volcán ofrece paisajes únicos y una conexión profunda con la naturaleza. 🌄\n"
                    "🔹 *Cerro Quemado*: Terrenos volcánicos y vistas espectaculares en una formación cargada de historia y energía. 🔥\n"
                    "🔹 *Cerro El Granizo*: La combinación perfecta de desafío y recompensa con paisajes que te dejarán sin aliento. 🌳\n\n"
                    "✅ *¡No te pierdas esta increíble oportunidad!* Vive una experiencia inolvidable que combina aventura, naturaleza y el espíritu de superación. 💪🐾\n\n"
                    "#SieteOrejas #CerroQuemado #CerroElGranizo #MontañismoGuatemala #PasiónPorLasAlturas #ConquistaTriple #AventuraÉpica"
                )
            }
        }
    elif "2l" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/events/1.Volcan_Pacaya_Atardecer.pdf",
                "caption": (
                    "🌋🔥 *¡Cupo Lleno para el Volcán Pacaya!* 🔥🌋\n\n"
                    "¡Gracias a todos los aventureros por su entusiasmo! 🎉 Hemos llenado todos los cupos para esta increíble expedición "
                    "al *Volcán Pacaya*, uno de los destinos más espectaculares y dinámicos de Guatemala. 🏔️✨\n\n"
                    "Prepárense para vivir una experiencia inolvidable, caminando sobre paisajes únicos, admirando ríos de lava petrificada "
                    "y disfrutando de vistas panorámicas que quitan el aliento. 🌄🔥 Cada paso en esta aventura será un recuerdo imborrable.\n\n"
                    "❗ *Si no alcanzaste cupo esta vez, no te preocupes.* Muy pronto anunciaremos nuevas fechas y rutas para que puedas unirte "
                    "a nuestras próximas expediciones. 🚶‍♂️🐾\n\n"
                    "#VolcánPacaya #AventuraÉpica #PasiónPorLaMontaña #MontañismoGuatemala #EspírituDeAventura"
                )
            }
        }
    elif "3l" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/events/2.Acatenango_Ruta_Alotenango.pdf",
                "caption": (
                    "🌋🔥 *¡Desafío Extremo en el Volcán Acatenango por la Ruta Alotenango!* 🔥🌋\n\n"
                    "Este no es un ascenso cualquiera, es una *aventura extrema* reservada para los más valientes y experimentados. "
                    "La *Ruta Alotenango* es conocida por ser desafiante, intensa y llena de emociones que pondrán a prueba tu resistencia física y mental. 🏔️💪\n\n"
                    "Si buscas superar tus límites, atravesar terrenos empinados y disfrutar de vistas espectaculares mientras conquistas una de las "
                    "cumbres más imponentes de Guatemala, *esta es tu oportunidad*. 🌄✨\n\n"
                    "⚠️ *No apto para principiantes*: Este desafío requiere experiencia previa en montañismo, excelente condición física y determinación "
                    "para enfrentar uno de los ascensos más intensos de la región.\n\n"
                    "❓ *¿Estás listo para el reto?* ¡Únete y demuestra de qué estás hecho en esta aventura inolvidable! 🔥🐾\n\n"
                    "#AcatenangoExtremo #RutaAlotenango #AventuraÉpica #MontañismoGuatemala #DesafíoDeAltura #NoParaPrincipiantes #ConquistaLasCimas"
                )
            }
        }
    elif "4l" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/events/3.Volcan_Santa_Maria_Turistica.pdf",
                "caption": (
                    "🌋✨ *¡Aventura en el Volcán Santa María y Campana Abaj!* ✨🌋\n\n"
                    "Prepárate para explorar una de las rutas más espectaculares y accesibles de Guatemala: el *Volcán Santa María* "
                    "y la mágica experiencia en *Campana Abaj*. Este recorrido turístico combina paisajes impresionantes, historia cultural "
                    "y la belleza natural que solo este destino puede ofrecer. 🏔️🌿\n\n"
                    "🔹 *Volcán Santa María*: Con una de las vistas más impresionantes hacia el volcán activo *Santiaguito*, este coloso "
                    "es una parada obligatoria para los amantes de las alturas y la naturaleza. 🌄🔥\n"
                    "🔹 *Campana Abaj*: Un lugar lleno de misticismo y tradición que conecta a los visitantes con la cultura y el legado "
                    "ancestral de la región. Una experiencia inolvidable rodeada de paisajes únicos. ✨🌳\n\n"
                    "❓ *¿Listo para esta aventura turística?* Únete a este recorrido que combina naturaleza, cultura y la magia de nuestras "
                    "montañas. Una oportunidad para disfrutar del esplendor de Guatemala en su máximo esplendor. 💪🐾\n\n"
                    "#VolcánSantaMaría #CampanaAbaj #AventuraTurística #NaturalezaYTradición #MontañismoGuatemala #PasiónPorLaCultura"
                )
            }
        }
    elif "5l" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/events/4.Volcan_Santa_Maria_Ruta_La_Virgen.pdf",
                "caption": (
                    "🌋🔥 *¡Aventura Extrema: Ruta La Virgen al Volcán Santa María!* 🔥🌋\n\n"
                    "Para los más valientes y audaces, presentamos *Ruta La Virgen*, un recorrido desafiante, poco explorado "
                    "y diseñado exclusivamente para los más intrépidos. Esta nueva ruta hacia el imponente *Volcán Santa María* "
                    "promete poner a prueba tu resistencia y espíritu aventurero mientras descubres senderos ocultos y paisajes "
                    "que pocos han visto. 🏔️💪✨\n\n"
                    "Con *terrenos escarpados, inclinaciones pronunciadas y una conexión inigualable con la naturaleza*, *Ruta La Virgen* "
                    "es el desafío perfecto para quienes buscan algo más allá de lo ordinario. Cada paso será un logro, y la recompensa "
                    "final será una experiencia que marcará tu vida. 🌄🔥\n\n"
                    "⚠️ *No es para principiantes:* Este recorrido exige preparación física, determinación y el alma de un verdadero explorador.\n\n"
                    "❓ *¿Te atreves a ser parte de esta travesía épica?* La cima del *Santa María* te espera para escribir una nueva historia de "
                    "superación y aventura. 🐾🔥\n\n"
                    "#RutaLaVirgen #VolcánSantaMaría #AventuraExtrema #SoloParaIntrepidos #MontañismoGuatemala #ConquistaLasAlturas"
                )
            }
        }
    elif "6l" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/events/5.Volcan_Tajumulco_Ruta_San_Sebastian_Nocturno.pdf",
                "caption": (
                    "🌋🔥 *¡Conquista el techo de Centroamérica: Volcán Tajumulco!* 🔥🌋\n\n"
                    "Prepárate para una de las expediciones más emblemáticas de Guatemala: el ascenso al *Volcán Tajumulco*, "
                    "el punto más alto de toda Centroamérica con *4,220 metros sobre el nivel del mar*. 🏔️✨\n\n"
                    "Esta travesía te llevará a través de *impresionantes paisajes montañosos, bosques de altura y cielos despejados* "
                    "que regalan *amaneceres y atardeceres de ensueño*. Cada paso en esta aventura pondrá a prueba tu resistencia, "
                    "pero la recompensa en la cima será inigualable. 🌄💪\n\n"
                    "🌟 *Lo que te espera en el Tajumulco:*\n"
                    "🔹 *Ascenso desafiante* con vistas panorámicas inigualables.\n"
                    "🔹 *Amanecer desde la cima*, un espectáculo de colores y nubes danzando bajo tus pies.\n"
                    "🔹 *Conexión con la naturaleza* y el espíritu aventurero que llevas dentro.\n\n"
                    "✅ *No te pierdas esta oportunidad de conquistar el techo de Centroamérica* y ser parte de una experiencia inolvidable. "
                    "¿Estás listo para el reto? 🚀🔥\n\n"
                    "#VolcánTajumulco #TechoDeCentroamérica #AventuraÉpica #MontañismoGuatemala #SuperandoLímites #ConquistandoCimas"
                )
            }
        }
    elif "1r" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/rj.pdf",
                "caption": "Reto Jaguar"
            }
        }
    elif "2r" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                    "link": "https://mountainconqueror.club/assets/document/rm.pdf",
                    "caption": "Reto Maya"
                }
            }
    elif "3r" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/rt.pdf",
                "caption": "Reto Tigre"
            }
        }
    elif "4r" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/rc.pdf",
                "caption": "Reto Chivo"
            }
        }
    elif "1tr" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "¡Sumérgete en la emocionante experiencia de la X-SKYRACE! Este desafío te invita a conquistar elevaciones impresionantes y explorar la majestuosidad de terrenos montañosos a través de una competición de resistencia y determinación. Prepárate para elevar tu espíritu y desafiar los límites en los 3 volcanes de Xela, Cerró Quemado, Santa María, Siete Orejas \n\n\n 🌐 Visita nuestra pagina:\n https://www.instagram.com/x_skyrace/"
            }
        }
    else:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 *¡Hola!* Gracias por comunicarte con nosotros\n\n📌 *Selecciona una opción del menú para continuar:*\n\n1️⃣ Próximos Eventos ❔\n2️⃣ Salida desde la Capital 📍\n3️⃣ Salida desde Xela 📍\n4️⃣ Hablar con un operador 🙋‍♂️\n5️⃣ Información de Eventos y Retos 🌋\n 0️⃣ Regresar al Menú 🕜\n\n✨ *Escribe el número de la opción que deseas y te ayudaremos de inmediato.* \n\n\n 🌐 Visita nuestro sitio web:\n mountainconqueror.club"
            }
        }

    data=json.dumps(data)

    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAA3DvBSFw0oBOy6TUbXILZCO6YoSvCxn8LZCyKvAbLGP1XQpHUtImCuPKSlDipQUdCMsOlhiWIY3V37L8YfshOpbxN95kqDBFepgnygzG0Nqv0DwQWZByqxCg4IKbpO00bVHnoSnX4k0EoKIJMyHYXYwHaJhoNPqs2TGUi5N8pRCaq2zDBbYZC2ZBXsSymiIahRzGfPZCwA4ol2PqiCAbseld5NZA0l1XzQs08ZAKZAYD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST","/v21.0/557632224096092/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))
    finally:
        connection.close()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)