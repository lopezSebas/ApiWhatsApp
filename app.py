from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bandera = False

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
                "body": "🙋‍♂️ Hola soy asistente de Sebas, lamento que no hayas encontrado la información que buscabas y solicitas apoyo para resolver tus dudas. \n\n📌 *Puedes escribir al número personal y con gusto te atenderá.* \n\n +502 34267938"
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
                                    "id":"b",
                                    "title" : "Febrero 09",
                                    "description": "(Atardecer) Volcán Pacaya"
                                },
                                {
                                    "id":"c",
                                    "title" : "Febrero 08 - 09",
                                    "description": "(Ruta Alotenango - Asalto) Volcán Acatenango"
                                },
                                {
                                    "id":"d",
                                    "title" : "Febrero 15 - 16",
                                    "description": "(Ruta Turistica - Asalto Nocturno) Volcán Santa María + Campana Abaj"
                                },
                                {
                                    "id":"e",
                                    "title" : "Febrero 15 - 16",
                                    "description": "(Ruta La Viergen - Asalto Nocturno) Volcán Santa María + Campana Abaj"
                                },
                                {
                                    "id":"f",
                                    "title" : "Febrero 21 - 23",
                                    "description": "Volcán Tajumulco (Asalto - Ruta San Sebastián con acercamiento de 4x4)"
                                },
                                {
                                    "id":"g",
                                    "title" : "Febrero 22 - 23",
                                    "description": "Semuc Champey (Express)"
                                },
                                {
                                    "id":"h",
                                    "title" : "Abril 17 - 20",
                                    "description": "Trekking Ixil"
                                },
                                {
                                    "id":"i",
                                    "title" : "Abril 14 - 20",
                                    "description": "Expedición La Danta (Semana Santa - Todo Incluido)"
                                }
                            ]
                        },{
                            "title":"Retos",
                            "rows":[
                                {
                                    "id":"w",
                                    "title" : "Reto Chivo",
                                    "description": "37 Cumbres 2025 (Guatemala) - Salida desde Xela"
                                }
                            ]
                        },{
                            "title":"Trail Running",
                            "rows":[
                                {
                                    "id":"t",
                                    "title" : "Abril 13 2025(X SkyRace)",
                                    "description": "Evento de Trail running (X SkyRace) con distancias de 10K 14K 24K 42K"
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
                "body": "🚀 *¡Hola!* Gracias por comunicarte con nosotros\n\n📌 *Selecciona una opción del menú para continuar:*\n\n1️⃣ Próximos Eventos ❔\n2️⃣ Salida desde la Capital 📍\n3️⃣ Salida desde Xela 📍\n4️⃣ Hablar con un operador 🙋‍♂️\n5️⃣ Información de Eventos y Retos 🌋\n0️⃣ Regresar al Menú 🕜\n\n✨ *Escribe el número de la opción que deseas y te ayudaremos de inmediato.* \n\n\n 🌐 Visita nuestro sitio web:\n mountainconqueror.club"
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
                "body": "!Bienvenid@ a la aventura!. \n\n "
                "**INSCRIPCIÓN** \n"
                "Banco Promerica — \n"
                "Titular: SEBASTIAN LORENZO LOPEZ\n"
                "Tipo: Ahorro — Número: 32992082536883\n"

                "Banco Industrial —\n"
                "Titular: SEBASTIAN LORENZO LOPEZ\n"
                "Tipo: Ahorro — Número: 3698864\n"

                "Proceso 𝐝𝐞 𝐩𝐚𝐠𝐨:\n"
                "1.- Realizar depósito o reserva.\n"
                "2.- Tomar Foto o escanear boleta de pago.\n"
                "3.- LLenar el formulario de participación:\n"
                "https://forms.gle/gdUL8iduCiK8VUYF9 \n"
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
                "body": "Es una Lastima, igual te dejaré nuestros próximos tours! https://mountainconqueror.club/tours ."
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
                "body": "Estare a al pendiente, si tienes dudas especificas que no encuentras en el documento, puedes escribir al +502 34267938."
            }
        }
        

    elif "b" == texto.strip():
        bandera = True
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/events/1.Volcan_Pacaya_Atardecer.pdf",
                "caption": (
                    "🌋🔥 *¡Vive la Experiencia del Volcán Pacaya!* 🔥🌋\n\n"
                    "🚀 Únete a una **aventura inolvidable** explorando uno de los volcanes más impresionantes de Guatemala. "
                    "Disfruta de paisajes espectaculares, senderos rodeados de lava petrificada y una vista increíble de la actividad volcánica. 🌄🔥\n\n"
                    "📌 **Incluye:**\n"
                    "✔️ Transporte ida y vuelta 🚌\n"
                    "✔️ Guías expertos 🏞️\n"
                    "✔️ Experiencia única con vistas panorámicas 🌅\n"
                    "✔️ Oportunidad de asar malvaviscos en la lava caliente 🔥\n\n"
                    "🎟️ *Reserva tu cupo ahora y prepárate para una experiencia épica.*\n"
                    "📅 Fecha: Febrero 09\n"
                    "💰 Costo: Q160\n\n"
                    "📲 *¡Escríbenos para más información y asegura tu lugar!* 🏔️✨\n\n"
                    "#VolcánPacaya #AventuraÉpica #MontañismoGuatemala #PasiónPorLaNaturaleza #ViajaConNosotros"
                )
            }
        }
    elif "c" == texto.strip():
        bandera = True
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
    elif "d" == texto.strip():
        bandera = True
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
    elif "e" == texto.strip():
        bandera = True
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
    elif "f" == texto.strip():
        bandera = True
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
    elif "g" == texto.strip():
        bandera = True
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "caption": (
                    "🌊✨ *¡Descubre el mágico Semuc Champey!* ✨🌊\n\n"
                    "🌿 Sumérgete en un paraíso natural con **piscinas de agua turquesa**, impresionantes vistas y cuevas llenas de aventura. "
                    "Vive una experiencia inolvidable en uno de los destinos más fascinantes de Guatemala. 🌄💙\n\n"
                    
                    "📅 **Fecha:** Febrero 22 - 23\n"
                    "🕒 **Hora de salida Capital:** 9:00 PM ⏳\n"
                    "💰 **Costo Capital:** Q295 💵\n\n"
                    "🕒 **Hora de salida Xela:** 5:30 PM ⏳\n"
                    "💰 **Costo Xela:** Q695 💵\n\n"

                    "📌 **Incluye:** ✅\n"
                    "✔️ Transporte ida y vuelta 🚐\n"
                    "✔️ Tour guiado por las pozas naturales 💦\n"

                    "🚫 **No incluye:** ❌\n"
                    "❌ Alimentación 🍽️\n"
                    "❌ Bebidas 🥤\n"
                    "❌ Gastos personales 🛍️\n\n"
                    "❌ Traslado de 4x4 Q20 por persona (debes cancelar en efectivo el día del viaje, directamente con nuestro staff).\n\n"
                    "❌ Visita a las **Cuevas de Kan’Ba** (opcional) 🔦 \n\n"
                    "❌ Tubing en el río Cahabón 🛶 (opcional) \n\n"
                    "❌ Ingreso al parque natural Semuc Champey. (Q30 nacional y 50 Extranjeros) 🛍️\n\n"

                    "🎟️ *Reserva tu cupo ahora y prepárate para una experiencia épica.*\n"
                    "📲 *¡Escríbenos para más información y asegura tu lugar!* 🌎🔥\n\n"
                    "#SemucChampey #AventuraÉpica #GuatemalaMágica #ViajesIncreíbles #TurismoSostenible"
                )
            }
        }
    elif "i" == texto.strip():
        bandera = True
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "caption": (
                    "⛰️🏕️ *¡Trekking Ixil – Conéctate con la Naturaleza y la Cultura!* 🏕️⛰️\n\n"
                    "🚀 Explora los majestuosos paisajes de la región Ixil, un territorio lleno de historia, cultura y senderos escondidos "
                    "entre montañas, ríos y valles ancestrales. Vive una **aventura única** en este destino poco explorado. 🌄🔥\n\n"

                    "📅 **Fecha:** 17 - 20 Abril\n"
                    "🕒 **Hora de salida:** 9:00 PM ⏳\n"
                    "💰 **Costo:** Q 875 💵\n\n"

                    "📌 **Incluye:** ✅\n"
                    "✔️ Transporte ida y vuelta 🚐\n"
                    "✔️ Guías locales y narración cultural 🏞️\n"
                    "✔️ Acceso a senderos exclusivos 🌿\n"
                    "✔️ Experiencia en comunidades locales 🏡\n"
                    "✔️ Seguro básico de trekking 🏕️\n\n"

                    "🚫 **No incluye:** ❌\n"
                    "❌ Alimentación en el recorrido 🍽️\n"
                    "❌ Hidratación personal 🥤\n"
                    "❌ Gastos adicionales personales 🏪\n\n"

                    "🎟️ *Camina por los senderos de la historia y la naturaleza.*\n"
                    "📲 *¡Reserva tu cupo y únete a esta experiencia única en el corazón de Guatemala!* 🌎🔥\n\n"
                    "#TrekkingIxil #AventuraEnGuatemala #SenderosSagrados #Montañismo #ExplorandoGuatemala"
                )
            }
        }
    elif "h" == texto.strip():
        bandera = True
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": "https://mountainconqueror.club/assets/document/events/La_Danta_Semana_Santa.pdf",
                "caption": (
                    "🏕️🌿 *¡Expedición La Danta – El Corazón de la Selva Maya!* 🌿🏕️\n\n"
                    "🚀 Atrévete a una **aventura extrema** explorando el misterioso **Mirador y la Pirámide de La Danta**, "
                    "una de las más grandes del mundo. Adéntrate en la densa selva petenera y camina entre historia, naturaleza y desafíos únicos. 🌎🔥\n\n"

                    "📅 **Fecha:** 14 - 20 Abril\n"
                    "🕒 **Hora de salida:** 5:00 AM ⏳\n"
                    "💰 **Costo:** Q 3,650 💵\n\n"
                    "💰 **Si reservas antes del 15 de Marzo :** Q 3,450 💵\n\n"

                    "📌 **Incluye:** ✅\n"
                    "✔️ Transporte terrestre ida y vuelta 🚐\n"
                    "✔️ Guías especializados en la selva 🌿\n"
                    "✔️ Permiso de acceso a la reserva arqueológica 🏛️\n"
                    "✔️ Alimentación en el campamento 🥘\n"
                    "✔️ Equipo básico de expedición 🎒\n\n"

                    "🚫 **No incluye:** ❌\n"
                    "❌ Equipo personal de camping ⛺\n"
                    "❌ Snacks y bebidas adicionales 🥤\n"
                    "❌ Seguro de viaje 🏥\n\n"

                    "🎟️ *Una expedición solo para verdaderos aventureros.*\n"
                    "📲 *¡Reserva tu cupo y prepárate para explorar la historia en su máxima expresión!* 🏕️🔥\n\n"
                    "#ExpediciónLaDanta #AventuraMaya #SelvaPetenera #MontañismoGuatemala #HistoriaYNaturaleza"
                )
            }
        }
    elif "z" == texto.strip():
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
    elif "y" == texto.strip():
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
    elif "x" == texto.strip():
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
    elif "w" == texto.strip():
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
    elif "t" == texto.strip():
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
                "body": "🚀 *¡Hola!* Gracias por comunicarte con nosotros\n\n📌 *Selecciona una opción del menú para continuar:*\n\n1️⃣ Próximos Eventos ❔\n2️⃣ Salida desde la Capital 📍\n3️⃣ Salida desde Xela 📍\n4️⃣ Hablar con un operador 🙋‍♂️\n5️⃣ Información de Eventos y Retos 🌋\n0️⃣ Regresar al Menú 🕜\n\n✨ *Escribe el número de la opción que deseas y te ayudaremos de inmediato.* \n\n\n 🌐 Visita nuestro sitio web:\n mountainconqueror.club"
            }
        }

    data=json.dumps(data)
    
    data_boton = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "\n\n ¿Confirmas tu registro?"
            },
            "footer": {
                "text": "Selecciona una de las opciones"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btnsi",
                            "title": "Sí"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "btnno",
                            "title": "No"
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
    
    data_boton=json.dumps(data_boton)

    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAA3DvBSFw0oBOy6TUbXILZCO6YoSvCxn8LZCyKvAbLGP1XQpHUtImCuPKSlDipQUdCMsOlhiWIY3V37L8YfshOpbxN95kqDBFepgnygzG0Nqv0DwQWZByqxCg4IKbpO00bVHnoSnX4k0EoKIJMyHYXYwHaJhoNPqs2TGUi5N8pRCaq2zDBbYZC2ZBXsSymiIahRzGfPZCwA4ol2PqiCAbseld5NZA0l1XzQs08ZAKZAYD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST","/v21.0/526518787218130/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
        
        
        if(bandera):
            time.sleep(10)
            bandera = False
        
            connection.request("POST","/v21.0/526518787218130/messages", data_boton, headers)
            response = connection.getresponse()
            print(response.status, response.reason)
        
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))
    finally:
        connection.close()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)