"""
Seed the database with the three required legal documents:
  - Términos y Condiciones (terms_and_conditions)
  - Política de Privacidad (privacy_policy)
  - Política de Tratamiento de Datos Personales (data_treatment_policy)

Run from the backend directory:
    python -m scripts.seed_legal
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.models.legal import LegalDocument

# ──────────────────────────────────────────────────────────────────────────────
# Document content
# ──────────────────────────────────────────────────────────────────────────────

TERMS_AND_CONDITIONS = """\
TÉRMINOS Y CONDICIONES DE USO DE WAYGO
Versión 1.0 — Vigente a partir del 1 de julio de 2026

Por favor, lea detenidamente estos Términos y Condiciones antes de utilizar la plataforma WAYGO. Al crear una cuenta o acceder a la aplicación, usted declara haber leído, comprendido y aceptado estos Términos en su totalidad.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. DEFINICIONES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1.1. "WAYGO" o "la Plataforma" hace referencia a la aplicación móvil WAYGO, su infraestructura tecnológica, sus servicios digitales y cualquier funcionalidad asociada.
1.2. "Propietario" hace referencia a la persona natural o jurídica titular de la Plataforma.
1.3. "Usuario" es toda persona natural que cree una cuenta en WAYGO o haga uso de sus servicios.
1.4. "Contenido" son todos los materiales que el Usuario publique, comparta o transmita a través de la Plataforma, incluyendo fotografías, comentarios, reseñas y demás.
1.5. "Visita Verificada" es el registro de presencia física de un Usuario en un lugar determinado, validada mediante geolocalización.
1.6. "Puntos" y "Logros" son reconocimientos virtuales que la Plataforma otorga a los Usuarios por sus interacciones; no tienen valor monetario ni pueden ser canjeados por dinero u otros bienes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. OBJETO Y DESCRIPCIÓN DEL SERVICIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WAYGO es una plataforma social de turismo geo-verificado que permite a sus Usuarios: (i) registrar visitas a lugares mediante verificación de proximidad GPS; (ii) publicar fotografías y comentarios de los lugares visitados; (iii) seguir a otros Usuarios e interactuar con su Contenido; (iv) acumular puntos, obtener logros y aparecer en clasificaciones; y (v) descubrir nuevos destinos y lugares de interés.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. REGISTRO DE CUENTA Y ACCESO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3.1. Para acceder a las funciones de WAYGO el Usuario debe crear una cuenta proporcionando un nombre de usuario único, una dirección de correo electrónico válida y una contraseña.
3.2. El Usuario garantiza que los datos de registro son verídicos, actualizados y precisos. Toda información falsa o engañosa constituye causal de suspensión inmediata de la cuenta.
3.3. El Usuario es el único responsable de mantener la confidencialidad de sus credenciales de acceso y de todas las actividades realizadas bajo su cuenta.
3.4. En caso de uso no autorizado de su cuenta, el Usuario deberá notificarlo de inmediato al Propietario a través de los canales de contacto establecidos en estos Términos.
3.5. El registro en WAYGO está destinado a personas mayores de 18 años. Los menores de edad solo podrán utilizar la Plataforma con la supervisión y autorización expresa de sus padres o representantes legales, quienes asumen plena responsabilidad.
3.6. El Propietario se reserva el derecho de rechazar solicitudes de registro o cancelar cuentas a su sola discreción.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. USO PERMITIDO DE LA PLATAFORMA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4.1. El Usuario se compromete a utilizar WAYGO únicamente con fines lícitos y de conformidad con estos Términos, la normativa colombiana aplicable y las buenas costumbres.
4.2. Queda expresamente prohibido:
  a) Publicar Contenido que sea ilegal, difamatorio, obsceno, violento, discriminatorio, pornográfico o que incite al odio.
  b) Usar la Plataforma para actividades comerciales no autorizadas o para spam.
  c) Publicar información falsa sobre lugares, engañar a otros Usuarios o manipular los sistemas de puntos.
  d) Realizar ingeniería inversa, descompilar o intentar acceder al código fuente de la aplicación.
  e) Acceder a cuentas de otros Usuarios sin autorización.
  f) Interferir con el funcionamiento normal de la Plataforma mediante ataques, scripts automatizados o cualquier otro medio.
  g) Publicar Contenido que viole derechos de propiedad intelectual de terceros.
  h) Suplantar la identidad de otras personas o entidades.
  i) Recopilar información de otros Usuarios sin su consentimiento.
  j) Simular visitas o falsificar datos de geolocalización.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. CONTENIDO GENERADO POR EL USUARIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5.1. El Usuario conserva la titularidad de los derechos de autor sobre el Contenido que publica en WAYGO.
5.2. Al publicar Contenido, el Usuario concede al Propietario una licencia no exclusiva, mundial, gratuita y sublicenciable para usar, reproducir, modificar, adaptar, distribuir y mostrar dicho Contenido dentro de la Plataforma y para los fines de operación y promoción del servicio.
5.3. El Usuario garantiza que el Contenido que publica: (i) es original o cuenta con las autorizaciones necesarias de sus titulares; (ii) no viola derechos de terceros; y (iii) cumple con estos Términos.
5.4. El Propietario podrá eliminar, sin previo aviso, cualquier Contenido que considere violatorio de estos Términos o que resulte inapropiado.
5.5. El Propietario no asume responsabilidad editorial por el Contenido publicado por los Usuarios y no garantiza su exactitud, integridad o veracidad.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. SISTEMA DE PUNTOS, LOGROS Y CLASIFICACIONES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6.1. WAYGO cuenta con un sistema de puntos, logros (badges) y clasificaciones que premia la participación activa de los Usuarios.
6.2. Los puntos, logros y posiciones en clasificaciones son elementos virtuales que no tienen valor económico, no son intercambiables por dinero, bienes o servicios, ni pueden ser transferidos entre Usuarios.
6.3. El Propietario se reserva el derecho de ajustar, modificar o eliminar el sistema de puntos, logros o clasificaciones en cualquier momento sin previo aviso y sin que ello genere derecho de compensación alguna a favor de los Usuarios.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. PROPIEDAD INTELECTUAL DE LA PLATAFORMA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7.1. Todos los derechos de propiedad intelectual sobre la Plataforma WAYGO —incluyendo, sin limitación, el software, diseño, marca, logotipos, textos, gráficos y funcionalidades— son propiedad exclusiva del Propietario o de sus licenciantes.
7.2. Estos Términos no otorgan al Usuario ningún derecho de propiedad intelectual sobre la Plataforma, más allá de la licencia limitada y revocable de uso personal y no comercial.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. SUSPENSIÓN Y TERMINACIÓN DE CUENTA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8.1. El Propietario podrá suspender o cancelar la cuenta de cualquier Usuario, de forma temporal o definitiva, ante el incumplimiento de estos Términos, sin perjuicio de las acciones legales que correspondan.
8.2. El Usuario podrá solicitar la eliminación de su cuenta en cualquier momento, conforme a lo establecido en la Política de Privacidad.
8.3. La terminación de la cuenta no extingue las obligaciones ya adquiridas ni las disposiciones de estos Términos que, por su naturaleza, deben sobrevivir a la terminación.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9. DISPONIBILIDAD DEL SERVICIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9.1. El Propietario procurará mantener la Plataforma disponible de manera continua; sin embargo, no garantiza su disponibilidad ininterrumpida.
9.2. El Propietario podrá suspender temporal o definitivamente la Plataforma por razones de mantenimiento, actualización, razones técnicas o de seguridad, o por decisión unilateral, sin que ello genere responsabilidad alguna frente al Usuario.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
10. EXCLUSIÓN DE GARANTÍAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

10.1. En la medida en que lo permita la legislación aplicable, la Plataforma se ofrece "tal como está" y "según disponibilidad", sin garantías expresas ni implícitas de ningún tipo.
10.2. El Propietario no garantiza que la Plataforma esté libre de errores, interrupciones, virus u otros componentes dañinos.
10.3. El Propietario no garantiza la exactitud o actualidad de los datos geográficos, descripciones de lugares u otro contenido disponible en la Plataforma.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
11. LIMITACIÓN DE RESPONSABILIDAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

11.1. En la medida máxima permitida por la ley, el Propietario no será responsable por daños indirectos, incidentales, especiales, punitivos o consecuentes que surjan del uso o la imposibilidad de uso de la Plataforma.
11.2. El Propietario no será responsable por: (i) daños derivados del Contenido publicado por otros Usuarios; (ii) pérdida de datos; (iii) daños causados por terceros; (iv) fallos en redes de comunicación ajenas al Propietario; (v) acceso no autorizado a los datos del Usuario por parte de terceros a pesar de las medidas de seguridad implementadas.
11.3. En ningún caso la responsabilidad total del Propietario frente al Usuario superará el monto pagado por el Usuario por el uso de la Plataforma en los últimos doce (12) meses, o COP $50.000 (cincuenta mil pesos colombianos) si el servicio fue gratuito.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
12. INDEMNIZACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El Usuario se compromete a indemnizar, defender y mantener indemne al Propietario, sus representantes, empleados y colaboradores, frente a cualquier reclamación, daño, pérdida o gasto (incluidos honorarios de abogados) derivados del incumplimiento de estos Términos, del Contenido que el Usuario publique, o de la violación de derechos de terceros.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
13. LEGISLACIÓN APLICABLE Y RESOLUCIÓN DE CONFLICTOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

13.1. Estos Términos se rigen por las leyes de la República de Colombia.
13.2. Cualquier controversia derivada de la interpretación o cumplimiento de estos Términos se resolverá, en primera instancia, mediante acuerdo directo entre las partes.
13.3. Si no se logra acuerdo directo en un plazo de treinta (30) días calendario, las partes se someterán a la jurisdicción de los jueces competentes de la ciudad de Bogotá D.C., Colombia, renunciando a cualquier otro fuero que pudiera corresponderles.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
14. MODIFICACIONES A LOS TÉRMINOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

14.1. El Propietario podrá modificar estos Términos en cualquier momento. Los cambios se notificarán a través de la Plataforma o por correo electrónico al Usuario.
14.2. Si el Usuario continúa usando WAYGO después de la entrada en vigor de los nuevos Términos, se entenderá que los acepta. Si no está de acuerdo, deberá dejar de usar la Plataforma y solicitar la eliminación de su cuenta.
14.3. Cuando se publique una nueva versión de los Términos, la Plataforma requerirá la aceptación expresa del Usuario antes de permitirle continuar con su uso.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
15. CONTACTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para consultas sobre estos Términos, puede comunicarse con el Propietario a través de:
Correo electrónico: legal@waygo.app

Última actualización: 1 de julio de 2026
"""

PRIVACY_POLICY = """\
POLÍTICA DE PRIVACIDAD DE WAYGO
Versión 1.0 — Vigente a partir del 1 de julio de 2026

En WAYGO nos comprometemos con la protección de sus datos personales. Esta Política explica qué información recopilamos, cómo la utilizamos, con quién la compartimos y cuáles son sus derechos.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. RESPONSABLE DEL TRATAMIENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El responsable del tratamiento de sus datos personales es el Propietario de la Plataforma WAYGO.
Contacto de privacidad: privacidad@waygo.app

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. DATOS QUE RECOPILAMOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2.1. Datos que usted nos proporciona directamente:
  • Nombre de usuario (apodo o alias elegido por el Usuario).
  • Dirección de correo electrónico.
  • Contraseña (almacenada únicamente en forma de hash criptográfico; nunca en texto plano).
  • Foto de perfil (avatar), si la proporciona voluntariamente.
  • Descripción biográfica (bio), país y ciudad, si los proporciona voluntariamente.

2.2. Datos generados por el uso de la Plataforma:
  • Visitas verificadas: fecha, hora y lugar del registro de visita.
  • Datos de geolocalización: coordenadas GPS capturadas únicamente en el momento en que el Usuario activa una verificación de visita. No realizamos rastreo continuo de ubicación en segundo plano.
  • Fotografías y videos publicados en la Plataforma.
  • Comentarios, reacciones (likes) y colecciones guardadas.
  • Relaciones de seguimiento (seguidores y seguidos).
  • Puntos acumulados, logros obtenidos y posición en clasificaciones.
  • Registro de aceptación de documentos legales (fecha, versión, IP, plataforma).

2.3. Datos técnicos recopilados automáticamente:
  • Dirección IP en el momento de registro de consentimiento y durante el uso de la API.
  • Plataforma del dispositivo (Android/iOS) y versión de la aplicación.
  • Registros de errores y diagnósticos (logs del servidor).

2.4. Datos que NO recopilamos:
  • Datos de salud o médicos.
  • Información financiera o de tarjetas de crédito.
  • Número de identificación nacional o documento de identidad.
  • Datos biométricos distintos a la fotografía de perfil.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. CÓMO RECOPILAMOS LOS DATOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Directamente del Usuario durante el registro y uso de la aplicación.
  • A través de los permisos del dispositivo concedidos por el Usuario (ubicación, cámara, galería).
  • Automáticamente a través de los registros del servidor de API.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. PERMISOS DEL DISPOSITIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WAYGO solicita los siguientes permisos al dispositivo del Usuario:

  • Ubicación precisa (GPS): para verificar la presencia física en un lugar. Solo se activa cuando el Usuario inicia una verificación de visita; no se accede en segundo plano.
  • Cámara: para tomar fotografías de los lugares visitados y publicarlas en la Plataforma.
  • Galería / almacenamiento: para seleccionar fotografías existentes en el dispositivo y publicarlas en la Plataforma.
  • Acceso a Internet: para la comunicación con los servidores de WAYGO.

El Usuario puede revocar estos permisos en cualquier momento desde la configuración de su dispositivo, aunque ello podrá limitar el funcionamiento de ciertas funciones de la aplicación.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. FINALIDADES DEL TRATAMIENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Los datos personales son tratados para las siguientes finalidades:

  a) Crear y gestionar la cuenta del Usuario.
  b) Prestar los servicios de la Plataforma (verificación de visitas, publicación de contenido, sistema de puntos, clasificaciones).
  c) Enviar notificaciones relacionadas con el servicio (nuevos seguidores, likes, comentarios).
  d) Enviar correos electrónicos para verificación de cuenta, recuperación de contraseña y comunicaciones operativas esenciales.
  e) Garantizar la seguridad de la Plataforma, prevenir fraudes y detectar usos indebidos.
  f) Mejorar y desarrollar los servicios de WAYGO.
  g) Cumplir con obligaciones legales y regulatorias.
  h) Registrar y acreditar el consentimiento otorgado por el Usuario a los documentos legales.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. BASE LEGAL DEL TRATAMIENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El tratamiento de datos personales se sustenta en las siguientes bases legales:

  • Consentimiento del titular: para el tratamiento general de datos y el registro de consentimiento a documentos legales.
  • Ejecución de un contrato: para proveer los servicios de la Plataforma (Términos y Condiciones aceptados).
  • Interés legítimo: para garantizar la seguridad de la Plataforma, prevenir fraudes y mejorar el servicio.
  • Obligación legal: para cumplir con requerimientos de autoridades competentes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. SERVICIOS EXTERNOS (TERCEROS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WAYGO utiliza los siguientes servicios de terceros que pueden tener acceso a datos del Usuario:

  • Almacenamiento en la nube (Amazon S3, Cloudflare R2 u otro proveedor S3-compatible): para almacenar fotografías e imágenes subidas a la Plataforma. Los archivos se almacenan en servidores seguros; solo el Propietario tiene acceso administrativo.
  • Servicio de correo electrónico (SMTP): para el envío de correos de verificación y recuperación de contraseña. El proveedor de SMTP puede procesar la dirección de correo electrónico del Usuario.
  • Sentry (monitoreo de errores): si está habilitado, se envía información de diagnóstico (trazas de error, versión de la app, plataforma) para detectar y corregir fallos. La configuración de Sentry en WAYGO excluye el envío de información de identificación personal (send_default_pii=False).
  • Base de datos MongoDB: los datos del Usuario se almacenan en bases de datos MongoDB. El acceso está restringido mediante credenciales seguras.
  • Redis: se utiliza para caché y control de límites de peticiones. No almacena datos personales de forma persistente.

No vendemos, alquilamos ni cedemos sus datos personales a terceros con fines comerciales o publicitarios.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. TRANSFERENCIAS INTERNACIONALES DE DATOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Los proveedores de almacenamiento en la nube y el servicio de correo electrónico pueden operar en jurisdicciones distintas a Colombia. En tales casos, nos aseguramos de que existan garantías contractuales adecuadas (como cláusulas contractuales tipo) para proteger sus datos conforme a los estándares de la Ley 1581 de 2012 y las buenas prácticas internacionales.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9. CONSERVACIÓN DE LOS DATOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Datos de cuenta: se conservan mientras la cuenta esté activa. Al eliminar la cuenta, los datos personales del perfil se eliminan en un plazo máximo de 30 días, salvo que exista obligación legal de conservarlos por un período mayor.
  • Fotografías y contenido: al eliminar la cuenta, el contenido publicado se elimina de los servidores en un plazo máximo de 30 días.
  • Registros de consentimiento: se conservan durante el tiempo que sea necesario para demostrar el cumplimiento legal, con un mínimo de 5 años.
  • Logs del servidor: se conservan por un período máximo de 90 días, con fines de seguridad y diagnóstico.
  • Tokens de sesión (refresh tokens): se eliminan automáticamente al vencer o al cerrar sesión.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
10. SEGURIDAD DE LA INFORMACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Implementamos medidas técnicas y organizativas razonables para proteger sus datos personales, que incluyen:

  • Cifrado de contraseñas mediante algoritmos de hash criptográfico seguros (bcrypt/argon2).
  • Transmisión de datos cifrada mediante HTTPS/TLS.
  • Autenticación basada en tokens JWT con vigencia limitada.
  • Almacenamiento seguro de tokens de sesión mediante Flutter Secure Storage (cifrado del dispositivo).
  • Control de acceso por roles (usuarios regulares vs. administradores).
  • Límites de velocidad (rate limiting) para prevenir ataques de fuerza bruta.
  • Cabeceras de seguridad HTTP (Content-Security-Policy, X-Frame-Options, etc.).

Sin embargo, ningún sistema de seguridad es absolutamente infalible. En caso de una brecha de seguridad que afecte sus datos, le notificaremos conforme a la normativa aplicable.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
11. DERECHOS DEL USUARIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usted tiene los siguientes derechos sobre sus datos personales:

  • Acceso: conocer qué datos personales suyos tratamos.
  • Rectificación: corregir datos inexactos o desactualizados.
  • Supresión (eliminación): solicitar la eliminación de sus datos personales cuando ya no sean necesarios para las finalidades para las que fueron recopilados, salvo obligación legal de conservarlos.
  • Portabilidad: recibir sus datos en un formato estructurado y legible por máquina, cuando sea técnicamente posible.
  • Revocación del consentimiento: retirar su consentimiento para el tratamiento de datos en cualquier momento, sin que ello afecte la licitud del tratamiento previo.
  • Oposición: oponerse al tratamiento de sus datos cuando exista una razón legítima.
  • Limitación: solicitar la restricción del tratamiento de sus datos en ciertos casos.

Para ejercer cualquiera de estos derechos, escríbanos a: privacidad@waygo.app

Responderemos su solicitud en un plazo máximo de 15 días hábiles contados desde la recepción de la solicitud completa.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
12. MENORES DE EDAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WAYGO no está destinado a personas menores de 18 años. No recopilamos intencionalmente datos personales de menores de edad. Si tenemos conocimiento de que hemos recopilado datos de un menor sin el consentimiento de sus representantes legales, tomaremos medidas para eliminar dicha información a la brevedad.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
13. NOTIFICACIONES PUSH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Las notificaciones se gestionan internamente a través del sistema de notificaciones de la Plataforma (in-app). En versiones futuras, si se implementan notificaciones push mediante FCM u otro servicio, se actualizará esta Política y se solicitará el consentimiento correspondiente.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
14. APLICABILIDAD DE REGULACIONES INTERNACIONALES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

14.1. GDPR (Reglamento General de Protección de Datos de la Unión Europea): Si usted reside en el Espacio Económico Europeo, puede ejercer sus derechos GDPR (acceso, rectificación, supresión, portabilidad, oposición, limitación) contactándonos a privacidad@waygo.app. También tiene derecho a presentar una reclamación ante la autoridad de protección de datos de su país.
14.2. CCPA (Ley de Privacidad del Consumidor de California): Si usted reside en California, EE.UU., no vendemos sus datos personales. Puede ejercer sus derechos bajo el CCPA contactándonos a privacidad@waygo.app.
14.3. Ley 1581 de 2012 (Colombia): Esta Política cumple con los principios y obligaciones de la normativa colombiana de protección de datos. Ver también nuestra Política de Tratamiento de Datos Personales.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
15. CAMBIOS A ESTA POLÍTICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Podremos actualizar esta Política en cualquier momento. La versión vigente estará siempre disponible en la Plataforma. Cuando los cambios sean materiales, le notificaremos y le solicitaremos su aceptación expresa antes de continuar usando WAYGO.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
16. CONTACTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para consultas, solicitudes o reclamaciones relacionadas con esta Política de Privacidad:
Correo electrónico: privacidad@waygo.app

Última actualización: 1 de julio de 2026
"""

DATA_TREATMENT_POLICY = """\
POLÍTICA DE TRATAMIENTO DE DATOS PERSONALES DE WAYGO
Versión 1.0 — Vigente a partir del 1 de julio de 2026

Elaborada en cumplimiento de la Ley 1581 de 2012, el Decreto 1377 de 2013, el Decreto 1074 de 2015 y las normas que los complementen, modifiquen o sustituyan.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. IDENTIFICACIÓN DEL RESPONSABLE DEL TRATAMIENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Responsable: WAYGO (Propietario de la Plataforma)
Correo de contacto: privacidad@waygo.app
Actividad: Plataforma digital de turismo social geo-verificado.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. MARCO LEGAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Esta Política se rige por:
  • Ley 1581 de 2012 — Régimen general de protección de datos personales.
  • Decreto 1377 de 2013 — Reglamentación parcial de la Ley 1581 de 2012.
  • Decreto 1074 de 2015 (Decreto Único Reglamentario del Sector Comercio).
  • Circular Externa 002 de 2015 de la Superintendencia de Industria y Comercio (SIC).
  • Demás normas que complementen, modifiquen o sustituyan las anteriores.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. DEFINICIONES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Dato personal: cualquier información vinculada o que pueda asociarse a una o varias personas naturales determinadas o determinables.
  • Titular: la persona natural cuyos datos personales son objeto de tratamiento.
  • Responsable del tratamiento: persona que decide sobre la base de datos y/o el tratamiento de los datos.
  • Encargado del tratamiento: quien realiza el tratamiento de datos por cuenta del responsable.
  • Tratamiento: toda operación sobre datos personales (recolección, almacenamiento, uso, circulación, supresión, etc.).
  • Consentimiento: manifestación libre, previa, expresa e informada del Titular para el tratamiento de sus datos.
  • Base de datos: conjunto organizado de datos personales objeto de tratamiento.
  • Dato sensible: datos que afectan la intimidad del Titular o cuyo uso puede generar discriminación (salud, orientación sexual, origen étnico, etc.). WAYGO no trata datos sensibles.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. PRINCIPIOS QUE RIGEN EL TRATAMIENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El tratamiento de datos personales en WAYGO se rige por los principios establecidos en la Ley 1581 de 2012:

  • Legalidad: el tratamiento es una actividad reglada que se sujeta a la normativa vigente.
  • Finalidad: el tratamiento obedece a finalidades determinadas, explícitas y legítimas.
  • Libertad: el tratamiento solo puede realizarse con el consentimiento previo, expreso e informado del Titular.
  • Veracidad/Calidad: la información tratada debe ser veraz, completa, exacta y actualizada.
  • Transparencia: el Titular puede conocer en todo momento la existencia de los datos y las finalidades del tratamiento.
  • Acceso y circulación restringida: los datos no se divulgarán a terceros salvo autorización del Titular o mandato legal.
  • Seguridad: se adoptan las medidas técnicas necesarias para proteger los datos.
  • Confidencialidad: las personas que intervengan en el tratamiento están obligadas a guardar reserva de la información.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. DATOS PERSONALES RECOPILADOS Y FINALIDADES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5.1. Datos de registro:
  • Nombre de usuario: identificación del Titular en la Plataforma.
  • Correo electrónico: verificación de cuenta, recuperación de contraseña y comunicaciones operativas.
  • Contraseña (hash): autenticación segura.
  • Foto de perfil, bio, país, ciudad (opcionales): personalización del perfil público.

5.2. Datos de geolocalización:
  • Coordenadas GPS capturadas puntualmente durante la verificación de visita a un lugar. No se realiza rastreo continuo ni en segundo plano.

5.3. Contenido generado:
  • Fotografías, comentarios y colecciones: prestación del servicio social de la Plataforma.

5.4. Datos técnicos:
  • Dirección IP: seguridad, prevención de fraudes y registro de consentimientos.
  • Plataforma y versión de app: diagnóstico técnico y mejora del servicio.

5.5. Registro de consentimientos:
  • Versión del documento aceptado, fecha y hora, IP, plataforma: acreditación del cumplimiento legal.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. AUTORIZACIÓN DEL TITULAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6.1. El tratamiento de datos personales en WAYGO requiere la autorización previa, expresa e informada del Titular, conforme al artículo 9 de la Ley 1581 de 2012.
6.2. La autorización se obtiene a través del flujo de aceptación de la presente Política dentro de la aplicación, antes de que el Usuario pueda acceder a las funciones de la Plataforma.
6.3. La autorización es registrada electrónicamente con fecha, hora, IP, plataforma y versión del documento, garantizando su trazabilidad y acreditación.
6.4. El Titular puede revocar la autorización en cualquier momento, lo que implicará la eliminación de su cuenta y datos personales, salvo los que deban conservarse por obligación legal.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. DERECHOS DEL TITULAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

De conformidad con el artículo 8 de la Ley 1581 de 2012, el Titular tiene derecho a:

  a) Conocer, actualizar y rectificar sus datos personales.
  b) Solicitar prueba de la autorización otorgada al Responsable.
  c) Ser informado sobre el uso que se ha dado a sus datos personales.
  d) Presentar quejas ante la Superintendencia de Industria y Comercio (SIC) por infracciones a la normativa de protección de datos.
  e) Revocar la autorización y/o solicitar la supresión de sus datos cuando el tratamiento no respete los principios de la Ley 1581 de 2012.
  f) Acceder gratuitamente a sus datos personales que hayan sido objeto de tratamiento.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. PROCEDIMIENTO PARA EJERCER DERECHOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8.1. Canal de contacto: privacidad@waygo.app

8.2. Consultas (artículo 14, Ley 1581 de 2012):
  El Titular puede consultar su información personal enviando un correo a la dirección indicada. La respuesta se remitirá en un plazo máximo de diez (10) días hábiles. Si la consulta no puede atenderse en ese plazo, se informará al Titular antes del vencimiento, expresando los motivos y señalando la fecha en que se atenderá (máximo cinco (5) días hábiles adicionales).

8.3. Reclamos (artículo 15, Ley 1581 de 2012):
  Si el Titular considera que sus datos deben ser corregidos, actualizados, suprimidos o si detecta un presunto incumplimiento de la normativa, puede presentar un reclamo ante el Responsable. El reclamo debe incluir: identificación del Titular, descripción de los hechos, documentos de soporte (si los hay) y la pretensión concreta. El Responsable tiene un plazo de quince (15) días hábiles para atender el reclamo. Si no puede resolverse en ese plazo, se informará al Titular antes del vencimiento con los motivos y la nueva fecha de resolución (máximo ocho (8) días hábiles adicionales). Si el Responsable no atiende el reclamo, el Titular puede acudir a la SIC.

8.4. Autoridad de control: Superintendencia de Industria y Comercio (SIC) — www.sic.gov.co

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9. TRANSFERENCIA Y TRANSMISIÓN DE DATOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9.1. Los datos personales no serán vendidos, cedidos ni compartidos con terceros para fines comerciales o publicitarios.
9.2. Los proveedores de servicios técnicos (almacenamiento en nube, correo electrónico) actúan como Encargados del Tratamiento y están sujetos a acuerdos contractuales que garantizan el tratamiento adecuado de los datos.
9.3. La transmisión de datos a Encargados ubicados fuera de Colombia se realiza únicamente cuando el país receptor ofrece niveles adecuados de protección o cuando se han adoptado las garantías contractuales exigidas por la normativa colombiana.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
10. CONSERVACIÓN Y SUPRESIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Los datos personales se conservarán mientras sea necesario para cumplir las finalidades del tratamiento o mientras exista una obligación legal de conservarlos. Al solicitar la supresión o al cancelar la cuenta, los datos personales del perfil se eliminarán en un plazo máximo de 30 días. Los registros de consentimiento se conservarán por un mínimo de 5 años para fines probatorios.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
11. MEDIDAS DE SEGURIDAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El Responsable ha implementado medidas técnicas, humanas y administrativas para proteger los datos personales, incluyendo cifrado de contraseñas, transmisión mediante HTTPS, autenticación segura con JWT, almacenamiento seguro en el dispositivo mediante cifrado, control de acceso por roles y protección contra ataques de fuerza bruta.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
12. VIGENCIA Y MODIFICACIONES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Esta Política rige a partir del 1 de julio de 2026. El Responsable podrá modificarla en cualquier momento; los cambios materiales serán comunicados al Titular y requerirán su aceptación expresa antes de continuar usando la Plataforma. La versión vigente estará siempre disponible en la aplicación.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
13. CONTACTO Y CANAL OFICIAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para consultas, reclamos o el ejercicio de sus derechos:
Correo electrónico: privacidad@waygo.app

Autoridad de Control: Superintendencia de Industria y Comercio (SIC)
Sitio web: www.sic.gov.co
Línea de atención: 601 5870000

Última actualización: 1 de julio de 2026
"""

# ──────────────────────────────────────────────────────────────────────────────
# Seed function
# ──────────────────────────────────────────────────────────────────────────────

DOCUMENTS = [
    {
        "doc_type": "terms_and_conditions",
        "version": "1.0",
        "title": "Términos y Condiciones de Uso",
        "content": TERMS_AND_CONDITIONS,
    },
    {
        "doc_type": "privacy_policy",
        "version": "1.0",
        "title": "Política de Privacidad",
        "content": PRIVACY_POLICY,
    },
    {
        "doc_type": "data_treatment_policy",
        "version": "1.0",
        "title": "Política de Tratamiento de Datos Personales",
        "content": DATA_TREATMENT_POLICY,
    },
]


async def seed() -> None:
    await connect_to_mongo()

    for meta in DOCUMENTS:
        existing = await LegalDocument.find_one(
            LegalDocument.doc_type == meta["doc_type"],
            LegalDocument.is_active == True,
        )
        if existing:
            print(f"[SKIP] {meta['doc_type']} already active (v{existing.version})")
            continue

        doc = LegalDocument(**meta)
        await doc.insert()
        print(f"[OK]   Created {meta['doc_type']} v{meta['version']}")

    await close_mongo_connection()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(seed())
