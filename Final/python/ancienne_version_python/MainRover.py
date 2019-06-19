import SuiviLigne
import Client
import threading

class MainRover:
    
    def __init__(self, suivi_ligne):
        self.suivi_ligne = suivi_ligne

    
    def sendInstruction(self, instruction):
        self.suivi_ligne.set_instruction(instruction)


    def getVoltage(self):
        return #appele fonction qui retourne la voltage des roues


suivi_ligne = SuiviLigne.SuiviLigne()
main_rover = MainRover(suivi_ligne)
client = Client.Client(main_rover)

threading.Thread(target=suivi_ligne.start_rover).start()

client.start_connection()