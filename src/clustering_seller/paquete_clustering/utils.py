
import requests


class UtilsClustering:
    """
    Esta clase provee de funciones utilies para el proceso de extracción y clusterización  
    """
    def __init__(self, configraciones):
        """Constructor de la clase.

        Args:
            configraciones:  Diccionario que contiene configuraciones.
        """
        self.configraciones = configraciones 
        
    def generar_token(self) :
        """
        Generación de token en la aplicación de MELI
        """

        data = {
            'grant_type': self.configraciones["grant_type"],
            'client_id':  self.configraciones["client_id"],
            'client_secret': self.configraciones["client_secret"],
            'code': self.configraciones["code"],
            'redirect_uri':self.configraciones["redirect_uri"]
        }

        headers = {'accept': 'application/json','content-type': 'application/x-www-form-urlencoded'}
        try:
            response = requests.post('https://api.mercadolibre.com/oauth/token',
                                    data=data, 
                                    headers=headers)
            if response.status_code == 200:
                print("Solicitud post exitosa")
                print("Respuesta:")
                print(response.text)
            else:
                print(f"Error en la solicitud POST. Código de estado: {response.status_code}")
                print("Mensaje de error:")

        except Exception as e:
            print(f"Error: {e}")

            
    def actualizar_token(self, token_anterior) :
        """
        Actualización de token en la aplicación de MELI

        Args:
                token_anterior:  Token vencido

        Returns:
            Retona el token actual
            """
        url = 'https://api.mercadolibre.com/oauth/token'
        data = {
            'grant_type': self.configraciones['grant_type_update'],
            'client_id': self.configraciones['client_id'] ,
            'client_secret':self.configraciones['client_secret'],
            'refresh_token' : token_anterior
        }
        

        headers = {'accept': 'application/json','content-type': 'application/x-www-form-urlencoded'}
        try:
            response = requests.post(url,
                                    data=data, 
                                    headers=headers)
            if response.status_code == 200:
                print("Solicitud post exitosa")
                print("Respuesta:")
                print(response.text)
                return response.text
            else:
                print(f"Error en la solicitud POST. Código de estado: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")
        


